class Diplomacy:
    def __init__(self, world):
        self.world = world

    def get_relation(self, a, b):
        if a == b:
            return 100
        return self.world.countries[a].relations.get(b, 0)

    def improve(self, a, b):
        if a == b:
            return False, "Нельзя улучшить отношения с самим собой"
        if self._incompatible_zombie_diplomacy(a, b):
            return False, "С заражёнными нельзя вести дипломатические переговоры"
        ca, cb = self.world.countries[a], self.world.countries[b]
        cost = 80
        if ca.relations.get(b, 0) >= 100:
            return False, "Отношения уже на максимуме"
        if ca.money < cost:
            return False, "Недостаточно средств"
        ca.money -= cost
        ca.relations[b] = min(100, ca.relations.get(b, 0) + 12)
        cb.relations[a] = min(100, cb.relations.get(a, 0) + 8)
        self.world.add_event(
            f"{ca.name} улучшает отношения с {cb.name}.",
            notify=self.world.player_id in (a, b),
        )
        return True, "Отношения улучшены"

    def degrade(self, a, b):
        if self._incompatible_zombie_diplomacy(a, b):
            return False, "С заражёнными нельзя вести дипломатические переговоры"
        ca, cb = self.world.countries[a], self.world.countries[b]
        ca.relations[b] = max(-100, ca.relations.get(b, 0) - 15)
        cb.relations[a] = max(-100, cb.relations.get(a, 0) - 5)
        self.world.add_event(
            f"Напряжение растёт между {ca.name} и {cb.name}.",
            notify=self.world.player_id in (a, b),
        )
        return True, "Отношения ухудшены"

    def form_alliance(self, a, b):
        if a == b:
            return False, "Нельзя заключить союз с самим собой"
        if self._incompatible_zombie_diplomacy(a, b):
            return False, "С заражёнными нельзя заключить союз"
        ca, cb = self.world.countries[a], self.world.countries[b]
        if ca.wars or cb.wars:
            return False, "Нельзя заключить союз во время войны"
        if ca.alliance == b and cb.alliance == a:
            return False, "Союз уже заключён"
        if ca.alliance or cb.alliance:
            return False, "Сначала расторгните действующий союз"
        if ca.relations.get(b, 0) < 20:
            return False, "Для союза нужны отношения не ниже +20"
        ca.alliance = b
        cb.alliance = a
        ca.relations[b] = max(ca.relations.get(b, 0), 60)
        cb.relations[a] = max(cb.relations.get(a, 0), 60)
        self.world.add_event(
            f"{ca.name} и {cb.name} заключили союз.",
            notify=self.world.player_id in (a, b),
            modal=self.world.player_id in (a, b),
        )
        return True, "Союз заключён"

    def break_alliance(self, a, b):
        if a == b:
            return False, "Нельзя расторгнуть союз с самим собой"
        if self._incompatible_zombie_diplomacy(a, b):
            return False, "У заражённых не может быть дипломатических союзов"
        ca, cb = self.world.countries[a], self.world.countries[b]
        if ca.alliance != b and cb.alliance != a:
            return False, "Союз между государствами не заключён"
        if ca.alliance == b:
            ca.alliance = None
        if cb.alliance == a:
            cb.alliance = None
        if ca.treaties.get(b, {}).get("type") == "alliance":
            del ca.treaties[b]
        if cb.treaties.get(a, {}).get("type") == "alliance":
            del cb.treaties[a]
        self.world.add_event(
            f"{ca.name} и {cb.name} расторгли союз.",
            notify=self.world.player_id in (a, b),
            modal=self.world.player_id in (a, b),
        )
        return True, "Союз расторгнут"

    def propose_peace(self, a, b):
        return self.world.offer_peace(a, b, "status_quo")

    def _incompatible_zombie_diplomacy(self, a, b):
        return (
            self.world.scenario_id == "zombie"
            and "zombies" in (a, b)
        )
