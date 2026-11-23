from .ideology import ideology_branch_locked
from .political_courses import course_available
from .technology import technology_branch_locked


class AISystem:
    def __init__(self, world):
        self.world = world

    def update(self):
        ids = [
            country_id for country_id, country in self.world.countries.items()
            if country_id != self.world.player_id and not country.is_defeated
        ]
        for country_id in ids:
            country = self.world.countries[country_id]
            rng = self.world.rng
            if country.wars:
                if country.war_support <= 45 and country.money >= 300:
                    self.world.mobilize(country_id)
                if self.world.can_recruit(country_id):
                    self.world.recruit(country_id)
                if self.world.scenario_id != "zombie":
                    continue
                self._recover_country(country_id)
            else:
                self._recover_country(country_id)
            course_chance = (
                0.05 if self.world.scenario_id == "zombie"
                and country_id == "zombies" else 0.025
            )
            if country.political_power >= 120 and rng.random() < course_chance:
                options = [
                    course for course in self.world.political_courses_for(country_id)
                    if course_available(self.world, country, course["id"])
                    and country.money >= course["cost"]
                    and country.political_power >= course["political_power"]
                    and not (
                        course.get("partner") == self.world.player_id
                        or country_id == self.world.player_id
                    )
                ]
                if options:
                    priorities = {
                        "expansion": ("military", "production"),
                        "industrial": ("production", "taxes"),
                        "resource": ("taxes", "production"),
                        "balanced": ("stability", "support", "research"),
                    }.get(country.strategy, ("stability", "production"))
                    course = max(
                        options,
                        key=lambda item: sum(
                            item["bonuses"].get(key, 0) for key in priorities
                        ),
                    )
                    self.world.start_political_course(country_id, course["id"])
            if rng.random() < 0.008:
                if country.money >= 380:
                    kind = {
                        "industrial": "industry",
                        "resource": "farms",
                        "expansion": "military",
                    }.get(country.strategy, "infrastructure")
                    country.invest(kind)
            research_chance = (
                0.03 if self.world.scenario_id == "zombie"
                and country_id == "zombies" else 0.006
            )
            if rng.random() < research_chance:
                technology_tree = self.world.technology_tree_for(country_id)
                options = [
                    node for node in technology_tree
                    if node["id"] not in country.techs
                    and all(required in country.techs for required in node["requires"])
                    and not technology_branch_locked(
                        country.techs, node["id"], technology_tree
                    )
                ]
                if options:
                    self.world.research_technology(country_id, rng.choice(options)["id"])
            ideology_chance = (
                0.03 if self.world.scenario_id == "zombie"
                and country_id == "zombies" else 0.012
            )
            if country.political_power >= 35 and rng.random() < ideology_chance:
                self._develop_ideology(country_id)

            if not country.wars and rng.random() < 0.025:
                self._conduct_diplomacy(country_id, ids)

            if country.wars:
                continue
            war_chance = {
                "expansion": 0.0035,
                "balanced": 0.0012,
                "resource": 0.0007,
                "industrial": 0.0007,
                "naval": 0.0007,
            }.get(country.strategy, 0.0007)
            if rng.random() < war_chance:
                target_id = self._choose_war_target(country_id, self.world.countries)
                if target_id:
                    self.world.declare_war(country_id, target_id)

        for war in self.world.active_wars():
            if self._resolve_ai_war_end(war):
                continue
            if (
                war.peace_offer
                and war.peace_offer["recipient"] != self.world.player_id
            ):
                self.world.respond_ai_peace_offer(war)
                if war.status != "active":
                    continue

            losing_side = war.defenders if war.attacker_score >= war.defender_score else war.attackers
            pressured = [
                self.world.countries[country_id]
                for country_id in losing_side
                if country_id != self.world.player_id
                and (
                    self.world.countries[country_id].war_exhaustion >= 68
                    or self.world.countries[country_id].war_support <= 15
                )
            ]
            if pressured and self.world.rng.random() < 0.2:
                offered = self.world.propose_ai_peace(war)
                if offered[0]:
                    continue

            self._resolve_war_operation(war)
            if self.world.pending_modal_events:
                break

    def _resolve_ai_war_end(self, war):
        if war.objective.get("type") == "zombie_outbreak":
            return False
        if self.world.player_id in war.attackers + war.defenders:
            return False
        absolute_day = self.world.absolute_day()
        winners, losers = self.world._winning_sides(war)
        victor_id = max(
            winners,
            key=lambda item: self.world.countries[item].military_strength(self.world),
        )
        for loser_id in losers:
            if self.world.can_capitulate(war, victor_id):
                self.world.settle_war(victor_id, loser_id, "capitulation")
                return True

        stalled_days = absolute_day - war.last_progress_day
        if stalled_days < 240:
            return False
        self.world.settle_war(war.attackers[0], war.defenders[0], "status_quo")
        return True

    def _recover_country(self, country_id):
        country = self.world.countries[country_id]
        absolute_day = self.world.absolute_day()
        if (
            not country.recovery_ready_day
            or absolute_day < country.recovery_ready_day
        ):
            return False

        target_army = max(
            1000,
            int(country.population * (0.0015 + country.military / 100000)),
        )
        if (
            country.army_size < target_army * 0.9
            and self.world.can_recruit(country_id)
        ):
            self.world.recruit(country_id)
            country.recovery_ready_day = absolute_day + 60
            return True

        relief_cost = self.world.unrest_relief_cost(country_id)
        if country.unrest >= 50 and country.money >= relief_cost:
            self.world.reduce_unrest(country_id)
            country.recovery_ready_day = absolute_day + 45
            return True

        if country.stability < 48 and country.money >= 800:
            country.money -= 800
            country.stability = min(100, country.stability + 6)
            country.government_support = min(
                100, country.government_support + 4
            )
            country.unrest = max(0, country.unrest - 3)
            country.recovery_ready_day = absolute_day + 45
            return True

        investments = (
            ("farms", country.food < 35),
            ("power", country.energy < 35),
            ("economy", country.economy_level < 6),
            ("industry", country.industry < 70),
            ("infrastructure", country.development < 65),
        )
        for kind, needed in investments:
            if needed and country.money >= country.investment_cost(kind):
                country.invest(kind)
                country.recovery_ready_day = absolute_day + 45
                return True
        return False

    def _develop_ideology(self, country_id):
        country = self.world.countries[country_id]
        priorities = {
            "expansion": ("military", "readiness", "war_support"),
            "naval": ("military", "production", "readiness"),
            "industrial": ("production", "industry", "taxes"),
            "resource": ("production", "taxes", "political_power"),
            "balanced": ("stability", "support", "research", "political_power"),
        }.get(country.strategy, ("stability", "support", "research"))
        options = [
            node for node in self.world.ideology_tree_for(country_id)
            if node["id"] not in country.ideology_upgrades
            and country.political_power >= node["cost"]
            and all(
                required in country.ideology_upgrades
                for required in node["requires"]
            )
            and not ideology_branch_locked(
                country.ideology_upgrades, country.ideology, node["id"]
            )
        ]
        if not options:
            return False
        node = max(
            options,
            key=lambda item: (
                sum(item["bonuses"].get(key, 0) for key in priorities),
                -item["cost"],
            ),
        )
        return self.world.develop_ideology(country_id, node["id"])[0]

    def _resolve_war_operation(self, war):
        absolute_day = self.world.absolute_day()
        zombie_outbreak = war.objective.get("type") == "zombie_outbreak"
        operation_interval = 2 if zombie_outbreak else 3
        if (
            war.last_ai_operation_day is not None
            and absolute_day - war.last_ai_operation_day < operation_interval
        ):
            return

        player_side = war.side(self.world.player_id)
        eligible = [
            country_id
            for side in (war.attackers, war.defenders)
            for country_id in side
            if country_id != self.world.player_id
            and self.world.countries[country_id].money >= 120
            and (
                zombie_outbreak
                or player_side is None
                or war.side(country_id) != player_side
            )
        ]
        self.world.rng.shuffle(eligible)
        for country_id in eligible:
            country = self.world.countries[country_id]
            fronts, _ = self.world._front_regions(
                [country_id], war.enemies(country_id)
            )
            if not fronts:
                continue
            front_owners = {region.owner for region in fronts}
            enemies = [
                enemy_id for enemy_id in war.enemies(country_id)
                if enemy_id in front_owners
                and absolute_day >= country.battle_cooldowns.get(enemy_id, 0)
            ]
            if zombie_outbreak:
                self.world.rng.shuffle(enemies)
            elif self.world.player_id in enemies:
                enemies.remove(self.world.player_id)
                enemies.insert(0, self.world.player_id)
            for enemy_id in enemies:
                success, _ = self.world.resolve_conflict(
                    country_id, enemy_id,
                    cooldown_days=(
                        2 if zombie_outbreak and country_id == "zombies" else 3
                    ),
                )
                if success:
                    war.last_ai_operation_day = absolute_day
                    return

    def _conduct_diplomacy(self, country_id, candidate_ids):
        country = self.world.countries[country_id]
        partners = [
            self.world.countries[other_id]
            for other_id in candidate_ids
            if other_id != country_id
            and not self.world.countries[other_id].is_defeated
            and not country.wars
            and not self.world.countries[other_id].wars
            and other_id not in country.truce_until
            and country.id not in self.world.countries[other_id].truce_until
        ]
        if not partners:
            return False

        partners.sort(
            key=lambda partner: (
                country.relations.get(partner.id, 0),
                partner.relations.get(country_id, 0),
            ),
            reverse=True,
        )
        for partner in partners:
            if (
                not country.alliance
                and not partner.alliance
                and country.relations.get(partner.id, 0) >= 45
                and partner.relations.get(country_id, 0) >= 20
                and country_id != self.world.player_id
                and partner.id != self.world.player_id
            ):
                return self.world.diplomacy.form_alliance(country_id, partner.id)[0]

        partner = next(
            (
                item for item in partners
                if country.relations.get(item.id, 0) < 100
            ),
            None,
        )
        if partner:
            return self.world.diplomacy.improve(country_id, partner.id)[0]
        return False

    def _choose_war_target(self, country_id, candidates):
        country = self.world.countries[country_id]
        if (
            country.is_defeated or country.wars or country.money < 1200 or country.stability < 55
            or country.war_support < 55 or country.military < 35
        ):
            return None
        neighbors = self.world.country_neighbors.get(country_id, ())
        targets = []
        strength = country.military_strength(self.world)
        relation_limit, strength_ratio = {
            "expansion": (25, 0.82),
            "balanced": (-5, 1.0),
            "resource": (-10, 1.05),
            "industrial": (-10, 1.05),
            "naval": (-8, 1.05),
        }.get(country.strategy, (-10, 1.05))
        for target_id in neighbors:
            if target_id not in candidates or target_id == country_id:
                continue
            target = self.world.countries[target_id]
            relation = country.relations.get(target_id, 0)
            if (
                target.is_defeated or target.wars or relation > relation_limit
                or target_id in country.truce_until
                or target_id in target.truce_until
                or target.alliance == country_id
            ):
                continue
            if strength < target.military_strength(self.world) * strength_ratio:
                continue
            targets.append((relation, target_id))
        return min(targets)[1] if targets else None
