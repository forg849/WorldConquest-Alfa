class Economy:
    @staticmethod
    def summary(country, region_count=1):
        report = country.economy_report(region_count)
        return {
            "output": round(report["output"], 1),
            "income": round(report["taxes"], 1),
            "upkeep": round(report["upkeep"], 1),
            "net": round(report["net"], 1),
            "money": round(country.money),
            "food": round(country.food),
            "food_balance": round(report["food_balance"], 2),
            "industry": round(country.industry),
            "energy": round(country.energy),
            "energy_balance": round(report["energy_balance"], 2),
            "tax_rate": country.tax_rate,
        }
