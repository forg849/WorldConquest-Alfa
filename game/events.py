import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import DATA_DIR
from .decision_events import DECISION_EVENTS


class EventSystem:
    EVENT_EFFECTS = {
        "money": ("money", 0, None, "Казна"),
        "stability": ("stability", 0, 100, "Стабильность"),
        "food": ("food", 0, 100, "Продовольствие"),
        "industry": ("industry", 0, 100, "Промышленность"),
        "development": ("development", 0, 100, "Развитие"),
        "economy_level": ("economy_level", 1, 10, "Уровень экономики"),
        "energy": ("energy", 0, 100, "Энергия"),
        "farms": ("farms", 0, None, "Фермы"),
        "power_plants": ("power_plants", 0, None, "Электростанции"),
        "military": ("military", 0, 100, "Военный потенциал"),
        "tax_rate": ("tax_rate", 5, 30, "Налоговая ставка"),
        "government_support": ("government_support", 0, 100, "Поддержка правительства"),
        "war_support": ("war_support", 0, 100, "Поддержка войны"),
        "army_readiness": ("army_readiness", 0, 100, "Боеготовность"),
        "unrest": ("unrest", 0, 100, "Недовольство"),
        "research_points": ("research_points", 0, None, "Очки исследований"),
        "political_power": ("political_power", 0, None, "Политическая сила"),
    }

    def __init__(self, world):
        self.world = world
        with open(os.path.join(DATA_DIR, "events.json"), "r", encoding="utf-8") as file:
            self.events = json.load(file)

    def try_random_event(self):
        if (
            self.world.scenario_id == "zombie"
            and not self.world.pending_modal_events
            and self.world.rng.random() < 0.012
            and self._trigger_decision_event()
        ):
            return
        spread_reduction = min(
            0.75,
            self.world.emergency_measure_global_bonuses().get(
                "outbreak_event_reduction", 0
            ),
        ) if self.world.scenario_id == "zombie" else 0
        if (
            self.world.scenario_id == "zombie"
            and self.world.rng.random() < 0.006 * (1 - spread_reduction)
            and self._spread_zombie_region()
        ):
            return
        if self.world.rng.random() >= 0.018:
            return
        candidates = [
            country for country in self.world.countries.values()
            if not country.is_defeated
        ]
        if not candidates:
            return
        player = self.world.countries.get(self.world.player_id)
        if player and not player.is_defeated and self.world.rng.random() < 0.65:
            country = self.world.countries[self.world.player_id]
        else:
            other_candidates = [
                item for item in candidates if item.id != self.world.player_id
            ]
            country = self.world.rng.choice(other_candidates or candidates)
        event = self.world.rng.choice(self.events)
        consequences = self.apply_event(country, event)
        is_player = country.id == self.world.player_id
        self.world.add_event(
            f"{country.name}: {event['name']} — {event['description']}",
            notify=is_player,
            modal=is_player,
            consequences=consequences,
        )

    def _trigger_decision_event(self):
        available = [
            event for event in DECISION_EVENTS
            if event["id"] not in self.world.decision_events_seen
            and (
                not event.get("country")
                or (
                    event["country"] in self.world.countries
                    and not self.world.countries[event["country"]].is_defeated
                    and self.world.province_count(event["country"]) > 0
                )
            )
        ]
        if not available:
            return False
        event = self.world.rng.choice(available)
        if event.get("country"):
            country_id = event["country"]
        else:
            candidates = [
                country.id for country in self.world.countries.values()
                if country.id != "zombies" and not country.is_defeated
                and self.world.province_count(country.id) > 0
            ]
            if not candidates:
                return False
            country_id = self.world.rng.choice(candidates)
        return self.world.present_decision_event(event["id"], country_id)

    def _spread_zombie_region(self):
        countries = [
            country for country in self.world.countries.values()
            if country.id != "zombies"
            and not country.is_defeated
            and self.world.province_count(country.id) > 0
        ]
        if not countries:
            return False
        owner = self.world.rng.choice(countries)
        candidates = [
            province for province in self.world.provinces
            if province.owner == owner.id
        ]
        if not candidates:
            return False

        core_reduction = min(
            1.0,
            self.world.emergency_measure_global_bonuses().get(
                "core_outbreak_reduction", 0
            ),
        )
        if core_reduction and self.world.rng.random() < core_reduction:
            core_capitals = {
                self.world.capital_provinces[country_id]
                for country_id in self.world._scenario_settings().get(
                    "selectable_countries", ()
                )
                if country_id in self.world.capital_provinces
            }
            protected = [
                province for province in candidates
                if province.id not in core_capitals
            ]
            if protected:
                candidates = protected

        province = self.world.rng.choice(candidates)
        owner = self.world.countries[province.owner]
        owner.unrest = min(100, owner.unrest + 4)
        owner.stability = max(0, owner.stability - 2)
        self.world._set_region_owner(
            province, "zombies", kind="province", occupied=False
        )
        if self.world.province_count(owner.id) == 0:
            self.world._handle_country_elimination(owner.id)
        is_player = owner.id == self.world.player_id
        cause = self.world.rng.choice((
            "землетрясения", "пожара", "аварии на карантинном рубеже",
            "разрушения укрытия",
        ))
        self.world.add_event(
            f"Катастрофа: после {cause} появились заражённые в регионе "
            f"«{province.name}». Контроль перешёл к заражённым.",
            notify=is_player,
            modal=is_player and not owner.is_defeated,
            consequences=(
                f"{owner.name}: регион потерян, недовольство +4%, "
                "стабильность −2."
            ),
        )
        self.world._update_zombie_scenario_outcome()
        return True

    def apply_event(self, country, event):
        effects = event.get("effects", {})
        unknown_effects = set(effects) - set(self.EVENT_EFFECTS) - {"relations"}
        if unknown_effects:
            raise ValueError(
                f"Unknown effects for event {event.get('id', '<unknown>')}: "
                f"{', '.join(sorted(unknown_effects))}"
            )

        region_count = self.world.province_count(country.id)
        active_wars = len(self.world.wars_for(country.id))
        income_before = country.economy_report(
            region_count, active_wars,
            zombie_scenario=self.world.scenario_id == "zombie",
        )["net"]
        before = {
            attribute: getattr(country, attribute)
            for attribute, _, _, _ in self.EVENT_EFFECTS.values()
        }
        for effect, amount in effects.items():
            if effect == "relations":
                continue
            attribute, minimum, maximum, _ = self.EVENT_EFFECTS[effect]
            if effect == "tax_rate":
                maximum = country.tax_rate_cap
            value = getattr(country, attribute) + amount
            if minimum is not None:
                value = max(minimum, value)
            if maximum is not None:
                value = min(maximum, value)
            setattr(country, attribute, value)

        consequences = []
        for effect, amount in effects.items():
            if effect == "relations":
                continue
            attribute, _, _, label = self.EVENT_EFFECTS[effect]
            change = getattr(country, attribute) - before[attribute]
            if change:
                consequences.append(
                    f"{label} {self._format_change(change)}"
                )

        income_after = country.economy_report(
            self.world.province_count(country.id),
            len(self.world.wars_for(country.id)),
            zombie_scenario=self.world.scenario_id == "zombie",
        )["net"]
        income_change = income_after - income_before
        if abs(income_change) >= 0.05:
            consequences.insert(
                1 if consequences and consequences[0].startswith("Казна ") else 0,
                f"Доход/день {self._format_change(income_change)}",
            )

        relation_change = effects.get("relations", 0)
        if relation_change:
            partners = [
                other for other in self.world.countries.values()
                if other.id != country.id
                and not other.is_defeated
                and not (
                    self.world.scenario_id == "zombie"
                    and (country.id == "zombies" or other.id == "zombies")
                )
                and (
                    country.relations.get(other.id, 0) < 100
                    if relation_change > 0
                    else country.relations.get(other.id, 0) > -100
                )
            ]
            if partners:
                partner = self.world.rng.choice(partners)
                previous = country.relations.get(partner.id, 0)
                updated = max(-100, min(100, previous + relation_change))
                actual_change = updated - previous
                country.relations[partner.id] = updated
                partner.relations[country.id] = max(
                    -100,
                    min(100, partner.relations.get(country.id, 0) + actual_change),
                )
                if actual_change:
                    consequences.append(
                        f"Отношения с {partner.name} "
                        f"{self._format_change(actual_change)}"
                    )

        return " · ".join(consequences) or "Заметных изменений параметров нет"

    @staticmethod
    def _format_change(value):
        rounded = round(value, 1)
        formatted = str(int(rounded)) if rounded.is_integer() else f"{rounded:.1f}"
        if rounded > 0:
            return f"+{formatted}"
        return formatted.replace("-", "−")
