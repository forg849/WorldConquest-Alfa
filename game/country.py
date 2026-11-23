import random
from .ideology import ideology_bonuses, migrate_ideology
from .political_courses import political_course_bonuses
from .technology import technology_bonuses
from .emergency_measures import emergency_measure_bonuses


class Country:
    INVESTMENT_COSTS = {
        "industry": 500,
        "infrastructure": 420,
        "military": 520,
        "farms": 380,
        "power": 460,
        "economy": 900,
    }

    def __init__(self, data):
        self.id = data["id"]
        self.name = data["name"]
        self.color = tuple(data["color"])
        self.population = data["population"]
        self.money = data["money"]
        self.economy_level = data.get("economy_level", 1)
        self.stability = data.get("stability", 70)
        self.development = data.get("development", 50)
        self.difficulty = data.get("difficulty", "Normal")
        self.strategy = data.get("strategy", "balanced")
        self.food = data["food"]
        self.industry = data["industry"]
        self.energy = data["energy"]
        population_millions = self.population / 1_000_000
        self.farms = data.get("farms", max(4, round(population_millions * 0.25)))
        self.power_plants = data.get("power_plants", max(4, round(self.industry * 0.32)))
        self.military = data.get("military", 35 + self.economy_level * 4)
        self.army_size = data.get(
            "army_size",
            max(1000, int(self.population * (0.0015 + self.military / 100000))),
        )
        self.army_readiness = data.get("army_readiness", 75)
        self.tax_rate = data.get("tax_rate", 12)
        self.tax_rate_cap = int(data.get("tax_rate_cap", 30))
        self.research_points = data.get("research_points", 2.0)
        self.techs = set(data.get("techs", []))
        self.ideology = migrate_ideology(
            self.id, data.get("ideology", "democracy")
        )
        self.ideology_upgrades = set(data.get("ideology_upgrades", []))
        self.leadership_term = int(data.get("leadership_term", 1))
        default_title = {
            "communism": "Председатель правительства",
            "fascism": "Национальный лидер",
            "monarchy": "Монарх",
            "democracy": "Президент",
            "z_emergency": "Чрезвычайный совет",
            "z_science": "Научный совет",
            "z_defense": "Командование обороны",
            "z_horde": "Коллективный разум",
        }[self.ideology]
        self.leader = data.get(
            "leader", f"{default_title} №{self.leadership_term}"
        )
        self.political_policies = set(data.get("political_policies", []))
        self.emergency_measures = set(data.get("emergency_measures", []))
        self.decision_modifiers = dict(data.get("decision_modifiers", {}))
        self.active_upgrade = data.get("active_upgrade")
        self.active_political_course = data.get("active_political_course")
        self.pacts = data.get("pacts", {})
        self.treaties = data.get("treaties", {})
        self.political_power = data.get("political_power", 80.0)
        self.government_support = data.get("government_support", 58)
        self.unrest = data.get("unrest", 0.0)
        self.rebellion_cooldown_until = data.get("rebellion_cooldown_until", 0)
        self.unrest_relief_count = data.get("unrest_relief_count", 0)
        self.investment_levels = {
            kind: int(level)
            for kind, level in data.get("investment_levels", {}).items()
        }
        self.recovery_ready_day = data.get("recovery_ready_day", 0)
        self.war_support = data.get("war_support", 65)
        self.war_exhaustion = data.get("war_exhaustion", 0)
        self.is_defeated = data.get("is_defeated", False)
        self.battle_cooldowns = data.get("battle_cooldowns", {})
        self.recruitment_ready_day = data.get("recruitment_ready_day", 0)
        self.relations = {}
        self.alliance = None
        self.wars = set()
        self.truce_until = {}
        self.is_player = False

    def region_count(self, world):
        counts = getattr(world, "region_counts", None)
        if counts is not None:
            return counts.get(self.id, 0)
        return sum(1 for region in world.regions if region.owner == self.id)

    def military_strength(self, world):
        ideology_effects = ideology_bonuses(self.ideology, self.ideology_upgrades)
        technology_effects = technology_bonuses(self.techs)
        policy_effects = political_course_bonuses(self.political_policies)
        emergency_effects = emergency_measure_bonuses(self.emergency_measures)
        treaty_effects = self.treaty_bonuses()
        if world.scenario_id == "zombie" and self.id == "zombies":
            regions = world.province_count(self.id)
            regions = min(regions, 9) + max(0, regions - 9) * 0.1
        else:
            regions = self.region_count(world)
        strength = 20 + regions * 4 + self.military * 1.2 + self.industry * 0.2
        strength *= (
            1 + ideology_effects.get("military", 0)
            + technology_effects.get("military", 0)
            + policy_effects.get("military", 0)
            + emergency_effects.get("military", 0)
            + treaty_effects.get("military", 0)
        )
        if "military_logistics" in self.techs:
            strength *= 1.12
        if "military_doctrine" in self.techs:
            strength *= 1.08
        if "tactics" in self.techs:
            strength *= 1.08
        if "modern_arms" in self.techs:
            strength *= 1.15
        strength *= 1 - self.war_exhaustion / 400
        expected_army = max(1, self.population * 0.002)
        strength *= min(1.25, max(0.55, 0.8 + self.army_size / expected_army * 0.25))
        effective_readiness = self.army_readiness
        if (
            world.scenario_id == "zombie"
            and self.id == "zombies"
            and world.absolute_day() < world.zombie_readiness_penalty_until
        ):
            effective_readiness = max(0, effective_readiness - 10)
        strength *= 0.65 + effective_readiness * 0.0035
        strength *= 1 + self.decision_modifiers.get("military_strength", 0)
        if self.energy < 15:
            strength *= 0.8
        if world.scenario_id == "zombie" and self.id != "zombies":
            strength *= 0.9
        if (
            world.scenario_id == "zombie"
            and self.id != "zombies"
            and world.international_evacuation_result == "success"
        ):
            strength *= 1.1
        return strength * (0.55 + self.war_support / 220)

    def daily_income(self):
        return self.economy_report()["net"]

    def investment_cost(self, kind):
        if kind not in self.INVESTMENT_COSTS:
            raise ValueError(f"Unknown investment: {kind}")
        level = self.investment_levels.get(kind, 0)
        return round(self.INVESTMENT_COSTS[kind] * (1 + level * 0.35))

    def invest(self, kind):
        if kind not in self.INVESTMENT_COSTS:
            return False, "Неизвестный тип вложения"
        limits = {
            "industry": self.industry >= 100,
            "infrastructure": self.development >= 100,
            "military": self.military >= 100,
            "economy": self.economy_level >= 10,
        }
        if limits.get(kind, False):
            return False, "Уровень уже максимальный"
        cost = self.investment_cost(kind)
        if self.money < cost:
            return False, "Недостаточно средств"
        self.money -= cost
        if kind == "industry":
            self.industry = min(100, self.industry + 8)
        elif kind == "infrastructure":
            self.development = min(100, self.development + 6)
        elif kind == "military":
            self.military = min(100, self.military + 7)
        elif kind == "farms":
            self.farms += 5
        elif kind == "power":
            self.power_plants += 3
        elif kind == "economy":
            self.economy_level = min(10, self.economy_level + 1)
        self.investment_levels[kind] = self.investment_levels.get(kind, 0) + 1
        messages = {
            "industry": f"Производственный комплекс построен. Промышленность: {self.industry:.0f}",
            "infrastructure": f"Инфраструктура развита до {self.development:.0f}",
            "military": f"Армия усилена до {self.military:.0f}",
            "farms": f"Фермерские хозяйства: {self.farms}",
            "power": f"Электростанции: {self.power_plants}",
            "economy": f"Уровень экономики: {self.economy_level}/10",
        }
        return True, f"{messages[kind]} (вложено ${cost})"

    def economy_report(
        self, region_count=1, active_wars=0, zombie_scenario=False
    ):
        ideology_effects = ideology_bonuses(self.ideology, self.ideology_upgrades)
        technology_effects = technology_bonuses(self.techs)
        policy_effects = political_course_bonuses(self.political_policies)
        emergency_effects = emergency_measure_bonuses(self.emergency_measures)
        treaty_effects = self.treaty_bonuses()
        population_millions = self.population / 1_000_000
        output = (
            30 + self.economy_level * 18 + self.industry * 0.9
            + self.development * 0.35 + population_millions * 0.45
            + region_count * 3.4
        )
        if "administration" in self.techs:
            output *= 1.08
        if "trade_network" in self.techs:
            output *= 1.05
        if "industrial_trade" in self.techs:
            output *= 1.08
        if "global_market" in self.techs:
            output *= 1.12
        if "automation" in self.techs:
            output *= 1.07
        output *= (
            1 + ideology_effects.get("production", 0)
            + technology_effects.get("production", 0)
            + policy_effects.get("production", 0)
            + emergency_effects.get("production", 0)
            + treaty_effects.get("production", 0)
        )
        unrest_output_penalty = 0.00075 if zombie_scenario else 0.0015
        output *= max(
            0.55,
            1 - self.war_exhaustion * 0.00025
            - self.unrest * unrest_output_penalty,
        )
        taxes = output * self.tax_rate / 100
        if "tax_reform" in self.techs:
            taxes *= 1.1
        taxes *= (
            1 + ideology_effects.get("taxes", 0)
            + technology_effects.get("taxes", 0)
            + policy_effects.get("taxes", 0)
            + emergency_effects.get("taxes", 0)
            + treaty_effects.get("taxes", 0)
        )
        unrest_tax_penalty = 0.00125 if zombie_scenario else 0.0025
        taxes *= max(0.65, 1 - self.unrest * unrest_tax_penalty)
        military_spending = self.military * 0.08 + max(0, active_wars) * (
            4 + self.military * 0.025
        )
        upkeep = (
            7 + population_millions * 0.025 + military_spending
            + region_count * 0.22 + self.industry * 0.015
            + self.development * 0.02 + self.economy_level * 0.25
        )
        if self.food < 15 or self.energy < 15:
            taxes *= 0.8
        upkeep *= max(
            0.5,
            1 + ideology_effects.get("upkeep", 0)
            + technology_effects.get("upkeep", 0)
            + policy_effects.get("upkeep", 0)
            + emergency_effects.get("upkeep", 0)
            + treaty_effects.get("upkeep", 0),
        )
        food_balance = (
            15 + self.development * 0.10 + self.farms * 1.8
            - population_millions * 0.45
        ) / 40
        energy_balance = (
            8 + self.power_plants * 1.8 - self.industry * 0.28
            - population_millions * 0.05
        ) / 40
        research = 0.04 + self.development / 100 * 0.16
        unrest_research_penalty = 0.001 if zombie_scenario else 0.002
        research *= max(
            0.3,
            1 - self.war_exhaustion * 0.0015
            - self.unrest * unrest_research_penalty,
        )
        if "education" in self.techs:
            research *= 1.5
        research *= (
            1 + ideology_effects.get("research", 0)
            + technology_effects.get("research", 0)
            + policy_effects.get("research", 0)
            + emergency_effects.get("research", 0)
            + treaty_effects.get("research", 0)
        )
        political_power = (
            0.12 + self.stability * 0.0035 + self.government_support * 0.0025
        ) * (
            1 + ideology_effects.get("political_power", 0)
            + technology_effects.get("political_power", 0)
            + policy_effects.get("political_power", 0)
            + emergency_effects.get("political_power", 0)
            + treaty_effects.get("political_power", 0)
        )
        return {
            "output": output,
            "taxes": taxes,
            "upkeep": upkeep,
            "military_spending": military_spending,
            "net": taxes - upkeep,
            "food_balance": food_balance,
            "energy_balance": energy_balance,
            "research": research,
            "political_power": political_power,
        }

    def advance_day(
        self, rng=None, region_count=1, active_wars=0, zombie_scenario=False
    ):
        rng = rng or random
        report = self.economy_report(
            region_count, active_wars, zombie_scenario
        )
        self.money += report["net"]
        self.food = max(0, min(100, self.food + report["food_balance"]))
        self.energy = max(0, min(100, self.energy + report["energy_balance"]))
        self.research_points += report["research"]
        self.political_power += report["political_power"]
        ideology_effects = ideology_bonuses(self.ideology, self.ideology_upgrades)
        technology_effects = technology_bonuses(self.techs)
        policy_effects = political_course_bonuses(self.political_policies)
        emergency_effects = emergency_measure_bonuses(self.emergency_measures)
        treaty_effects = self.treaty_bonuses()
        population_growth = (
            1.00002 + self.stability * 0.0000002
            + technology_effects.get("population_growth", 0)
        )
        if "public_health" in self.techs:
            population_growth += 0.00001
        self.population = max(100000, int(self.population * population_growth))
        if self.food < 20:
            self.stability = max(0, self.stability - 0.12)
        elif self.food > 60 and self.government_support < 100 and rng.random() < 0.04:
            self.stability = min(100, self.stability + 0.2)
        if self.energy < 15:
            self.stability = max(0, self.stability - 0.08)
        self.stability = max(
            0, min(
                100, self.stability + ideology_effects.get("stability", 0)
                + technology_effects.get("stability", 0)
                + policy_effects.get("stability", 0)
                + emergency_effects.get("stability", 0)
                + treaty_effects.get("stability", 0)
            )
        )
        self.government_support = max(
            0, min(
                100, self.government_support + ideology_effects.get("support", 0)
                + technology_effects.get("support", 0)
                + policy_effects.get("support", 0)
                + emergency_effects.get("support", 0)
                + treaty_effects.get("support", 0)
            )
        )
        if self.wars:
            self.war_support = max(
                0, min(
                    100, self.war_support + ideology_effects.get("war_support", 0)
                    + technology_effects.get("war_support", 0)
                    + policy_effects.get("war_support", 0)
                    + emergency_effects.get("war_support", 0)
                    + treaty_effects.get("war_support", 0)
                )
            )
        tax_pressure = max(0, self.tax_rate - 12)
        if tax_pressure:
            self.stability = max(
                0, self.stability - max(0, self.tax_rate - 14) * 0.012
            )
            self.government_support = max(
                0, self.government_support - max(0, self.tax_rate - 14) * 0.01
            )
        elif self.stability >= 65:
            self.government_support = min(100, self.government_support + 0.04)

        if self.wars and self.war_exhaustion > 35:
            fatigue = self.war_exhaustion - 35
            self.stability = max(0, self.stability - fatigue * 0.0003)
            self.government_support = max(
                0, self.government_support - fatigue * 0.0002
            )

        if self.unrest > 60:
            pressure = self.unrest - 60
            self.stability = max(0, self.stability - pressure * 0.003)
            self.government_support = max(0, self.government_support - pressure * 0.002)

        unrest_change = (
            tax_pressure * 0.025
            + max(0, 50 - self.government_support) * 0.005
            + max(0, 45 - self.stability) * 0.01
            + max(0, self.war_exhaustion - 25) * (0.0005 if self.wars else 0)
            + max(0, 30 - self.food) * 0.012
            + max(0, 20 - self.energy) * 0.01
            + ideology_effects.get("unrest", 0)
            + technology_effects.get("unrest", 0)
            + policy_effects.get("unrest", 0)
            + emergency_effects.get("unrest", 0)
            + treaty_effects.get("unrest", 0)
        )
        if (
            not self.wars and self.stability >= 60
            and self.tax_rate <= 15 and self.food >= 30
        ):
            unrest_change -= 0.18
        unrest_change *= max(
            0, 1 + self.decision_modifiers.get("unrest_growth", 0)
        )
        self.unrest = max(0, min(100, self.unrest + unrest_change))

        self.war_exhaustion = max(
            0, self.war_exhaustion - (0.03 if self.wars else 0.2)
        )
        if self.war_support < 100 and not self.wars:
            self.war_support = min(100, self.war_support + 0.08)
        if not self.wars:
            self.army_readiness = max(
                0, min(
                    100, self.army_readiness + 0.12
                    + ideology_effects.get("readiness", 0)
                    + technology_effects.get("readiness", 0)
                    + emergency_effects.get("readiness", 0)
                )
            )

    def set_tax_rate(self, adjustment):
        self.tax_rate = max(5, min(self.tax_rate_cap, self.tax_rate + adjustment))
        return self.tax_rate

    def treaty_bonuses(self):
        bonuses = {}
        for treaty in self.treaties.values():
            for key, value in treaty.get("bonuses", {}).items():
                bonuses[key] = bonuses.get(key, 0) + value
        return bonuses

    def to_dict(self):
        return {
            "id": self.id, "name": self.name, "color": list(self.color),
            "population": self.population, "money": round(self.money, 2),
            "economy_level": self.economy_level, "stability": self.stability,
            "development": self.development, "difficulty": self.difficulty,
            "strategy": self.strategy, "food": self.food,
            "industry": self.industry, "energy": self.energy,
            "farms": self.farms, "power_plants": self.power_plants,
            "military": self.military, "tax_rate": self.tax_rate,
            "tax_rate_cap": self.tax_rate_cap,
            "army_size": self.army_size, "army_readiness": self.army_readiness,
            "research_points": round(self.research_points, 2),
            "political_power": round(self.political_power, 2),
            "techs": sorted(self.techs), "ideology": self.ideology,
            "ideology_upgrades": sorted(self.ideology_upgrades),
            "leader": self.leader,
            "leadership_term": self.leadership_term,
            "political_policies": sorted(self.political_policies),
            "emergency_measures": sorted(self.emergency_measures),
            "decision_modifiers": self.decision_modifiers,
            "active_upgrade": self.active_upgrade,
            "active_political_course": self.active_political_course,
            "pacts": self.pacts,
            "treaties": self.treaties,
            "government_support": self.government_support,
            "unrest": self.unrest,
            "rebellion_cooldown_until": self.rebellion_cooldown_until,
            "unrest_relief_count": self.unrest_relief_count,
            "investment_levels": self.investment_levels,
            "recovery_ready_day": self.recovery_ready_day,
            "is_defeated": self.is_defeated,
            "war_support": self.war_support, "war_exhaustion": self.war_exhaustion,
            "battle_cooldowns": self.battle_cooldowns,
            "recruitment_ready_day": self.recruitment_ready_day,
            "relations": self.relations, "alliance": self.alliance,
            "wars": list(self.wars), "truce_until": self.truce_until,
            "is_player": self.is_player,
        }

    @classmethod
    def from_dict(cls, data):
        country = cls(data)
        country.relations = data.get("relations", {})
        country.alliance = data.get("alliance")
        country.wars = set(data.get("wars", []))
        country.truce_until = data.get("truce_until", {})
        country.is_player = data.get("is_player", False)
        return country

