class War:
    def __init__(
        self,
        war_id,
        attackers,
        defenders,
        objective,
        started_day,
        data=None,
    ):
        data = data or {}
        self.id = war_id
        self.attackers = list(dict.fromkeys(data.get("attackers", attackers)))
        self.defenders = list(dict.fromkeys(data.get("defenders", defenders)))
        self.objective = data.get("objective", objective)
        self.started_day = data.get("started_day", started_day)
        self.started_territories = dict(data.get("started_territories", {}))
        self.last_progress_day = data.get("last_progress_day", self.started_day)
        self.status = data.get("status", "active")
        self.battles = data.get("battles", 0)
        self.attacker_score = data.get("attacker_score", 0.0)
        self.defender_score = data.get("defender_score", 0.0)
        self.last_ai_operation_day = data.get("last_ai_operation_day")
        self.last_peace_offer_day = data.get("last_peace_offer_day")
        self.peace_offer = data.get("peace_offer")
        self.casualties = dict(data.get("casualties", {}))
        self.occupied_regions = list(data.get("occupied_regions", []))
        self.settlement = data.get("settlement")
        self.ended_day = data.get("ended_day")

    def side(self, country_id):
        if country_id in self.attackers:
            return self.attackers
        if country_id in self.defenders:
            return self.defenders
        return None

    def enemies(self, country_id):
        if country_id in self.attackers:
            return self.defenders
        if country_id in self.defenders:
            return self.attackers
        return []

    def to_dict(self):
        return {
            "id": self.id,
            "attackers": self.attackers,
            "defenders": self.defenders,
            "objective": self.objective,
            "started_day": self.started_day,
            "started_territories": self.started_territories,
            "last_progress_day": self.last_progress_day,
            "status": self.status,
            "battles": self.battles,
            "attacker_score": self.attacker_score,
            "defender_score": self.defender_score,
            "last_ai_operation_day": self.last_ai_operation_day,
            "last_peace_offer_day": self.last_peace_offer_day,
            "peace_offer": self.peace_offer,
            "casualties": self.casualties,
            "occupied_regions": self.occupied_regions,
            "settlement": self.settlement,
            "ended_day": self.ended_day,
        }
