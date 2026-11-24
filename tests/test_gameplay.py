import math
import os
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import pygame
from game.world import (
    World, ZOMBIE_OUTBREAK_COUNTRIES_BY_CONTINENT, geo_to_map,
)
from game.save_system import SaveSystem
from game.ideology import (
    IDEOLOGY_TREES, develop as develop_ideology, ideology_bonuses,
)
from game.events import EventSystem
from game.country import Country
from game.technology import TECH_TREE, research
from game.decision_events import DECISION_EVENTS
from ui.game_screen import GameScreen
from ui.main_menu import MainMenu
from ui.localization import get_language, set_language, translate


class GameplayTests(unittest.TestCase):
    def setUp(self):
        self.world = World()

    def test_language_setting_defaults_to_english_and_persists(self):
        original_language = get_language()
        try:
            with tempfile.TemporaryDirectory() as settings_dir:
                menu = MainMenu.__new__(MainMenu)
                menu.settings_path = os.path.join(settings_dir, "settings.json")
                menu.settings = menu._load_settings()
                menu.screen = SimpleNamespace(get_size=lambda: (1280, 720))
                menu.mode = "settings"
                menu.background = object()
                set_language(menu.settings["language"])

                self.assertEqual(menu.settings["language"], "en")
                self.assertEqual(translate("НАСТРОЙКИ"), "SETTINGS")
                self.assertEqual(translate("Идеологии"), "Ideologies")
                self.assertEqual(
                    translate("Мирное предложение активно"),
                    "Peace offer is active",
                )

                language_rect = menu._settings_rects(1280, 720)[1]
                menu.handle_settings_event(SimpleNamespace(
                    type=pygame.MOUSEBUTTONDOWN,
                    button=1,
                    pos=language_rect.center,
                ))
                self.assertEqual(menu.settings["language"], "ru")
                self.assertEqual(get_language(), "ru")
                self.assertIsNone(menu.background)

                reloaded = MainMenu.__new__(MainMenu)
                reloaded.settings_path = menu.settings_path
                self.assertEqual(reloaded._load_settings()["language"], "ru")

                menu.handle_settings_event(SimpleNamespace(
                    type=pygame.MOUSEBUTTONDOWN,
                    button=1,
                    pos=language_rect.center,
                ))
                self.assertEqual(menu.settings["language"], "en")
                self.assertEqual(translate("НАСТРОЙКИ"), "SETTINGS")
        finally:
            set_language(original_language)

    def test_scenarios_use_distinct_dates_and_territory_owners(self):
        self.world.new_game("ussr", "ww2")
        self.assertEqual(self.world.year, 1936)
        self.assertEqual(self.world.get_region(geo_to_map((30, 50))).owner, "ussr")
        self.assertEqual(self.world.get_region(geo_to_map((78, 22))).owner, "uk")
        self.assertEqual(self.world.countries["ussr"].ideology, "communism")
        self.assertEqual(self.world.countries["germany"].ideology, "fascism")

        self.world.new_game("usa", "modern")
        self.assertEqual(self.world.year, 2026)
        self.assertEqual(self.world.get_region(geo_to_map((30, 50))).owner, "ukr")

    def test_world_war_two_country_names_and_labels_use_homelands(self):
        self.world.new_game("portugal", "ww2")

        self.assertEqual(self.world.countries["portugal"].name, "Португалия")
        self.assertEqual(
            self.world.get_region(geo_to_map((32.6, -25.9))).owner,
            "portugal",
        )
        label = self.world.map_labels["portugal"]["point"]
        homeland = geo_to_map((-9.1, 38.7))
        self.assertLess(math.dist(label, homeland), 40)

    def test_selectable_regions_follow_real_administrative_boundaries(self):
        self.world.new_game("germany")
        berlin = self.world.get_province(geo_to_map((13.4, 52.5)))
        hesse = self.world.get_province(geo_to_map((10.0, 51.0)))

        self.assertIsNotNone(berlin)
        self.assertIsNotNone(hesse)
        self.assertEqual((berlin.name, berlin.owner), ("Berlin", "germany"))
        self.assertEqual((hesse.name, hesse.owner), ("Hesse", "germany"))
        self.assertNotEqual(berlin.id, hesse.id)

    def test_economy_ideology_and_research_have_costs_and_effects(self):
        self.world.new_game("germany")
        country = self.world.countries["germany"]
        report_before = country.economy_report(country.region_count(self.world))
        money_before = country.money
        industry_before = country.industry
        initial_cost = country.investment_cost("industry")

        self.assertTrue(country.invest("industry")[0])
        self.assertEqual(country.money, money_before - initial_cost)
        self.assertEqual(country.industry, industry_before + 8)
        self.assertGreater(country.investment_cost("industry"), initial_cost)
        self.assertFalse(self.world.research_technology("germany", "industry")[0])

        country.research_points = 100
        self.assertTrue(self.world.research_technology("germany", "administration")[0])
        self.assertTrue(self.world.research_technology("germany", "logistics")[0])
        self.assertIn("logistics", country.techs)
        self.assertGreater(country.economy_report()["output"], report_before["output"])

        old_ideology = country.ideology
        self.assertTrue(self.world.change_ideology("germany", "monarchy")[0])
        self.assertNotEqual(country.ideology, old_ideology)

    def test_ideology_branches_cost_political_power_and_survive_saves(self):
        self.world.new_game("germany")
        country = self.world.countries["germany"]
        country.money = 5000
        country.political_power = 200
        country.government_support = 80
        target_ideology = "communism" if country.ideology != "communism" else "democracy"

        self.assertTrue(
            self.world.change_ideology("germany", target_ideology)[0]
        )
        country.political_power = 200
        before_power = country.political_power
        before_industry = country.industry
        self.assertFalse(
            self.world.develop_ideology(
                "germany", "communism_planned_industry"
            )[0]
        )
        first_upgrade = (
            "communism_collectivization"
            if target_ideology == "communism"
            else "democracy_civil_rights"
        )
        self.assertTrue(
            self.world.develop_ideology("germany", first_upgrade)[0]
        )
        self.assertLess(country.political_power, before_power)
        if target_ideology == "communism":
            self.assertTrue(
                self.world.develop_ideology(
                    "germany", "communism_planned_industry"
                )[0]
            )
            self.assertEqual(country.industry, before_industry + 8)

        with tempfile.TemporaryDirectory() as save_dir:
            saves = SaveSystem(save_dir)
            self.assertTrue(saves.save(self.world, 1)[0])
            loaded = World()
            self.assertTrue(saves.load(loaded, 1)[0])
        restored = loaded.countries["germany"]
        self.assertEqual(restored.ideology, target_ideology)
        self.assertEqual(restored.ideology_upgrades, country.ideology_upgrades)
        self.assertEqual(restored.political_power, country.political_power)

    def test_taxes_and_war_exhaustion_reduce_stability_and_research(self):
        class NoRandomEvents:
            @staticmethod
            def random():
                return 1.0

        self.world.new_game("germany")
        country = self.world.countries["germany"]
        initial = country.economy_report()
        self.assertLess(initial["research"], 0.4)
        initial_political_power = country.political_power
        self.assertGreater(initial["political_power"], 0)

        country.set_tax_rate(18)
        initial_support = country.government_support
        country.advance_day(NoRandomEvents(), country.region_count(self.world), 0)
        self.assertGreater(country.political_power, initial_political_power)
        self.assertLess(country.government_support, initial_support)
        self.assertGreater(country.unrest, 0)

        country.wars.add("poland")
        country.war_exhaustion = 90
        stability_before = country.stability
        exhaustion_report = country.economy_report(
            country.region_count(self.world), 1
        )
        self.assertLess(exhaustion_report["output"], initial["output"])
        self.assertLess(exhaustion_report["research"], initial["research"])
        country.advance_day(NoRandomEvents(), country.region_count(self.world), 1)
        self.assertLess(country.stability, stability_before)

    def test_war_exhaustion_has_a_moderate_economic_penalty(self):
        self.world.new_game("germany")
        country = self.world.countries["germany"]
        country.unrest = 0
        country.food = 100
        country.energy = 100
        rested = country.economy_report()

        country.war_exhaustion = 100
        exhausted = country.economy_report()

        self.assertAlmostEqual(exhausted["output"], rested["output"] * 0.975)
        self.assertAlmostEqual(exhausted["research"], rested["research"] * 0.85)

    def test_zombie_scenario_reduces_the_economic_penalty_from_unrest(self):
        self.world.new_game("usa", "zombie")
        country = self.world.countries["usa"]
        country.food = 100
        country.energy = 100
        country.war_exhaustion = 0
        region_count = self.world.province_count(country.id)
        active_wars = len(self.world.wars_for(country.id))

        country.unrest = 100
        standard = country.economy_report(region_count, active_wars)
        zombie_rules = country.economy_report(
            region_count, active_wars, zombie_scenario=True
        )

        self.assertGreater(zombie_rules["output"], standard["output"])
        self.assertGreater(zombie_rules["taxes"], standard["taxes"])
        self.assertGreater(zombie_rules["research"], standard["research"])

    def test_battles_accumulate_war_exhaustion_more_slowly(self):
        class FixedRolls:
            @staticmethod
            def uniform(low, high):
                return low

        self.world.new_game("germany")
        self.world.declare_war("germany", "poland")
        attacker = self.world.countries["germany"]
        defender = self.world.countries["poland"]
        war = self.world.war_between(attacker.id, defender.id)
        self.world.rng = FixedRolls()

        self.world._apply_conflict_losses(war, attacker, defender, True)

        attacker_fatigue = 1 + ideology_bonuses(
            attacker.ideology, attacker.ideology_upgrades
        ).get("war_exhaustion", 0)
        defender_fatigue = 1 + ideology_bonuses(
            defender.ideology, defender.ideology_upgrades
        ).get("war_exhaustion", 0)
        self.assertAlmostEqual(attacker.war_exhaustion, 4 * attacker_fatigue)
        self.assertAlmostEqual(defender.war_exhaustion, 8 * defender_fatigue)

    def test_high_unrest_can_start_a_rebellion(self):
        class CertainRevolt:
            @staticmethod
            def random():
                return 0.0

            @staticmethod
            def choice(values):
                return values[0]

        self.world.new_game("germany")
        country = self.world.countries["germany"]
        country.stability = 20
        country.government_support = 10
        country.unrest = 100
        initial_regions = self.world.province_count("germany")
        self.world.rng = CertainRevolt()

        self.world._process_rebellions()
        country.wars.clear()
        self.world._process_rebellions()

        rebels = next(
            item for item in self.world.countries.values()
            if item.id.startswith("rebels_germany_")
        )
        self.assertEqual(
            sum(item.id.startswith("rebels_germany_") for item in self.world.countries.values()),
            1,
        )
        self.assertGreater(country.rebellion_cooldown_until, self.world.absolute_day())
        self.assertEqual(self.world.province_count("germany"), initial_regions - 1)
        self.assertEqual(self.world.province_count(rebels.id), 1)
        self.assertTrue(self.world.war_between("germany", rebels.id))
        with tempfile.TemporaryDirectory() as save_dir:
            saves = SaveSystem(save_dir)
            saves.save(self.world, 1)
            loaded = World()
            self.assertTrue(saves.load(loaded, 1)[0])
        self.assertIn(rebels.id, loaded.countries)
        self.assertTrue(loaded.war_between("germany", rebels.id))
        self.assertEqual(
            loaded.countries["germany"].rebellion_cooldown_until,
            country.rebellion_cooldown_until,
        )
        rebel_capital = next(
            province for province in loaded.provinces
            if province.owner == rebels.id
        )
        self.assertEqual(
            loaded.capital_provinces[rebels.id],
            rebel_capital.id,
        )

    def test_paid_unrest_relief_has_an_escalating_cost_and_is_saved(self):
        self.world.new_game("usa")
        country = self.world.countries["usa"]
        country.money = 10_000
        country.unrest = 8

        self.assertEqual(self.world.unrest_relief_cost(country.id), 250)
        self.assertTrue(self.world.reduce_unrest(country.id)[0])
        self.assertEqual(country.unrest, 6)
        self.assertEqual(country.money, 9750)
        self.assertEqual(self.world.unrest_relief_cost(country.id), 500)
        self.assertTrue(self.world.reduce_unrest(country.id)[0])
        self.assertEqual(country.unrest, 4)
        self.assertEqual(self.world.unrest_relief_cost(country.id), 750)

        with tempfile.TemporaryDirectory() as save_dir:
            saves = SaveSystem(save_dir)
            self.assertTrue(saves.save(self.world, 1)[0])
            loaded = World()
            self.assertTrue(saves.load(loaded, 1)[0])
        self.assertEqual(loaded.countries["usa"].unrest_relief_count, 2)

    def test_rebellions_can_start_at_lower_unrest_and_use_stronger_armies(self):
        class CertainRevolt:
            @staticmethod
            def random():
                return 0.0

            @staticmethod
            def choice(values):
                return values[0]

        self.world.new_game("germany")
        country = self.world.countries["germany"]
        country.unrest = 75
        country.stability = 40
        country.government_support = 30
        country.army_size = 100_000
        self.world.rng = CertainRevolt()

        self.world._process_rebellions()
        rebels = next(
            item for item in self.world.countries.values()
            if item.id.startswith("rebels_germany_")
        )

        self.assertGreaterEqual(rebels.army_size, 120_000)
        self.assertGreater(rebels.army_readiness, 80)
        self.assertEqual(
            country.rebellion_cooldown_until,
            self.world.absolute_day() + 240,
        )

    def test_ai_recovers_its_army_and_industry_after_a_war(self):
        self.world.new_game("usa")
        self.assertTrue(self.world.declare_war("usa", "canada")[0])
        self.assertTrue(self.world.settle_war("usa", "canada", "status_quo")[0])
        canada = self.world.countries["canada"]
        canada.recovery_ready_day = self.world.absolute_day()
        canada.money = 5000
        canada.army_size = 1000
        initial_army = canada.army_size

        self.assertTrue(self.world.ai._recover_country("canada"))
        self.assertGreater(canada.army_size, initial_army)
        self.assertGreater(canada.recovery_ready_day, self.world.absolute_day())

        canada.recovery_ready_day = self.world.absolute_day()
        canada.army_size = max(
            1000,
            int(canada.population * (0.0015 + canada.military / 100000)),
        )
        canada.industry = 50
        initial_industry = canada.industry
        self.assertTrue(self.world.ai._recover_country("canada"))
        self.assertGreater(canada.industry, initial_industry)

    def test_random_events_have_varied_real_effects_and_report_consequences(self):
        events = EventSystem(self.world)
        self.assertGreaterEqual(len(events.events), 30)
        supported_effects = set(events.EVENT_EFFECTS) | {"relations"}
        self.assertTrue(all(
            set(event.get("effects", {})) <= supported_effects
            for event in events.events
        ))

        self.world.new_game("usa")
        country = self.world.countries["usa"]
        country.money = 5000
        country.industry = 50
        income_before = country.economy_report(
            country.region_count(self.world), len(self.world.wars_for(country.id))
        )["net"]
        crisis = next(event for event in events.events if event["id"] == "crisis")

        consequences = events.apply_event(country, crisis)

        self.assertEqual(country.money, 4650)
        self.assertEqual(country.industry, 48)
        income_after = country.economy_report(
            country.region_count(self.world), len(self.world.wars_for(country.id))
        )["net"]
        self.assertLess(income_after, income_before)
        self.assertIn("Казна −350", consequences)
        self.assertIn("Доход/день", consequences)
        self.world.add_event(
            "Экономический кризис", notify=True, modal=True,
            consequences=consequences,
        )
        self.assertEqual(
            self.world.pending_modal_events[0]["consequences"], consequences
        )
        self.assertEqual(self.world.events[0]["consequences"], consequences)

    def test_ai_countries_diplomatically_engage_and_choose_conquest_targets(self):
        self.world.new_game("usa")
        germany = self.world.countries["germany"]
        poland = self.world.countries["poland"]
        germany.relations[poland.id] = 60
        poland.relations[germany.id] = 60

        self.assertTrue(
            self.world.ai._conduct_diplomacy(
                germany.id, [germany.id, poland.id]
            )
        )
        self.assertEqual(germany.alliance, poland.id)
        self.assertEqual(poland.alliance, germany.id)

        self.world.diplomacy.break_alliance(germany.id, poland.id)
        germany.strategy = "expansion"
        germany.money = 10_000
        germany.stability = 90
        germany.war_support = 90
        germany.military = 100
        poland.military = 0
        for neighbor_id in self.world.country_neighbors[germany.id]:
            germany.relations[neighbor_id] = 0
        germany.relations[poland.id] = -100

        self.assertEqual(
            self.world.ai._choose_war_target(germany.id, self.world.countries),
            poland.id,
        )
        self.assertTrue(self.world.declare_war(germany.id, poland.id)[0])
        self.assertTrue(self.world.war_between(germany.id, poland.id))

    def test_expansion_ai_starts_wars_against_other_ai(self):
        class AggressiveRandom:
            @staticmethod
            def random():
                return 0.0001

            @staticmethod
            def shuffle(values):
                return None

            @staticmethod
            def choice(values):
                return values[0]

            @staticmethod
            def uniform(low, high):
                return high

        self.world.new_game("usa")
        for country_id, country in self.world.countries.items():
            if country_id == self.world.player_id:
                continue
            country.strategy = "expansion"
            country.money = 10_000
            country.stability = 90
            country.war_support = 90
            country.military = 100
            for other_id in self.world.countries:
                if other_id != country_id:
                    country.relations[other_id] = -100
        self.world.rng = AggressiveRandom()

        self.world.ai.update()

        ai_wars = [
            war for war in self.world.active_wars()
            if self.world.player_id not in war.attackers + war.defenders
        ]
        self.assertTrue(ai_wars)

    def test_ai_attacks_prioritize_the_capital_and_the_route_toward_it(self):
        self.world.new_game("germany")
        self.assertTrue(self.world.declare_war("germany", "poland")[0])
        war = self.world.war_between("germany", "poland")
        capital_id = self.world.capital_provinces["poland"]
        capital = self.world.provinces_by_id[capital_id]
        self.assertEqual(capital.owner, "poland")

        target = self.world._prioritize_front_target(
            [capital], "province", war, war.defenders
        )
        self.assertEqual(target.id, capital_id)

        fronts, kind = self.world._front_regions(war.attackers, war.defenders)
        self.assertEqual(kind, "province")
        target = self.world._prioritize_front_target(
            fronts, kind, war, war.defenders
        )
        distances = {capital_id: 0}
        queue = [capital_id]
        for province_id in queue:
            for neighbor_id in self.world.province_neighbors[province_id]:
                neighbor = self.world.provinces_by_id[neighbor_id]
                if neighbor.owner == "poland" and neighbor_id not in distances:
                    distances[neighbor_id] = distances[province_id] + 1
                    queue.append(neighbor_id)
        reachable_distances = [
            distances[province.id] for province in fronts
            if province.id in distances
        ]
        self.assertTrue(reachable_distances)
        self.assertEqual(
            distances[target.id],
            min(reachable_distances),
        )

    def test_capturing_the_capital_causes_major_war_pressure(self):
        self.world.new_game("germany")
        self.assertTrue(self.world.declare_war("germany", "poland")[0])
        war = self.world.war_between("germany", "poland")
        capital = self.world.provinces_by_id[
            self.world.capital_provinces["poland"]
        ]
        neighbor = next(
            self.world.provinces_by_id[neighbor_id]
            for neighbor_id in self.world.province_neighbors[capital.id]
            if self.world.provinces_by_id[neighbor_id].owner == "poland"
        )
        self.world._set_region_owner(
            neighbor, "germany", "province", occupied=False
        )
        poland = self.world.countries["poland"]
        initial_stability = poland.stability
        initial_exhaustion = poland.war_exhaustion

        class CertainVictory:
            @staticmethod
            def choice(values):
                return values[0]

            @staticmethod
            def uniform(low, high):
                return high

        self.world.rng = CertainVictory()
        self.assertTrue(
            self.world.resolve_conflict(
                "germany", "poland", capital.id
            )[0]
        )

        self.assertEqual(capital.owner, "germany")
        self.assertGreaterEqual(war.attacker_score, 32)
        self.assertLess(poland.stability, initial_stability)
        self.assertGreater(poland.war_exhaustion, initial_exhaustion)

    def test_military_research_requires_branches_and_increases_strength(self):
        self.world.new_game("germany")
        country = self.world.countries["germany"]
        country.research_points = 1000
        country.money = 10_000
        initial_strength = country.military_strength(self.world)

        self.assertFalse(self.world.research_technology("germany", "modern_arms")[0])
        for technology_id in (
            "administration",
            "logistics",
            "industry",
            "military_doctrine",
            "tactics",
            "military_logistics",
            "modern_arms",
        ):
            self.assertTrue(self.world.research_technology("germany", technology_id)[0])

        self.assertGreater(country.military_strength(self.world), initial_strength)

    def test_war_operations_capture_regions_and_respect_cooldown(self):
        self.world.new_game("usa")
        attacker = self.world.countries["usa"]
        defender = self.world.countries["canada"]
        attacker.military = 100
        attacker.war_support = 100
        attacker.money = 20_000
        defender.military = 0
        defender.stability = 0
        initial_provinces = self.world.province_count("canada")

        self.assertTrue(self.world.declare_war("usa", "canada")[0])
        self.assertTrue(self.world.resolve_conflict("usa", "canada")[0])
        self.assertLess(
            self.world.province_count("canada"),
            initial_provinces,
        )
        self.assertFalse(self.world.resolve_conflict("usa", "canada")[0])
        self.assertTrue(self.world.diplomacy.propose_peace("usa", "canada")[0])

    def test_war_requires_land_access_and_peace_restores_prewar_borders(self):
        self.world.new_game("usa")
        attacker = self.world.countries["usa"]
        attacker.money = 20_000
        self.assertNotIn("uk", self.world.country_neighbors["usa"])
        self.assertTrue(self.world.declare_war("usa", "uk")[0])
        money_before = attacker.money
        success, message = self.world.resolve_conflict("usa", "uk")
        self.assertFalse(success)
        self.assertIn("доступа", message)
        self.assertEqual(attacker.money, money_before)

        self.world.new_game("usa")
        attacker = self.world.countries["usa"]
        defender = self.world.countries["canada"]
        attacker.military = 100
        attacker.army_size = max(attacker.army_size, 1_000_000)
        attacker.army_readiness = 100
        attacker.war_support = 100
        attacker.money = 20_000
        defender.military = 0
        defender.army_size = 1000
        defender.army_readiness = 10
        defender.stability = 0
        defender.war_support = 0
        self.world.rng.seed(5)
        self.assertTrue(self.world.declare_war("usa", "canada")[0])
        war = self.world.war_between("usa", "canada")
        fronts, kind = self.world._front_regions(war.attackers, war.defenders)
        self.assertEqual(kind, "province")
        self.assertTrue(fronts)
        original_owner = fronts[0].owner
        while self.world.pending_modal_events:
            self.world.acknowledge_modal_event()

        self.assertTrue(self.world.resolve_conflict("usa", "canada")[0])
        self.assertFalse(self.world.pending_modal_events)
        captured = next(region for region in fronts if region.owner == "usa")
        self.assertEqual(captured.owner, "usa")
        self.assertTrue(captured.occupied)
        self.assertGreater(war.casualties.get("usa", 0), 0)
        self.assertTrue(self.world.settle_war("usa", "canada", "status_quo")[0])
        self.assertEqual(captured.owner, original_owner)
        self.assertFalse(captured.occupied)
        self.assertEqual(war.status, "ended")
        self.assertFalse(attacker.wars)

    def test_allies_join_war_and_reparations_are_paid(self):
        self.world.new_game("usa")
        attacker = self.world.countries["usa"]
        defender = self.world.countries["canada"]
        attacker.alliance = "mexico"
        self.world.countries["mexico"].alliance = "usa"
        defender.alliance = "uk"
        self.world.countries["uk"].alliance = "canada"
        attacker.relations["mexico"] = 60
        self.world.countries["mexico"].relations["usa"] = 60
        defender.relations["uk"] = 60
        self.world.countries["uk"].relations["canada"] = 60
        attacker.money = 1000
        defender.money = 1000
        attacker.military = 100
        defender.military = 0

        self.assertTrue(self.world.declare_war("usa", "canada")[0])
        war = self.world.war_between("usa", "canada")
        self.assertEqual(set(war.attackers), {"usa", "mexico"})
        self.assertEqual(set(war.defenders), {"canada", "uk"})
        self.assertIn("canada", self.world.countries["mexico"].wars)
        defender_money = defender.money
        self.assertTrue(self.world.settle_war("usa", "canada", "reparations")[0])
        self.assertLess(defender.money, defender_money)
        self.assertEqual(war.status, "ended")
        self.assertTrue(all(not self.world.countries[item].wars for item in war.attackers + war.defenders))

    def test_player_can_break_and_reform_an_alliance(self):
        self.world.new_game("usa")
        player = self.world.countries["usa"]
        partner = self.world.countries["mexico"]
        player.relations[partner.id] = 60
        partner.relations[player.id] = 60

        self.assertTrue(self.world.diplomacy.form_alliance(player.id, partner.id)[0])
        self.assertTrue(self.world.diplomacy.break_alliance(player.id, partner.id)[0])
        self.assertIsNone(player.alliance)
        self.assertIsNone(partner.alliance)
        self.assertTrue(self.world.diplomacy.form_alliance(player.id, partner.id)[0])

    def test_player_gets_a_pausing_notification_when_attacked(self):
        self.world.new_game("usa")

        self.assertTrue(self.world.declare_war("canada", "usa")[0])
        self.assertTrue(self.world.time.paused)
        self.assertEqual(len(self.world.pending_modal_events), 1)
        notification = self.world.notifications[0]["text"]
        self.assertIn("объявляет войну вашему государству", notification)
        self.assertIn(self.world.countries["canada"].name, notification)

    def test_ai_vs_ai_operations_do_not_notify_a_nonparticipant_player(self):
        self.world.new_game("usa")
        self.assertTrue(self.world.declare_war("germany", "poland")[0])
        self.world.notifications.clear()

        self.assertTrue(self.world.resolve_conflict("germany", "poland")[0])

        self.assertFalse(any(
            "Победа в операции" in notification["text"]
            or "Операция не удалась" in notification["text"]
            for notification in self.world.notifications
        ))

    def test_ai_does_not_form_an_alliance_with_player_without_consent(self):
        self.world.new_game("usa")
        player = self.world.countries["usa"]
        mexico = self.world.countries["mexico"]
        player.relations[mexico.id] = 60
        mexico.relations[player.id] = 60

        self.world.ai._conduct_diplomacy("mexico", ["mexico", "usa"])

        self.assertIsNone(player.alliance)
        self.assertIsNone(mexico.alliance)
        self.assertIsNone(self.world.alliance_partner(player.id))

    def test_unilateral_saved_alliance_is_not_treated_as_active(self):
        self.world.new_game("usa")
        data = self.world.to_dict()
        data["countries"]["usa"]["alliance"] = "mexico"
        data["countries"]["mexico"]["alliance"] = None
        loaded = World()
        loaded.from_dict(data)

        self.assertIsNone(loaded.alliance_partner("usa"))
        self.assertIsNone(loaded.countries["usa"].alliance)

    def test_czechia_can_capture_isolated_vienna_as_last_region(self):
        class WinningRandom:
            def __init__(self):
                self.draw = 0

            def uniform(self, low, high):
                self.draw += 1
                return high if self.draw % 2 else low

            @staticmethod
            def choice(values):
                return values[0]

        self.world.new_game("austria", "ww2")
        austria = self.world.countries["austria"]
        czechia = self.world.countries["czechoslovakia"]
        vienna = next(
            province for province in self.world.provinces
            if province.owner == austria.id and province.name == "Vienna"
        )
        self.assertTrue(self.world.province_neighbors[vienna.id])
        self.assertTrue(any(
            set(pair) == {vienna.id, neighbor_id}
            and segments
            for pair, segments in self.world.province_border_segments.items()
            for neighbor_id in self.world.province_neighbors[vienna.id]
        ))
        self.assertTrue(self.world.declare_war(czechia.id, austria.id)[0])
        for province in list(self.world.provinces):
            if province.owner == austria.id and province.id != vienna.id:
                self.world._set_region_owner(
                    province, czechia.id, "province",
                    occupied=True, update_neighbors=False,
                )

        czechia.military = 100
        czechia.army_size = max(czechia.army_size, 10_000_000)
        austria.military = 0
        austria.army_size = 1000
        self.world.rng = WinningRandom()
        czechia.battle_cooldowns[austria.id] = 0

        self.assertTrue(self.world.can_attack(czechia.id, austria.id))
        self.assertTrue(
            self.world.resolve_conflict(czechia.id, austria.id)[0]
        )
        self.assertEqual(self.world.province_count(austria.id), 0)
        self.assertTrue(austria.is_defeated)

    def test_conflict_operation_targets_the_selected_country_in_a_coalition(self):
        class WinningRandom:
            def __init__(self):
                self.draw = 0

            def uniform(self, low, high):
                self.draw += 1
                return high if self.draw % 2 else low

            @staticmethod
            def choice(values):
                return values[0]

        self.world.new_game("usa")
        war = self.world._add_war(
            ["usa"], ["canada", "mexico"],
            {"type": "conquest", "target": "mexico"},
        )
        usa = self.world.countries["usa"]
        usa.military = 100
        usa.army_size = max(usa.army_size, 10_000_000)
        for country_id in ("canada", "mexico"):
            country = self.world.countries[country_id]
            country.military = 0
            country.army_size = 1000
        initial_canada = self.world.province_count("canada")
        initial_mexico = self.world.province_count("mexico")
        self.world.rng = WinningRandom()

        self.assertTrue(self.world.resolve_conflict("usa", "canada")[0])
        self.assertEqual(self.world.province_count("canada"), initial_canada - 1)
        self.assertEqual(self.world.province_count("mexico"), initial_mexico)
        self.assertEqual(war.objective["target"], "mexico")

    def test_coalition_member_cannot_attack_from_an_allied_country_front(self):
        self.world.new_game("usa")
        war = self.world._add_war(
            ["usa", "france"], ["canada", "mexico"],
            {"type": "conquest", "target": "canada"},
        )
        self.world.countries["france"].money = 5000

        self.assertTrue(self.world.can_attack("usa", "canada"))
        self.assertFalse(self.world.can_attack("france", "canada"))
        success, message = self.world.resolve_conflict("france", "canada")
        self.assertFalse(success)
        self.assertIn("доступа", message)
        self.assertEqual(war.battles, 0)

    def test_expanded_trees_have_tradeoffs_that_affect_the_country(self):
        self.assertEqual({key: len(nodes) for key, nodes in IDEOLOGY_TREES.items()},
                         {key: 28 for key in IDEOLOGY_TREES})
        self.assertEqual(len(TECH_TREE), 59)
        technologies = {node["id"]: node for node in TECH_TREE}
        self.assertEqual(
            set(technologies["future_energy"]["requires"]),
            {"green_autonomy", "civil_industry"},
        )
        fascist_nodes = {
            node["id"]: node for node in IDEOLOGY_TREES["fascism"]
        }
        self.assertEqual(
            set(fascist_nodes["fascism_army_state"]["requires"]),
            {"fascism_heavy_industry", "fascism_militarized_state"},
        )
        for nodes in IDEOLOGY_TREES.values():
            node_ids = {node["id"] for node in nodes}
            for node in nodes:
                self.assertTrue(set(node["requires"]) <= node_ids, node["id"])
        technology_ids = {node["id"] for node in TECH_TREE}
        for node in TECH_TREE:
            self.assertTrue(
                set(node["requires"]) <= technology_ids, node["id"]
            )
        self.assertTrue(any(
            value < 0
            for nodes in IDEOLOGY_TREES.values()
            for node in nodes
            for value in node["bonuses"].values()
        ))
        self.assertTrue(any(
            value < 0
            for node in TECH_TREE
            for value in node.get("bonuses", {}).values()
        ))

        self.world.new_game("usa")
        country = self.world.countries["usa"]
        country.money = 100_000
        country.research_points = 1000
        country.techs.add("strategic_deterrence")
        country.stability = 50
        initial_strength = country.military_strength(self.world)
        initial_upkeep = country.economy_report()["upkeep"]

        self.assertTrue(
            self.world.research_technology("usa", "total_mobilization")[0]
        )
        self.assertGreater(country.military_strength(self.world), initial_strength)
        self.assertGreater(country.economy_report()["upkeep"], initial_upkeep)

        class NoRandom:
            @staticmethod
            def random():
                return 1.0

        country.advance_day(NoRandom(), country.region_count(self.world), 0)
        self.assertLess(country.stability, 50)
        self.assertGreater(
            ideology_bonuses("fascism", {"fascism_total_war"})["unrest"], 0
        )

    def test_technology_and_ideology_choices_lock_competing_branches(self):
        self.world.new_game("usa")
        country = self.world.countries["usa"]
        country.money = 100_000
        country.research_points = 1000
        country.techs.update({"civil_industry", "future_energy"})
        self.assertTrue(
            self.world.research_technology("usa", "green_transition")[0]
        )
        money_after_choice = country.money
        success, message = self.world.research_technology(
            "usa", "market_consolidation"
        )
        self.assertFalse(success)
        self.assertIn("ветку", message)
        self.assertEqual(country.money, money_after_choice)

        country.ideology = "communism"
        country.political_power = 5000
        country.ideology_upgrades.update({
            "communism_productive_targets",
            "communism_people_militia",
            "communism_party_discipline",
        })
        self.assertTrue(
            develop_ideology(country, "communism_national_program")[0]
        )
        self.assertTrue(
            develop_ideology(country, "communism_state_planned_economy")[0]
        )
        points_after_choice = country.political_power
        success, message = develop_ideology(country, "communism_social_investment")
        self.assertFalse(success)
        self.assertIn("направление", message)
        self.assertEqual(country.political_power, points_after_choice)

    def test_political_courses_apply_policy_and_change_leadership(self):
        self.world.new_game("usa")
        country = self.world.countries["usa"]
        country.money = 100_000
        country.political_power = 5000
        old_leader = country.leader

        self.assertTrue(
            self.world.start_political_course(
                "usa", "national_reconstruction"
            )[0]
        )
        for _ in range(25):
            self.world._advance_political_course(country)
        self.assertIn("national_reconstruction", country.political_policies)
        self.assertTrue(
            self.world.start_political_course("usa", "leadership_mandate")[0]
        )
        for _ in range(30):
            self.world._advance_political_course(country)
        self.assertNotEqual(country.leader, old_leader)
        self.assertIn("leadership_mandate", country.political_policies)

        restored = Country.from_dict(country.to_dict())
        self.assertEqual(restored.leader, country.leader)
        self.assertEqual(restored.political_policies, country.political_policies)

    def test_molotov_ribbentrop_course_requires_ww2_date_and_blocks_war(self):
        self.world.new_game("ussr", "ww2")
        ussr = self.world.countries["ussr"]
        ussr.money = 100_000
        ussr.political_power = 5000
        self.assertFalse(
            self.world.start_political_course(
                "ussr", "molotov_ribbentrop_pact"
            )[0]
        )

        self.world.year = 1939
        self.assertTrue(
            self.world.start_political_course(
                "ussr", "molotov_ribbentrop_pact"
            )[0]
        )
        for _ in range(60):
            self.world._advance_political_course(ussr)
        self.assertIn("germany", ussr.pacts)
        success, message = self.world.declare_war("ussr", "germany")
        self.assertFalse(success)
        self.assertIn("пакт", message)

    def test_political_pacts_create_real_alliances_and_trade_treaties(self):
        self.world.new_game("germany", "ww2")
        germany = self.world.countries["germany"]
        germany.money = 100_000
        germany.political_power = 5000
        self.world.year = 1939
        self.assertTrue(self.world.start_political_course("germany", "steel_pact")[0])
        for _ in range(45):
            self.world._advance_political_course(germany)
        italy = self.world.countries["italy"]
        self.assertEqual(germany.alliance, italy.id)
        self.assertEqual(italy.alliance, germany.id)
        self.assertGreater(italy.treaty_bonuses().get("military", 0), 0)
        self.assertTrue(self.world.diplomacy.break_alliance("germany", "italy")[0])
        self.assertNotIn("italy", germany.treaties)
        self.assertEqual(italy.treaty_bonuses().get("military", 0), 0)

        self.world.new_game("france", "modern")
        france = self.world.countries["france"]
        france.money = 100_000
        france.political_power = 5000
        self.assertTrue(
            self.world.start_political_course(
                "france", "european_recovery_compact"
            )[0]
        )
        for _ in range(40):
            self.world._advance_political_course(france)
        germany = self.world.countries["germany"]
        self.assertEqual(
            france.treaties["germany"]["type"], "trade"
        )
        self.assertGreater(france.treaty_bonuses().get("taxes", 0), 0)
        self.assertGreater(germany.treaty_bonuses().get("research", 0), 0)
        expires = self.world.absolute_day() + 1
        france.treaties["germany"]["expires"] = expires
        germany.treaties["france"]["expires"] = expires
        self.world.advance_day()
        self.assertNotIn("germany", france.treaties)
        self.assertNotIn("france", germany.treaties)
        self.assertEqual(france.treaty_bonuses().get("taxes", 0), 0)

    def test_event_renderer_accepts_saved_consequence_lists(self):
        pygame.font.init()
        surface = pygame.Surface((320, 80))
        lines = GameScreen._draw_wrapped(
            surface,
            ["Доход: +10%", "Поддержка: +4"],
            0, 0, pygame.font.SysFont("Arial", 10), (255, 255, 255), 300,
        )
        self.assertGreater(lines, 0)

    def test_every_research_node_has_a_working_effect_handler(self):
        for node in TECH_TREE:
            country = Country({
                "id": "test",
                "name": "Test",
                "color": [1, 2, 3],
                "population": 1_000_000,
                "money": node["cost"],
                "food": 50,
                "industry": 20,
                "energy": 50,
            })
            country.techs.update(node["requires"])
            country.research_points = node["points"]

            success, message = research(country, node["id"])

            self.assertTrue(success, f"{node['id']}: {message}")

    def test_peace_offers_wait_for_a_response_and_ai_can_propose_them(self):
        self.world.new_game("usa")
        self.assertTrue(self.world.declare_war("usa", "canada")[0])
        war = self.world.war_between("usa", "canada")

        self.assertTrue(self.world.offer_peace("usa", "canada", "status_quo")[0])
        self.assertEqual(war.status, "active")
        self.assertEqual(war.peace_offer["recipient"], "canada")
        self.world.rng.seed(3)
        self.world.ai.update()
        self.assertIsNone(war.peace_offer)
        self.assertEqual(war.status, "active")

        war.attacker_score = 80
        war.defender_score = 0
        self.world.countries["canada"].war_exhaustion = 65
        self.world.countries["canada"].war_support = 20
        war.last_peace_offer_day -= 30
        self.assertTrue(self.world.propose_ai_peace(war)[0])
        self.assertEqual(war.peace_offer["proposer"], "canada")
        self.assertEqual(war.peace_offer["recipient"], "usa")
        self.assertEqual(war.status, "active")
        self.assertTrue(self.world.respond_peace_offer(war.id, "usa", False)[0])
        self.assertIsNone(war.peace_offer)
        self.assertEqual(war.status, "active")
        self.assertFalse(self.world.propose_ai_peace(war)[0])
        self.assertEqual(war.last_peace_offer_day, self.world.absolute_day())

        war.defender_score = 100
        self.world.day += 30
        self.assertTrue(self.world.offer_peace("usa", "canada", "transfer")[0])
        self.world.ai.update()
        self.assertEqual(war.status, "ended")
        self.assertEqual(war.settlement, "transfer")

    def test_player_can_accept_an_ai_proposed_peace(self):
        self.world.new_game("usa")
        self.assertTrue(self.world.declare_war("usa", "canada")[0])
        war = self.world.war_between("usa", "canada")
        war.attacker_score = 100
        self.world.countries["canada"].war_exhaustion = 70

        self.assertTrue(self.world.propose_ai_peace(war)[0])
        self.assertTrue(self.world.respond_peace_offer(war.id, "usa", True)[0])
        self.assertEqual(war.status, "ended")
        self.assertEqual(war.settlement, "status_quo")

    def test_ai_replenishes_its_army_during_war(self):
        self.world.new_game("usa")
        self.assertTrue(self.world.declare_war("usa", "canada")[0])
        canada = self.world.countries["canada"]
        target_size = int(
            canada.population * (0.0015 + canada.military / 100000)
        )
        canada.army_size = int(target_size * 0.5)
        canada.money = 5000
        canada.war_support = 40
        initial_army_size = canada.army_size
        initial_support = canada.war_support
        war = self.world.war_between("usa", "canada")
        war.last_ai_operation_day = self.world.absolute_day()
        self.world.rng.seed(7)

        self.world.ai.update()

        self.assertGreater(canada.army_size, initial_army_size)
        self.assertGreater(canada.war_support, initial_support)
        self.assertGreater(canada.recruitment_ready_day, self.world.absolute_day())

    def test_capitulation_transfers_all_target_regions(self):
        self.world.new_game("usa")
        initial_usa = self.world.province_count("usa")
        initial_canada = self.world.province_count("canada")
        self.assertTrue(self.world.declare_war("usa", "canada")[0])
        war = self.world.war_between("usa", "canada")
        war.attacker_score = 36

        self.assertFalse(self.world.can_capitulate(war, "usa"))
        self.assertFalse(self.world.can_capitulate(war, "canada"))
        war.attacker_score = 60
        self.world.countries["canada"].war_exhaustion = 55
        self.world.countries["canada"].war_support = 30
        canada_provinces = [
            province for province in self.world.provinces
            if province.owner == "canada"
        ]
        capital_id = self.world.capital_provinces["canada"]
        provinces_to_capture = [
            province for province in canada_provinces
            if province.id == capital_id
        ]
        provinces_to_capture.extend(
            province for province in canada_provinces
            if province.id != capital_id
        )
        capture_limit = max(1, math.ceil(len(canada_provinces) * 0.7))
        self.assertGreater(len(canada_provinces), 3)
        for province in provinces_to_capture[:3]:
            self.world._set_region_owner(
                province, "usa", "province", occupied=False,
                update_neighbors=False,
            )
        self.world._refresh_country_neighbors()
        self.assertFalse(self.world.can_capitulate(war, "usa"))
        for province in provinces_to_capture[3:capture_limit]:
            self.world._set_region_owner(
                province, "usa", "province", occupied=False,
                update_neighbors=False,
            )
        self.world._refresh_country_neighbors()

        self.assertTrue(self.world.can_capitulate(war, "usa"))
        self.assertFalse(self.world.can_capitulate(war, "canada"))
        self.assertTrue(self.world.settle_war("usa", "canada", "capitulation")[0])
        self.assertEqual(self.world.province_count("canada"), 0)
        self.assertEqual(
            self.world.province_count("usa"),
            initial_usa + initial_canada,
        )
        self.assertEqual(war.status, "ended")

    def test_capitulation_does_not_award_target_to_remote_allied_war_member(self):
        self.world.new_game("germany")
        germany = self.world.countries["germany"]
        italy = self.world.countries["italy"]
        germany.alliance = italy.id
        italy.alliance = germany.id
        italy.military = 100
        italy.army_size = 20_000_000
        initial_italy = self.world.province_count(italy.id)
        initial_germany = self.world.province_count(germany.id)
        initial_poland = self.world.province_count("poland")

        self.assertTrue(self.world.declare_war(germany.id, "poland")[0])
        war = self.world.war_between(germany.id, "poland")
        self.assertEqual(war.attackers, [germany.id, italy.id])
        self.assertFalse(self.world.can_attack(italy.id, "poland"))

        poland = self.world.countries["poland"]
        poland.war_exhaustion = 90
        poland.war_support = 10
        war.attacker_score = 100
        polish_provinces = [
            province for province in self.world.provinces
            if province.owner == poland.id
        ]
        capital = self.world.provinces_by_id[
            self.world.capital_provinces[poland.id]
        ]
        captured = [capital] + [
            province for province in polish_provinces
            if province.id != capital.id
        ][:math.ceil(initial_poland * 0.7) - 1]
        for province in captured:
            self.world._set_region_owner(
                province, germany.id, "province", occupied=False
            )

        self.assertTrue(self.world.can_capitulate(war, italy.id))
        self.assertTrue(
            self.world.settle_war(italy.id, poland.id, "capitulation")[0]
        )

        self.assertEqual(self.world.province_count(italy.id), initial_italy)
        self.assertEqual(
            self.world.province_count(germany.id),
            initial_germany + initial_poland,
        )
        self.assertEqual(war.status, "ended")
        self.assertNotIn("poland", germany.wars)
        self.assertNotIn("poland", italy.wars)

    def test_ai_wars_end_after_victory_or_long_stalemate(self):
        self.world.new_game("usa")
        self.assertTrue(self.world.declare_war("canada", "mexico")[0])
        war = self.world.war_between("canada", "mexico")
        war.attacker_score = 60
        mexican_provinces = [
            province for province in self.world.provinces
            if province.owner == "mexico"
        ]
        capital_id = self.world.capital_provinces["mexico"]
        provinces_to_capture = [
            province for province in mexican_provinces
            if province.id == capital_id
        ]
        provinces_to_capture.extend(
            province for province in mexican_provinces
            if province.id != capital_id
        )
        for province in provinces_to_capture[
            :max(1, math.ceil(len(mexican_provinces) * 0.7))
        ]:
            self.world._set_region_owner(
                province, "canada", "province", occupied=False,
                update_neighbors=False,
            )
        self.world._refresh_country_neighbors()

        self.assertTrue(self.world.ai._resolve_ai_war_end(war))
        self.assertEqual(war.status, "ended")
        self.assertEqual(war.settlement, "capitulation")
        self.assertTrue(self.world.countries["mexico"].is_defeated)

        self.assertTrue(self.world.declare_war("brazil", "argentina")[0])
        stalled_war = self.world.war_between("brazil", "argentina")
        stalled_war.last_progress_day = self.world.absolute_day() - 240
        self.assertTrue(self.world.ai._resolve_ai_war_end(stalled_war))
        self.assertEqual(stalled_war.status, "ended")
        self.assertEqual(stalled_war.settlement, "status_quo")

    def test_important_event_queue_pauses_and_survives_saves(self):
        self.world.new_game("usa")
        self.world.add_event("Первое событие", notify=True, modal=True)
        self.world.add_event("Второе событие", notify=True, modal=True)
        self.assertTrue(self.world.time.paused)
        self.assertEqual(len(self.world.pending_modal_events), 2)

        with tempfile.TemporaryDirectory() as save_dir:
            saves = SaveSystem(save_dir)
            self.assertTrue(saves.save(self.world, 1)[0])
            loaded = World()
            self.assertTrue(saves.load(loaded, 1)[0])

        self.assertTrue(loaded.time.paused)
        self.assertEqual(len(loaded.pending_modal_events), 2)
        loaded.acknowledge_modal_event()
        self.assertTrue(loaded.time.paused)
        loaded.acknowledge_modal_event()
        self.assertFalse(loaded.time.paused)

    def test_auto_skip_news_prevents_modal_pause_and_is_saved(self):
        self.world.new_game("usa")
        screen = GameScreen.__new__(GameScreen)
        screen.world = self.world
        screen.auto_skip_news = False
        screen.toggle_auto_skip_news()
        self.assertTrue(self.world.auto_skip_news)
        self.world.notifications.clear()
        self.world.add_event("Первая новость", notify=True, modal=True)
        self.world.add_event("Вторая новость", notify=True, modal=True)

        self.assertFalse(self.world.pending_modal_events)
        self.assertFalse(self.world.time.paused)
        self.assertEqual(len(self.world.notifications), 2)

        with tempfile.TemporaryDirectory() as save_dir:
            saves = SaveSystem(save_dir)
            self.assertTrue(saves.save(self.world, 1)[0])
            loaded = World()
            self.assertTrue(saves.load(loaded, 1)[0])
        self.assertTrue(loaded.auto_skip_news)

        loaded.time.paused = True
        screen.world = loaded
        screen.auto_skip_news = False
        loaded.auto_skip_news = False
        loaded.add_event("Новость на ручной паузе", notify=True, modal=True)
        self.assertTrue(loaded.pending_modal_events)
        screen.toggle_auto_skip_news()
        self.assertFalse(loaded.pending_modal_events)
        self.assertTrue(loaded.time.paused)

    def test_zombie_decision_event_is_unskippable_and_applies_global_choice(self):
        self.world.new_game("uk", "zombie")
        self.world.auto_skip_news = True
        eu = self.world.countries["eu"]
        eu.unrest = 40
        eu.money = 10_000
        regions_before = self.world.province_count("eu")
        population_before = eu.population
        political_power_before = eu.political_power
        military_before = eu.decision_modifiers.get("military_strength", 0)

        self.assertTrue(
            self.world.present_decision_event(
                "france_quarantine_resistance", "eu"
            )
        )
        self.assertTrue(self.world.time.paused)
        self.assertFalse(self.world.acknowledge_modal_event())
        self.assertTrue(
            self.world.pending_modal_events[0]["decision_id"]
            == "france_quarantine_resistance"
        )

        with tempfile.TemporaryDirectory() as save_dir:
            saves = SaveSystem(save_dir)
            self.assertTrue(saves.save(self.world, 1)[0])
            loaded = World()
            self.assertTrue(saves.load(loaded, 1)[0])
        self.assertTrue(loaded.auto_skip_news)
        self.assertEqual(len(loaded.pending_modal_events), 1)

        self.assertTrue(loaded.resolve_decision_event(1)[0])
        resolved_eu = loaded.countries["eu"]
        self.assertEqual(loaded.province_count("eu"), regions_before - 5)
        self.assertEqual(resolved_eu.population, population_before)
        self.assertEqual(resolved_eu.unrest, 20)
        self.assertEqual(
            resolved_eu.decision_modifiers["military_strength"],
            military_before + 0.20,
        )
        self.assertEqual(
            resolved_eu.decision_modifiers["unrest_growth"], -0.05
        )
        self.assertEqual(resolved_eu.money, 8000)
        self.assertEqual(
            resolved_eu.political_power, political_power_before + 50
        )
        self.assertFalse(loaded.pending_modal_events)
        self.assertFalse(loaded.time.paused)

    def test_zombie_decision_event_catalog_has_fifteen_valid_choices(self):
        self.assertGreaterEqual(len(DECISION_EVENTS), 15)
        supported_effects = {
            "money", "population", "stability", "unrest", "political_power",
            "research_points", "army_size", "army_readiness", "food",
            "energy", "industry", "development", "army_growth",
            "military_strength", "unrest_growth", "global_military_strength",
            "lose_regions", "infect_regions",
        }
        for event in DECISION_EVENTS:
            self.assertEqual(len(event["choices"]), 2)
            for choice in event["choices"]:
                self.assertTrue(choice["name"])
                self.assertTrue(choice["consequence"])
                self.assertLessEqual(
                    set(choice["effects"]) - supported_effects, set()
                )
                if choice.get("risk"):
                    self.assertLessEqual(
                        set(choice["risk"]["effects"]) - supported_effects,
                        set(),
                    )

    def test_last_territory_capture_marks_country_defeated_and_ends_war(self):
        self.world.new_game("canada")
        usa = self.world.countries["usa"]
        canada = self.world.countries["canada"]
        usa.money = 20_000
        usa.military = 100
        usa.army_size = 1_000_000
        usa.army_readiness = 100
        usa.war_support = 100
        canada.military = 0
        canada.army_size = 1000
        canada.army_readiness = 10
        canada.war_support = 0
        self.assertTrue(self.world.declare_war(usa.id, canada.id)[0])
        war = self.world.war_between(usa.id, canada.id)
        fronts, kind = self.world._front_regions(war.attackers, war.defenders)
        self.assertEqual(kind, "province")
        target = fronts[0]
        for province in self.world.provinces:
            if province.owner == canada.id and province.id != target.id:
                self.world._set_region_owner(
                    province, usa.id, "province", occupied=False,
                    update_neighbors=False,
                )
        self.world._refresh_country_neighbors()

        class CertainVictory:
            @staticmethod
            def choice(values):
                return values[0]

            @staticmethod
            def uniform(low, high):
                return high

        self.world.rng = CertainVictory()
        self.assertTrue(
            self.world.resolve_conflict(usa.id, canada.id, target.id)[0]
        )

        self.assertTrue(canada.is_defeated)
        self.assertEqual(self.world.territory_count(canada.id), 0)
        self.assertEqual(war.status, "ended")
        self.assertFalse(canada.wars)
        self.assertTrue(self.world.time.paused)
        with tempfile.TemporaryDirectory() as save_dir:
            saves = SaveSystem(save_dir)
            saves.save(self.world, 1)
            loaded = World()
            self.assertTrue(saves.load(loaded, 1)[0])
        self.assertTrue(loaded.countries[canada.id].is_defeated)
        self.assertEqual(loaded.territory_count(canada.id), 0)

    def test_conquered_ai_country_is_defeated_without_manual_capitulation(self):
        self.world.new_game("usa")
        usa = self.world.countries["usa"]
        canada = self.world.countries["canada"]
        usa.money = 20_000
        usa.military = 100
        usa.army_size = 1_000_000
        usa.army_readiness = 100
        usa.war_support = 100
        canada.military = 0
        canada.army_size = 1000
        canada.army_readiness = 10
        canada.war_support = 0
        self.assertTrue(self.world.declare_war(usa.id, canada.id)[0])
        war = self.world.war_between(usa.id, canada.id)
        fronts, _ = self.world._front_regions(war.attackers, war.defenders)
        target = fronts[0]
        for province in self.world.provinces:
            if province.owner == canada.id and province.id != target.id:
                self.world._set_region_owner(
                    province, usa.id, "province", occupied=False,
                    update_neighbors=False,
                )
        self.world._refresh_country_neighbors()

        class CertainVictory:
            @staticmethod
            def choice(values):
                return values[0]

            @staticmethod
            def uniform(low, high):
                return high

        self.world.rng = CertainVictory()
        self.assertTrue(
            self.world.resolve_conflict(usa.id, canada.id, target.id)[0]
        )
        self.assertTrue(canada.is_defeated)
        self.assertEqual(war.status, "ended")
        self.assertEqual(war.settlement, "capitulation")

    def test_losing_player_cannot_trigger_own_capitulation(self):
        self.world.new_game("usa")
        self.assertTrue(self.world.declare_war("usa", "canada")[0])
        war = self.world.war_between("usa", "canada")
        war.defender_score = 60
        self.world.countries["usa"].war_exhaustion = 80
        self.world.countries["usa"].war_support = 10
        usa_provinces = [
            province for province in self.world.provinces
            if province.owner == "usa"
        ]
        for province in usa_provinces[:math.ceil(len(usa_provinces) * 0.5)]:
            self.world._set_region_owner(
                province, "canada", "province", occupied=False,
                update_neighbors=False,
            )
        self.world._refresh_country_neighbors()
        before = self.world.province_count("usa")

        self.assertTrue(self.world.can_capitulate(war, "canada"))
        self.assertFalse(self.world.can_capitulate(war, "usa"))
        self.assertFalse(self.world.settle_war("usa", "canada", "capitulation")[0])
        self.assertEqual(war.status, "active")
        self.assertEqual(self.world.province_count("usa"), before)

    def test_ai_counterattacks_player_front_after_operation_cooldown(self):
        class FixedRandom:
            def random(self):
                return 0.5

            def shuffle(self, values):
                return None

            def choice(self, values):
                return values[0]

            def uniform(self, low, high):
                return high

        self.world.new_game("usa")
        player = self.world.countries["usa"]
        player.alliance = "mexico"
        mexico = self.world.countries["mexico"]
        mexico.alliance = player.id
        player.relations[mexico.id] = 60
        mexico.relations[player.id] = 60
        player.military = 0
        player.army_size = 1000
        player.army_readiness = 10
        player.war_support = 0
        canada = self.world.countries["canada"]
        canada.military = 100
        canada.army_size = 5_000_000
        canada.army_readiness = 100
        canada.war_support = 100
        canada.money = 20_000
        self.world.rng = FixedRandom()
        initial_player_regions = self.world.province_count(player.id)
        initial_mexico_regions = self.world.province_count(mexico.id)

        self.assertTrue(self.world.declare_war(player.id, canada.id)[0])
        war = self.world.war_between(player.id, canada.id)
        def advance_and_acknowledge_events():
            self.world.advance_day()
            while self.world.pending_modal_events:
                self.world.acknowledge_modal_event()

        while self.world.pending_modal_events:
            self.world.acknowledge_modal_event()
        advance_and_acknowledge_events()

        self.assertEqual(war.battles, 1)
        self.assertEqual(self.world.province_count(player.id), initial_player_regions - 1)
        self.assertEqual(self.world.province_count(mexico.id), initial_mexico_regions)
        for _ in range(2):
            advance_and_acknowledge_events()
        self.assertEqual(war.battles, 1)

        advance_and_acknowledge_events()
        self.assertEqual(war.battles, 2)

    def test_active_war_state_survives_save_round_trip(self):
        self.world.new_game("germany")
        self.assertTrue(self.world.declare_war("germany", "poland")[0])
        war = self.world.war_between("germany", "poland")
        war.attacker_score = 24
        war.last_ai_operation_day = self.world.absolute_day() - 3
        war.last_peace_offer_day = self.world.absolute_day() - 11
        war.peace_offer = {
            "proposer": "germany",
            "recipient": "poland",
            "terms": "status_quo",
            "proposed_day": self.world.absolute_day(),
        }
        war.casualties["germany"] = 1300
        with tempfile.TemporaryDirectory() as save_dir:
            saves = SaveSystem(save_dir)
            saves.save(self.world, 1)
            loaded = World()
            self.assertTrue(saves.load(loaded, 1)[0])

        loaded_war = loaded.war_between("germany", "poland")
        self.assertIsNotNone(loaded_war)
        self.assertEqual(loaded_war.attacker_score, 24)
        self.assertEqual(
            loaded_war.last_ai_operation_day,
            self.world.absolute_day() - 3,
        )
        self.assertEqual(
            loaded_war.last_peace_offer_day,
            self.world.absolute_day() - 11,
        )
        self.assertEqual(loaded_war.peace_offer["terms"], "status_quo")
        self.assertEqual(loaded_war.casualties["germany"], 1300)
        self.assertEqual(loaded_war.objective["target"], "poland")

    def test_save_round_trip_preserves_scenario_and_map_changes(self):
        self.world.new_game("germany", "ww2")
        captured_province = next(
            province for province in self.world.provinces if province.owner == "germany"
        )
        captured_province.owner = "france"
        captured_province.occupied = True
        with tempfile.TemporaryDirectory() as save_dir:
            saves = SaveSystem(save_dir)
            saves.save(self.world, 1)
            loaded = World()
            self.assertTrue(saves.load(loaded, 1)[0])
        self.assertEqual(loaded.scenario_id, "ww2")
        self.assertEqual(loaded.year, 1936)
        self.assertEqual(loaded.player_id, "germany")
        self.assertEqual(len(loaded.detailed_regions), len(self.world.detailed_regions))
        self.assertEqual(loaded.provinces_by_id[captured_province.id].owner, "france")
        self.assertTrue(loaded.provinces_by_id[captured_province.id].occupied)

    def test_render_update_does_not_advance_calendar(self):
        self.world.new_game("germany")
        self.world.update(30)
        self.assertEqual(self.world.day, 0)
        self.world.advance_day()
        self.assertEqual(self.world.day, 1)

    def test_zombie_scenario_starts_with_global_war_and_continental_outbreaks(self):
        self.world.rng.seed(0)
        self.world.new_game("usa", "zombie")
        italian_outbreak = {
            "ITA-5400", "ITA-5397", "ITA-5396", "ITA-5398", "ITA-5399",
            "ITA-5404", "ITA-5405", "ITA-5403", "ITA-5406", "ITA-5407",
            "ITA-5408", "ITA-5389", "ITA-5390", "ITA-5391", "ITA-5392",
            "ITA-5393", "ITA-5395", "ITA-5394", "ITA-5409", "ITA-5411",
            "ITA-5410", "ITA-5417", "ITA-5416", "ITA-5415", "ITA-5414",
            "ITA-5413", "ITA-5412", "ITA-5401", "ITA-5402", "ITA-5419",
            "ITA-5418", "ITA-5421", "ITA-5420", "ITA-5426", "ITA-5422",
            "ITA-5423", "ITA-5424", "ITA-5425", "ITA-5433", "ITA-5432",
            "ITA-5427", "ITA-5429", "ITA-5430", "ITA-5431", "ITA-5428",
            "ITA-5379", "ITA-5380", "ITA-5381", "ITA-5383", "ITA-5382",
            "ITA-5388", "ITA-5387", "ITA-5386", "ITA-5384", "ITA-5385",
        }
        infected = {
            province.id.rsplit("_", 1)[-1]
            for province in self.world.provinces
            if province.owner == "zombies"
        }
        war = self.world.war_between("usa", "zombies")

        self.assertEqual(self.world.year, 2031)
        self.assertEqual(
            {item for item in infected if item.startswith("ITA-")},
            italian_outbreak,
        )
        self.assertEqual(
            len(infected.intersection({
                "CHN-1807", "CHN-1812", "CHN-1804", "CHN-1154",
            })),
            4,
        )
        for country_ids in ZOMBIE_OUTBREAK_COUNTRIES_BY_CONTINENT.values():
            seeded_regions = [
                province for province in self.world.provinces
                if province.owner == "zombies"
                and province.initial_owner in country_ids
            ]
            self.assertIn(len(seeded_regions), (2, 3))
        self.assertNotIn("USA-3521", infected)
        self.assertEqual(len(italian_outbreak), 55)
        self.assertGreater(
            self.world.countries["zombies"].military_strength(self.world),
            self.world.countries["eu"].military_strength(self.world) * 1.1,
        )
        self.assertEqual(self.world.countries["eu"].name, "Европейский союз")
        self.assertEqual(
            self.world._scenario_settings()["selectable_countries"],
            ["eu", "usa", "russia", "china", "uk"],
        )
        self.assertIsNotNone(war)
        self.assertEqual(war.objective["type"], "zombie_outbreak")
        self.assertEqual(len(war.attackers), 1)
        self.assertEqual(war.attackers[0], "zombies")
        self.assertEqual(len(war.defenders), len(self.world.countries) - 1)
        self.assertTrue(self.world.can_attack("china", "zombies"))
        self.assertFalse(self.world.can_attack("uk", "zombies"))
        zombie_fronts, _ = self.world._front_regions(
            ["zombies"], war.enemies("zombies")
        )
        sea_landing = next(
            province for province in zombie_fronts
            if not any(
                self.world.provinces_by_id[neighbor_id].owner == "zombies"
                for neighbor_id in self.world.province_neighbors.get(
                    province.id, ()
                )
            )
        )
        self.assertTrue(self.world.can_attack("zombies", sea_landing.owner))
        self.assertEqual(self.world.countries["usa"].tax_rate_cap, 20)
        self.assertEqual(self.world.countries["zombies"].alliance, None)
        self.world.countries["zombies"].army_size = 100_000_000
        self.assertTrue(
            self.world.resolve_conflict(
                "zombies", sea_landing.owner, sea_landing.id
            )[0]
        )
        self.assertEqual(
            self.world.zombie_breach_ready_day,
            self.world.absolute_day() + 30,
        )
        takeover_threshold = math.ceil(len(self.world.provinces) * 0.75)
        for province in self.world.provinces[:takeover_threshold]:
            province.owner = "zombies"
        self.world._rebuild_territory_counts()
        self.assertEqual(
            self.world._update_zombie_scenario_outcome(), "zombies_win"
        )
        self.assertTrue(self.world.time.paused)

    def test_zombie_scenario_uses_exclusive_trees_tax_and_recruitment_rules(self):
        self.world.new_game("china", "zombie")
        self.world.ai.update = lambda: None
        self.world.event_system.try_random_event = lambda: None
        survivor = self.world.countries["china"]
        survivor.money = 10000
        survivor.research_points = 100
        self.assertEqual(
            {item["id"] for item in self.world.technology_tree_for("china")},
            {item["id"] for item in self.world.technology_tree_for("usa")},
        )
        self.assertNotIn(
            "administration",
            {item["id"] for item in self.world.technology_tree_for("china")},
        )
        self.assertTrue(self.world.research_technology("china", "survivor_network")[0])
        self.assertNotIn("survivor_network", survivor.techs)
        while survivor.active_upgrade:
            self.world.advance_day()
        self.assertIn("survivor_network", survivor.techs)
        self.assertTrue(self.world.research_technology("china", "survivor_vaccine")[0])
        while survivor.active_upgrade:
            self.world.advance_day()
        self.assertIn("survivor_vaccine", survivor.techs)
        self.assertFalse(
            self.world.research_technology("china", "survivor_quarantine")[0]
        )

        survivor.political_power = 1000
        self.assertTrue(
            self.world.develop_ideology(
                "china", "z_emergency_emergency_program"
            )[0]
        )
        self.assertNotIn(
            "z_emergency_emergency_program", survivor.ideology_upgrades
        )
        while survivor.active_upgrade:
            self.world.advance_day()
        self.assertTrue(
            self.world.develop_ideology("china", "z_emergency_civil_defense")[0]
        )
        while survivor.active_upgrade:
            self.world.advance_day()
        self.assertFalse(
            self.world.develop_ideology("china", "z_emergency_safe_corridors")[0]
        )
        self.assertFalse(self.world.change_ideology("china", "democracy")[0])

        survivor.tax_rate = 19
        self.assertEqual(survivor.set_tax_rate(1), 20)
        self.assertEqual(survivor.set_tax_rate(1), 20)
        self.world.event_system.apply_event(
            survivor, {"id": "test_tax_cap", "effects": {"tax_rate": 10}}
        )
        self.assertEqual(survivor.tax_rate, 20)

        zombies = self.world.countries["zombies"]
        zombies.army_size = 100
        self.assertTrue(self.world.can_recruit("zombies"))
        self.assertTrue(self.world.recruit("zombies")[0])
        zombies.unrest = 100
        zombies.stability = 0
        zombies.government_support = 0
        self.world._process_rebellions()
        self.assertFalse(any(
            country_id.startswith("rebels_zombies_")
            for country_id in self.world.countries
        ))

    def test_zombies_join_rebellion_wars_and_can_attack_rebels(self):
        self.world.new_game("usa", "zombie")
        infected = next(
            province for province in self.world.provinces
            if province.owner == "zombies"
            and sum(
                self.world.provinces_by_id[neighbor_id].owner != "zombies"
                for neighbor_id in self.world.province_neighbors[province.id]
            ) >= 2
        )
        rebel_provinces = [
            self.world.provinces_by_id[neighbor_id]
            for neighbor_id in self.world.province_neighbors[infected.id]
            if self.world.provinces_by_id[neighbor_id].owner != "zombies"
        ][:2]
        self.assertEqual(len(rebel_provinces), 2)
        parent_id = rebel_provinces[0].owner
        rebel_data = self.world.countries[parent_id].to_dict()
        rebel_data.update(
            id="rebels_test", name="Повстанцы", military=0, army_size=1000,
            army_readiness=1, war_support=0, unrest=0, stability=50,
            political_policies=[], emergency_measures=[], active_upgrade=None,
        )
        rebels = Country.from_dict(rebel_data)
        self.world.countries[rebels.id] = rebels
        self.world.region_counts[rebels.id] = 0
        self.world.province_counts[rebels.id] = 0
        for country in self.world.countries.values():
            if country.id != rebels.id:
                country.relations[rebels.id] = -100 if country.id == parent_id else 0
                rebels.relations[country.id] = country.relations[rebels.id]
        for province in rebel_provinces:
            self.world._set_region_owner(
                province, rebels.id, "province", occupied=False
            )
        self.world.capital_provinces[rebels.id] = rebel_provinces[0].id
        self.world._add_war(
            [parent_id], [rebels.id],
            {"type": "rebellion", "target": rebels.id},
        )
        self.world._join_zombie_outbreak(rebels)
        outbreak = self.world.war_between("zombies", rebels.id)
        self.assertIsNotNone(outbreak)
        self.assertIn(rebels.id, outbreak.defenders)
        self.assertIn("zombies", rebels.wars)
        self.assertTrue(self.world.can_attack("zombies", rebels.id))

        zombies = self.world.countries["zombies"]
        zombies.money = 10000
        zombies.army_size = 100_000_000
        zombies.military = 100
        captured = rebel_provinces[0]
        self.assertTrue(
            self.world.resolve_conflict(
                "zombies", rebels.id, captured.id
            )[0]
        )
        self.assertEqual(captured.owner, "zombies")

    def test_zombie_political_command_unlocks_all_response_courses(self):
        from game.political_courses import course_available

        self.world.new_game("usa", "zombie")
        country = self.world.countries["usa"]
        country.money = 100_000
        country.political_power = 5000
        self.assertTrue(
            self.world.start_political_course(
                "usa", "outbreak_emergency_command"
            )[0]
        )
        for _ in range(18):
            self.world._advance_political_course(country)

        responses = (
            "outbreak_vaccine_program",
            "outbreak_quarantine_network",
            "outbreak_evacuation_network",
        )
        self.assertTrue(
            all(
                course_available(self.world, country, course_id)
                for course_id in responses
            )
        )
        self.assertTrue(
            self.world.start_political_course(
                "usa", "outbreak_vaccine_program"
            )[0]
        )
        for _ in range(28):
            self.world._advance_political_course(country)
        self.assertTrue(
            course_available(
                self.world, country, "outbreak_quarantine_network"
            )
        )
        self.assertTrue(
            course_available(
                self.world, country, "outbreak_evacuation_network"
            )
        )

    def test_zombie_emergency_measures_take_time_and_change_global_rules(self):
        self.world.new_game("usa", "zombie")
        self.world.ai.update = lambda: None
        self.world.event_system.try_random_event = lambda: None
        country = self.world.countries["usa"]
        country.money = 100_000
        country.research_points = 1000
        self.assertTrue(
            self.world.start_emergency_measure(
                "usa", "emergency_crisis_headquarters"
            )[0]
        )
        self.assertNotIn(
            "emergency_crisis_headquarters", country.emergency_measures
        )
        with tempfile.TemporaryDirectory() as save_dir:
            saves = SaveSystem(save_dir)
            self.assertTrue(saves.save(self.world, 1)[0])
            loaded = World()
            self.assertTrue(saves.load(loaded, 1)[0])
        self.assertEqual(
            loaded.countries["usa"].active_upgrade["kind"],
            "emergency_measure",
        )
        self.assertEqual(
            loaded.countries["usa"].active_upgrade["remaining_days"],
            10,
        )
        for _ in range(10):
            self.world.advance_day()
        self.assertIn(
            "emergency_crisis_headquarters", country.emergency_measures
        )
        self.assertTrue(
            self.world.start_emergency_measure(
                "usa", "emergency_maritime_quarantine"
            )[0]
        )
        self.assertEqual(self.world.zombie_breach_interval(), 30)
        for _ in range(16):
            self.world.advance_day()
        self.assertEqual(self.world.zombie_breach_interval(), 40)
        self.assertLess(country.economy_report()["net"], 100)

    def test_international_evacuation_success_buffs_all_human_countries(self):
        self.world.new_game("uk", "zombie")
        country = self.world.countries["uk"]
        country.emergency_measures.update({
            "emergency_evacuation_corridors",
            "emergency_mobile_laboratories",
        })
        country.money = 10_000
        country.research_points = 100
        strengths_before = {
            country_id: self.world.countries[country_id].military_strength(
                self.world
            )
            for country_id in ("uk", "usa", "eu", "china", "zombies")
        }

        self.assertTrue(
            self.world.start_emergency_measure(
                "uk", "emergency_international_evacuation"
            )[0]
        )
        country.active_upgrade["remaining_days"] = 1
        with patch.object(self.world.rng, "random", return_value=0.49):
            self.world._advance_upgrade(country)

        self.assertEqual(self.world.international_evacuation_result, "success")
        for country_id in ("uk", "usa", "eu", "china"):
            self.assertAlmostEqual(
                self.world.countries[country_id].military_strength(self.world),
                strengths_before[country_id] * 1.1,
            )
        self.assertAlmostEqual(
            self.world.countries["zombies"].military_strength(self.world),
            strengths_before["zombies"],
        )
        self.assertFalse(
            self.world.start_emergency_measure(
                "usa", "emergency_international_evacuation"
            )[0]
        )

        with tempfile.TemporaryDirectory() as save_dir:
            saves = SaveSystem(save_dir)
            self.assertTrue(saves.save(self.world, 1)[0])
            loaded = World()
            self.assertTrue(saves.load(loaded, 1)[0])
        self.assertEqual(loaded.international_evacuation_result, "success")
        self.assertAlmostEqual(
            loaded.countries["usa"].military_strength(loaded),
            strengths_before["usa"] * 1.1,
        )

    def test_international_evacuation_failure_infects_seven_countries(self):
        self.world.new_game("usa", "zombie")
        self.world.rng.seed(7)
        country = self.world.countries["usa"]
        country.emergency_measures.update({
            "emergency_evacuation_corridors",
            "emergency_mobile_laboratories",
        })
        country.money = 10_000
        country.research_points = 100
        owners_before = {
            province.id: province.owner for province in self.world.provinces
        }

        self.assertTrue(
            self.world.start_emergency_measure(
                "usa", "emergency_international_evacuation"
            )[0]
        )
        country.active_upgrade["remaining_days"] = 1
        with patch.object(self.world.rng, "random", return_value=0.5):
            self.world._advance_upgrade(country)

        new_infections = [
            province for province in self.world.provinces
            if province.owner == "zombies"
            and owners_before[province.id] != "zombies"
        ]
        self.assertEqual(len(new_infections), 7)
        self.assertEqual(
            len({owners_before[province.id] for province in new_infections}), 7
        )
        self.assertEqual(self.world.international_evacuation_result, "failure")
        self.assertIn("7 регионах", self.world.events[0]["text"])

    def test_zombie_save_migrates_unsupported_ideologies(self):
        self.world.new_game("usa", "zombie")
        self.world.countries["usa"].ideology = "democracy"
        loaded = World()
        loaded.from_dict(self.world.to_dict())

        self.assertEqual(loaded.countries["usa"].ideology, "z_emergency")
        self.assertEqual(
            loaded.ideology_name_for("usa"),
            loaded.ideology_options_for("usa")["z_emergency"]["name"],
        )

    def test_zombie_diplomacy_rejects_relations_with_infected(self):
        self.world.new_game("usa", "zombie")
        usa = self.world.countries["usa"]
        money_before = usa.money
        relation_before = usa.relations["zombies"]

        self.assertFalse(self.world.diplomacy.improve("usa", "zombies")[0])
        self.assertFalse(self.world.diplomacy.form_alliance("usa", "zombies")[0])
        self.assertEqual(usa.money, money_before)
        self.assertEqual(usa.relations["zombies"], relation_before)

    def test_zombie_catastrophe_spreads_to_a_real_region(self):
        self.world.new_game("usa", "zombie")
        canada = self.world.countries["canada"]
        self.assertNotEqual(canada.id, self.world.player_id)
        owners_before = {
            province.id: province.owner for province in self.world.provinces
        }
        infected_before = self.world.province_count("zombies")

        def choose_country(items):
            return next(
                (item for item in items if getattr(item, "id", None) == "canada"),
                items[0],
            )

        with patch.object(
            self.world.rng, "choice", side_effect=choose_country
        ):
            self.assertTrue(self.world.event_system._spread_zombie_region())

        newly_infected = [
            province for province in self.world.provinces
            if province.owner == "zombies"
            and owners_before[province.id] != "zombies"
        ]
        self.assertEqual(len(newly_infected), 1)
        self.assertEqual(owners_before[newly_infected[0].id], "canada")
        self.assertEqual(
            self.world.province_count("zombies"), infected_before + 1
        )
        self.assertIn("Катастрофа", self.world.events[0]["text"])
        self.assertIn("регион потерян", self.world.events[0]["consequences"])

    def test_zombie_landings_do_not_prioritize_the_player_country(self):
        self.world.new_game("usa", "zombie")
        war = self.world.war_between("zombies", "usa")
        war.defenders.remove("canada")
        war.defenders.remove("usa")
        war.defenders[0:0] = ["canada", "usa"]
        fronts = [
            SimpleNamespace(owner=country_id)
            for country_id in ("canada", "usa", "uk")
        ]
        targets = []

        with (
            patch.object(self.world.rng, "shuffle", side_effect=lambda items: None),
            patch.object(
                self.world, "_front_regions", return_value=(fronts, "province")
            ),
            patch.object(
                self.world,
                "resolve_conflict",
                side_effect=lambda attacker, defender, **kwargs: (
                    targets.append(defender) or True,
                    "test operation",
                ),
            ),
        ):
            self.world.ai._resolve_war_operation(war)

        self.assertEqual(targets, ["canada"])

    def test_zombie_ai_operations_have_a_two_day_cooldown(self):
        self.world.new_game("usa", "zombie")
        war = self.world.war_between("zombies", "usa")
        operations = []

        def resolve(attacker, defender, **kwargs):
            operations.append((attacker, defender, kwargs["cooldown_days"]))
            return True, "test operation"

        with (
            patch.object(self.world.rng, "shuffle", side_effect=lambda items: None),
            patch.object(
                self.world, "_front_regions",
                return_value=([SimpleNamespace(owner="canada")], "province"),
            ),
            patch.object(self.world, "resolve_conflict", side_effect=resolve),
        ):
            self.world.ai._resolve_war_operation(war)
            self.world.day += 1
            self.world.ai._resolve_war_operation(war)
            self.assertEqual(len(operations), 1)
            self.world.day += 1
            self.world.ai._resolve_war_operation(war)

        self.assertEqual(len(operations), 2)
        self.assertEqual(operations[0], ("zombies", "canada", 2))
        self.assertEqual(operations[1], ("zombies", "canada", 2))

    def test_imported_labor_accident_infects_california(self):
        self.world.new_game("uk", "zombie")
        country = self.world.countries["uk"]
        country.emergency_measures.update({
            "emergency_crisis_headquarters",
            "emergency_medical_mobilization",
        })
        country.money = 10_000
        country.research_points = 100

        california = self.world.provinces_by_id["usa_admin1_USA-3521"]
        self.assertEqual(california.name, "California")
        self.assertEqual(california.owner, "usa")
        self.assertTrue(
            self.world.start_emergency_measure(
                "uk", "emergency_import_labor_force"
            )[0]
        )
        country.active_upgrade["remaining_days"] = 1
        with patch.object(self.world.rng, "random", return_value=0.59):
            self.world._advance_upgrade(country)

        self.assertEqual(california.owner, "zombies")
        self.assertIn("emergency_import_labor_force", country.emergency_measures)
        self.assertIn("Авария", self.world.events[0]["text"])
        self.assertEqual(self.world.countries["usa"].unrest, 8)

    def test_imported_labor_success_reduces_zombie_readiness_for_half_year(self):
        self.world.new_game("usa", "zombie")
        usa = self.world.countries["usa"]
        zombies = self.world.countries["zombies"]
        usa.emergency_measures.update({
            "emergency_crisis_headquarters",
            "emergency_medical_mobilization",
        })
        usa.money = 10_000
        usa.research_points = 100

        self.assertTrue(
            self.world.start_emergency_measure(
                "usa", "emergency_import_labor_force"
            )[0]
        )
        usa.active_upgrade["remaining_days"] = 1
        strength_before = zombies.military_strength(self.world)
        expected_expiry = self.world.absolute_day() + 183
        with patch.object(self.world.rng, "random", return_value=0.60):
            self.world._advance_upgrade(usa)

        self.assertEqual(
            self.world.zombie_readiness_penalty_until, expected_expiry
        )
        self.assertLess(zombies.military_strength(self.world), strength_before)

        with tempfile.TemporaryDirectory() as save_dir:
            saves = SaveSystem(save_dir)
            self.assertTrue(saves.save(self.world, 1)[0])
            loaded = World()
            self.assertTrue(saves.load(loaded, 1)[0])
        self.assertEqual(
            loaded.zombie_readiness_penalty_until, expected_expiry
        )
        loaded.day += 183
        strength_after_expiry = loaded.countries["zombies"].military_strength(
            loaded
        )
        loaded.zombie_readiness_penalty_until = 0
        self.assertAlmostEqual(
            strength_after_expiry,
            loaded.countries["zombies"].military_strength(loaded),
        )

    def test_zombie_survivor_armies_have_scenario_strength_penalty(self):
        self.world.new_game("usa", "zombie")
        survivor = self.world.countries["usa"]
        scenario_strength = survivor.military_strength(self.world)
        self.world.scenario_id = "modern"
        baseline_strength = survivor.military_strength(self.world)

        self.assertAlmostEqual(scenario_strength, baseline_strength * 0.9)

    def test_zombie_scenario_outcome_is_saved(self):
        self.world.new_game("uk", "zombie")
        self.world.scenario_outcome = "humans_win"
        with tempfile.TemporaryDirectory() as save_dir:
            saves = SaveSystem(save_dir)
            saves.save(self.world, 1)
            loaded = World()
            self.assertTrue(saves.load(loaded, 1)[0])
        self.assertEqual(loaded.scenario_id, "zombie")
        self.assertEqual(loaded.scenario_outcome, "humans_win")
        self.assertEqual(loaded.countries["uk"].tax_rate_cap, 20)
        self.assertEqual(loaded.war_between("uk", "zombies").objective["type"],
                         "zombie_outbreak")



if __name__ == "__main__":
    unittest.main()
