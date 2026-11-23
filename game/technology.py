from .zombie_mode import SURVIVOR_TECH_TREE, ZOMBIE_TECH_TREE

TECH_TREE = (
    {"id": "administration", "name": "Государственное управление", "short": "Управление",
     "cost": 320, "points": 8, "requires": (), "effect": "Производство +8%",
     "position": (0, 0)},
    {"id": "education", "name": "Всеобщее образование", "short": "Образование",
     "cost": 360, "points": 9, "requires": (), "effect": "Исследования быстрее на 50%",
     "position": (1, 0)},
    {"id": "trade_network", "name": "Торговые сети", "short": "Торговля",
     "cost": 380, "points": 9, "requires": (), "effect": "Производство +5%",
     "position": (2, 0)},
    {"id": "military_doctrine", "name": "Военная доктрина", "short": "Доктрина",
     "cost": 420, "points": 10, "requires": (), "effect": "Военная сила +8%",
     "position": (3, 0)},
    {"id": "energy", "name": "Национальная энергосеть", "short": "Энергосеть",
     "cost": 350, "points": 9, "requires": (), "effect": "Энергия и электростанции",
     "position": (4, 0)},
    {"id": "logistics", "name": "Государственная логистика", "short": "Логистика",
     "cost": 450, "points": 11, "requires": ("administration",),
     "effect": "Развитие +5", "position": (0, 1)},
    {"id": "welfare", "name": "Общественные службы", "short": "Службы",
     "cost": 500, "points": 12, "requires": ("education",),
     "effect": "Стабильность +8", "position": (1, 1)},
    {"id": "tax_reform", "name": "Налоговая реформа", "short": "Налоговая реформа",
     "cost": 480, "points": 12, "requires": ("trade_network", "administration"),
     "effect": "Сбор налогов +10%", "position": (2, 1)},
    {"id": "tactics", "name": "Общевойсковая подготовка", "short": "Тактика",
     "cost": 520, "points": 13, "requires": ("military_doctrine",),
     "effect": "Военная сила +8%", "position": (3, 1)},
    {"id": "agriculture", "name": "Современное сельское хозяйство", "short": "Аграрный сектор",
     "cost": 460, "points": 11, "requires": ("energy",),
     "effect": "Фермы +6, продовольствие +12", "position": (4, 1)},
    {"id": "industry", "name": "Промышленные стандарты", "short": "Промышленность",
     "cost": 640, "points": 15, "requires": ("logistics",),
     "effect": "Промышленность +8", "position": (0, 2)},
    {"id": "public_health", "name": "Национальная медицина", "short": "Медицина",
     "cost": 620, "points": 15, "requires": ("welfare",),
     "effect": "Здоровье, стабильность и рост населения", "position": (1, 2)},
    {"id": "industrial_trade", "name": "Промышленная торговля", "short": "Экспорт",
     "cost": 680, "points": 16, "requires": ("tax_reform", "industry"),
     "effect": "Производство +8%, промышленность +5", "position": (2, 2)},
    {"id": "military_logistics", "name": "Военная логистика", "short": "Снабжение",
     "cost": 720, "points": 17, "requires": ("tactics",),
     "effect": "Военная сила +12%", "position": (3, 2)},
    {"id": "mechanized_farming", "name": "Механизация сельского хозяйства",
     "short": "Механизация ферм", "cost": 600, "points": 15,
     "requires": ("agriculture", "industry"),
     "effect": "Фермы +8, продовольствие +15", "position": (4, 2)},
    {"id": "automation", "name": "Промышленная автоматизация", "short": "Автоматизация",
     "cost": 850, "points": 20, "requires": ("industry", "logistics"),
     "effect": "Промышленность +10, производство +7%", "position": (0, 3)},
    {"id": "social_services", "name": "Социальная защита", "short": "Соцзащита",
     "cost": 780, "points": 19, "requires": ("public_health", "administration"),
     "effect": "Стабильность +10, поддержка +12", "position": (1, 3)},
    {"id": "global_market", "name": "Интеграция в мировой рынок", "short": "Мировой рынок",
     "cost": 900, "points": 21, "requires": ("industrial_trade", "tax_reform"),
     "effect": "Производство +12%", "position": (2, 3)},
    {"id": "modern_arms", "name": "Современные вооружения", "short": "Вооружения",
     "cost": 900, "points": 22, "requires": ("military_logistics", "industry"),
     "effect": "Военная сила +15%", "position": (3, 3)},
    {"id": "power_grid", "name": "Объединённая энергосистема", "short": "Энергоблок",
     "cost": 780, "points": 19, "requires": ("energy", "agriculture"),
     "effect": "Электростанции +8, энергия +20", "position": (4, 3)},
    {"id": "industrial_robotics", "name": "Промышленная роботизация", "short": "Роботизация",
     "cost": 1050, "points": 26, "requires": ("automation",),
     "effect": "Производство +10%, содержание +3%",
     "position": (0, 4), "bonuses": {"production": 0.10, "upkeep": 0.03}},
    {"id": "welfare_state", "name": "Государство всеобщего благосостояния", "short": "Благосостояние",
     "cost": 1050, "points": 26, "requires": ("social_services",),
     "effect": "Стабильность и поддержка растут; содержание +6%",
     "position": (1, 4),
     "bonuses": {"stability": 0.025, "support": 0.025, "upkeep": 0.06}},
    {"id": "global_finance", "name": "Международные финансовые рынки", "short": "Финансовые рынки",
     "cost": 1050, "points": 26, "requires": ("global_market",),
     "effect": "Налоговый доход +10%, политическая сила +5%",
     "position": (2, 4), "bonuses": {"taxes": 0.10, "political_power": 0.05}},
    {"id": "armored_warfare", "name": "Механизированная война", "short": "Механизированная война",
     "cost": 1100, "points": 28, "requires": ("modern_arms",),
     "effect": "Военная сила +12%, содержание армии +8%",
     "position": (3, 4), "bonuses": {"military": 0.12, "upkeep": 0.08}},
    {"id": "clean_energy", "name": "Атомная и возобновляемая энергетика", "short": "Новая энергетика",
     "cost": 1050, "points": 26, "requires": ("power_grid",),
     "effect": "Электростанции +8, производство +7%",
     "position": (4, 4), "bonuses": {"production": 0.07}},
    {"id": "national_industry", "name": "Национальные промышленные цепочки", "short": "Промышленные цепочки",
     "cost": 1250, "points": 30, "requires": ("industrial_robotics",),
     "effect": "Промышленность +12, налоговый доход +7%",
     "position": (0, 5), "bonuses": {"taxes": 0.07}},
    {"id": "public_university", "name": "Национальные университеты", "short": "Университеты",
     "cost": 1250, "points": 30, "requires": ("welfare_state",),
     "effect": "Исследования +20%, содержание +3%",
     "position": (1, 5), "bonuses": {"research": 0.20, "upkeep": 0.03}},
    {"id": "trade_blocs", "name": "Международные торговые блоки", "short": "Торговые блоки",
     "cost": 1250, "points": 30, "requires": ("global_finance",),
     "effect": "Производство +8%, недовольство +0,01 в день",
     "position": (2, 5), "bonuses": {"production": 0.08, "unrest": 0.01}},
    {"id": "strategic_deterrence", "name": "Стратегическое сдерживание", "short": "Сдерживание",
     "cost": 1300, "points": 32, "requires": ("armored_warfare",),
     "effect": "Военная сила +10%, военная поддержка +0,02 в день",
     "position": (3, 5), "bonuses": {"military": 0.10, "war_support": 0.02}},
    {"id": "precision_agriculture", "name": "Точное земледелие", "short": "Точное земледелие",
     "cost": 1250, "points": 30, "requires": ("clean_energy",),
     "effect": "Фермы +12, стабильность +0,02 в день",
     "position": (4, 5), "bonuses": {"stability": 0.02, "unrest": -0.02}},
    {"id": "supply_chain", "name": "Автоматизированная логистика", "short": "Умная логистика",
     "cost": 1500, "points": 35, "requires": ("national_industry",),
     "effect": "Производство +12%, недовольство +0,01 в день",
     "position": (0, 6), "bonuses": {"production": 0.12, "unrest": 0.01}},
    {"id": "universal_health", "name": "Всеобщая система здравоохранения", "short": "Здравоохранение",
     "cost": 1500, "points": 35, "requires": ("public_university",),
     "effect": "Здоровье населения, недовольство −0,03 в день",
     "position": (1, 6), "bonuses": {"unrest": -0.03, "population_growth": 0.00002}},
    {"id": "export_dominance", "name": "Экспортное доминирование", "short": "Экспортное влияние",
     "cost": 1500, "points": 35, "requires": ("trade_blocs",),
     "effect": "Производство +12%, военное содержание +4%",
     "position": (2, 6), "bonuses": {"production": 0.12, "upkeep": 0.04}},
    {"id": "total_mobilization", "name": "Тотальная мобилизация", "short": "Тотальная мобилизация",
     "cost": 1650, "points": 40, "requires": ("strategic_deterrence",),
     "effect": "Военная сила +20%, стабильность −0,02 и недовольство +0,025 в день",
     "position": (3, 6),
     "bonuses": {"military": 0.20, "upkeep": 0.15, "stability": -0.02, "unrest": 0.025}},
    {"id": "resource_independence", "name": "Ресурсная независимость", "short": "Автаркия ресурсов",
     "cost": 1500, "points": 35, "requires": ("precision_agriculture",),
     "effect": "Содержание −5%, исследования −5%",
     "position": (4, 6), "bonuses": {"upkeep": -0.05, "research": -0.05}},
    {"id": "resilient_supply", "name": "Устойчивые цепочки поставок", "short": "Устойчивые поставки",
     "cost": 1700, "points": 42, "requires": ("supply_chain",),
     "effect": "Производство +10%, налоговый доход +4%, содержание +4%",
     "position": (0, 7),
     "bonuses": {"production": 0.10, "taxes": 0.04, "upkeep": 0.04}},
    {"id": "national_research", "name": "Национальная научная программа", "short": "Научная программа",
     "cost": 1700, "points": 42, "requires": ("universal_health",),
     "effect": "Исследования +25%, налоговый доход −5%",
     "position": (1, 7), "bonuses": {"research": 0.25, "taxes": -0.05}},
    {"id": "sovereign_trade", "name": "Суверенные торговые сети", "short": "Суверенная торговля",
     "cost": 1750, "points": 43, "requires": ("export_dominance",),
     "effect": "Производство +12%, доход +8%, недовольство +0,015 в день",
     "position": (2, 7),
     "bonuses": {"production": 0.12, "taxes": 0.08, "unrest": 0.015}},
    {"id": "integrated_command", "name": "Объединённое военное командование", "short": "Единое командование",
     "cost": 1800, "points": 45, "requires": ("total_mobilization",),
     "effect": "Военная сила +16%, боеготовность выше, содержание +12%",
     "position": (3, 7),
     "bonuses": {"military": 0.16, "readiness": 0.05, "upkeep": 0.12}},
    {"id": "circular_economy", "name": "Замкнутый ресурсный цикл", "short": "Ресурсный цикл",
     "cost": 1700, "points": 42, "requires": ("resource_independence",),
     "effect": "Содержание −10%, производство −5%",
     "position": (4, 7), "bonuses": {"upkeep": -0.10, "production": -0.05}},
    {"id": "civil_industry", "name": "Переориентация на гражданскую промышленность", "short": "Гражданская промышленность",
     "cost": 2150, "points": 50,
     "requires": ("resilient_supply", "universal_health"),
     "effect": "Промышленность и производство растут, военная сила −4%",
     "position": (0, 8),
     "bonuses": {"industry": 12, "production": 0.10, "military": -0.04}},
    {"id": "defense_research", "name": "Оборонные научные институты", "short": "Оборонная наука",
     "cost": 2200, "points": 52,
     "requires": ("national_research", "strategic_deterrence"),
     "effect": "Военная сила +12%, исследования −8%",
     "position": (1, 8), "bonuses": {"military": 0.12, "research": -0.08}},
    {"id": "market_stability", "name": "Стабилизация мирового рынка", "short": "Стабильный рынок",
     "cost": 2150, "points": 50,
     "requires": ("sovereign_trade", "welfare_state"),
     "effect": "Доход и политическая сила растут, военная сила −8%",
     "position": (2, 8),
     "bonuses": {"taxes": 0.12, "political_power": 0.08, "military": -0.08}},
    {"id": "precision_command", "name": "Высокоточное управление войсками", "short": "Точное командование",
     "cost": 2250, "points": 54,
     "requires": ("integrated_command", "public_university"),
     "effect": "Военная сила и боеготовность растут, стабильность −0,02 в день",
     "position": (3, 8),
     "bonuses": {"military": 0.14, "readiness": 0.05, "stability": -0.02}},
    {"id": "green_autonomy", "name": "Энергетическая автономия", "short": "Энергетическая автономия",
     "cost": 2150, "points": 50,
     "requires": ("circular_economy", "precision_agriculture"),
     "effect": "Производство +10%, содержание ниже, исследования −4%",
     "position": (4, 8),
     "bonuses": {"production": 0.10, "upkeep": -0.06, "research": -0.04}},
    {"id": "automated_resilience", "name": "Автоматизированная устойчивость", "short": "Автоматизированная устойчивость",
     "cost": 2700, "points": 62,
     "requires": ("civil_industry", "green_autonomy"),
     "effect": "Производство +15%, содержание +8%, недовольство +0,015 в день",
     "position": (0, 9),
     "bonuses": {"production": 0.15, "upkeep": 0.08, "unrest": 0.015}},
    {"id": "social_compact", "name": "Национальный общественный договор", "short": "Общественный договор",
     "cost": 2650, "points": 60,
     "requires": ("market_stability", "defense_research"),
     "effect": "Стабильность, поддержка и исследования растут, военная сила −10%",
     "position": (1, 9),
     "bonuses": {"stability": 0.04, "support": 0.04, "research": 0.10, "military": -0.10}},
    {"id": "global_standards", "name": "Единые стандарты торговли", "short": "Мировые стандарты",
     "cost": 2700, "points": 62,
     "requires": ("market_stability", "green_autonomy"),
     "effect": "Доход и производство растут, содержание +4%",
     "position": (2, 9),
     "bonuses": {"taxes": 0.12, "production": 0.08, "upkeep": 0.04}},
    {"id": "strategic_arsenal", "name": "Стратегический арсенал", "short": "Стратегический арсенал",
     "cost": 2800, "points": 65,
     "requires": ("precision_command", "defense_research"),
     "effect": "Военная сила и боеготовность растут, содержание +16%",
     "position": (3, 9),
     "bonuses": {"military": 0.18, "readiness": 0.05, "upkeep": 0.16}},
    {"id": "future_energy", "name": "Энергетика следующего поколения", "short": "Энергетика будущего",
     "cost": 2700, "points": 62,
     "requires": ("green_autonomy", "civil_industry"),
     "effect": "Производство и исследования растут, содержание ниже",
     "position": (4, 9),
     "bonuses": {"production": 0.12, "research": 0.06, "upkeep": -0.08}},
    {"id": "green_transition", "name": "Зелёный промышленный переход", "short": "Зелёный переход",
     "cost": 3200, "points": 78,
     "requires": ("civil_industry", "future_energy"),
     "choice_group": "late_national_model",
     "effect": "Производство +12%, недовольство −0,02 в день, военная сила −8%",
     "position": (0, 10),
     "bonuses": {"production": 0.12, "unrest": -0.02, "military": -0.08}},
    {"id": "market_consolidation", "name": "Мировая финансовая интеграция", "short": "Финансовая интеграция",
     "cost": 3200, "points": 78,
     "requires": ("market_stability", "global_standards"),
     "choice_group": "late_national_model",
     "effect": "Налоговый доход +16%, исследования +8%, недовольство +0,025 в день",
     "position": (2, 10),
     "bonuses": {"taxes": 0.16, "research": 0.08, "unrest": 0.025}},
    {"id": "defense_first", "name": "Приоритет национальной обороны", "short": "Оборонный приоритет",
     "cost": 3400, "points": 82,
     "requires": ("strategic_arsenal", "integrated_command"),
     "choice_group": "late_national_model",
     "effect": "Военная сила +18%, содержание +15%, стабильность −0,025 в день",
     "position": (4, 10),
     "bonuses": {"military": 0.18, "upkeep": 0.15, "stability": -0.025}},
    {"id": "resilient_cities", "name": "Устойчивые города", "short": "Устойчивые города",
     "cost": 3900, "points": 90, "requires": ("green_transition",),
     "effect": "Стабильность +0,035 в день, доход −6%",
     "position": (0, 11),
     "bonuses": {"stability": 0.035, "taxes": -0.06, "unrest": -0.02}},
    {"id": "social_investment", "name": "Общественные инвестиции", "short": "Социальные инвестиции",
     "cost": 4500, "points": 105, "requires": ("resilient_cities",),
     "effect": "Поддержка и стабильность растут, производство −5%",
     "position": (0, 12),
     "bonuses": {"support": 0.04, "stability": 0.03, "production": -0.05}},
    {"id": "global_innovation", "name": "Глобальная инновационная сеть", "short": "Инновационная сеть",
     "cost": 3900, "points": 90, "requires": ("market_consolidation",),
     "effect": "Исследования +20%, производство +8%, содержание +6%",
     "position": (2, 11),
     "bonuses": {"research": 0.20, "production": 0.08, "upkeep": 0.06}},
    {"id": "credit_deregulation", "name": "Дерегулирование кредита", "short": "Свободный кредит",
     "cost": 4500, "points": 105, "requires": ("global_innovation",),
     "effect": "Налоговый доход +14%, стабильность −0,025 в день",
     "position": (2, 12),
     "bonuses": {"taxes": 0.14, "stability": -0.025, "unrest": 0.02}},
    {"id": "strategic_reserves", "name": "Стратегические резервы", "short": "Стратегические резервы",
     "cost": 4000, "points": 94, "requires": ("defense_first",),
     "effect": "Боеготовность и сила армии выше, доход −8%",
     "position": (4, 11),
     "bonuses": {"military": 0.10, "readiness": 0.06, "taxes": -0.08}},
    {"id": "permanent_mobilization", "name": "Постоянная мобилизация", "short": "Постоянная мобилизация",
     "cost": 4700, "points": 110, "requires": ("strategic_reserves",),
     "effect": "Военная сила +20%, содержание +20%, недовольство +0,03 в день",
     "position": (4, 12),
     "bonuses": {"military": 0.20, "upkeep": 0.20, "unrest": 0.03}},
)


def technology_bonuses(techs):
    bonuses = {}
    for node in TECH_TREE + SURVIVOR_TECH_TREE + ZOMBIE_TECH_TREE:
        if node["id"] not in techs:
            continue
        for key, value in node.get("bonuses", {}).items():
            bonuses[key] = bonuses.get(key, 0) + value
    return bonuses


def technology_branch_locked(techs, technology_id, technology_tree=TECH_TREE):
    node = next(
        (item for item in technology_tree if item["id"] == technology_id),
        None,
    )
    if not node or not node.get("choice_group"):
        return False
    return any(
        other["id"] in techs
        and other.get("choice_group") == node["choice_group"]
        and other["id"] != technology_id
        for other in technology_tree
    )


def validate_research(
    country, technology_id, technology_tree=TECH_TREE, paid=False
):
    node = next(
        (item for item in technology_tree if item["id"] == technology_id),
        None,
    )
    if node is None:
        return False, "Технология не найдена"
    if technology_id in country.techs:
        return False, "Технология уже изучена"
    if technology_branch_locked(country.techs, technology_id, technology_tree):
        return False, "Вы уже выбрали другую ветку развития"
    missing = [required for required in node["requires"] if required not in country.techs]
    if missing:
        return False, "Сначала изучите предыдущую технологию"
    if not paid and country.money < node["cost"]:
        return False, f"Нужно денег: {node['cost']}"
    if not paid and country.research_points < node["points"]:
        return False, f"Не хватает очков исследований: {node['points']}"
    return True, node


def research(country, technology_id, technology_tree=TECH_TREE, paid=False):
    valid, result = validate_research(
        country, technology_id, technology_tree, paid=paid
    )
    if not valid:
        return False, result
    node = result
    if not paid:
        country.money -= node["cost"]
        country.research_points -= node["points"]
    country.techs.add(technology_id)
    effects = {
        "administration": lambda: None,
        "education": lambda: None,
        "trade_network": lambda: None,
        "military_doctrine": lambda: None,
        "energy": lambda: (
            setattr(country, "power_plants", country.power_plants + 5),
            setattr(country, "energy", min(100, country.energy + 15)),
        ),
        "logistics": lambda: setattr(country, "development", min(100, country.development + 5)),
        "welfare": lambda: setattr(country, "stability", min(100, country.stability + 8)),
        "tax_reform": lambda: None,
        "tactics": lambda: None,
        "agriculture": lambda: (
            setattr(country, "farms", country.farms + 6),
            setattr(country, "food", min(100, country.food + 12)),
        ),
        "industry": lambda: setattr(country, "industry", min(100, country.industry + 8)),
        "public_health": lambda: (
            setattr(country, "stability", min(100, country.stability + 6)),
            setattr(country, "government_support", min(100, country.government_support + 5)),
        ),
        "industrial_trade": lambda: setattr(country, "industry", min(100, country.industry + 5)),
        "military_logistics": lambda: None,
        "mechanized_farming": lambda: (
            setattr(country, "farms", country.farms + 8),
            setattr(country, "food", min(100, country.food + 15)),
        ),
        "automation": lambda: setattr(country, "industry", min(100, country.industry + 10)),
        "social_services": lambda: (
            setattr(country, "stability", min(100, country.stability + 10)),
            setattr(country, "government_support", min(100, country.government_support + 12)),
        ),
        "global_market": lambda: None,
        "modern_arms": lambda: None,
        "power_grid": lambda: (
            setattr(country, "power_plants", country.power_plants + 8),
            setattr(country, "energy", min(100, country.energy + 20)),
        ),
        "industrial_robotics": lambda: setattr(
            country, "industry", min(100, country.industry + 8)
        ),
        "welfare_state": lambda: (
            setattr(country, "stability", min(100, country.stability + 6)),
            setattr(
                country, "government_support",
                min(100, country.government_support + 6),
            ),
        ),
        "global_finance": lambda: None,
        "armored_warfare": lambda: None,
        "clean_energy": lambda: (
            setattr(country, "power_plants", country.power_plants + 8),
            setattr(country, "energy", min(100, country.energy + 15)),
        ),
        "national_industry": lambda: setattr(
            country, "industry", min(100, country.industry + 12)
        ),
        "public_university": lambda: None,
        "trade_blocs": lambda: None,
        "strategic_deterrence": lambda: setattr(
            country, "army_readiness", min(100, country.army_readiness + 8)
        ),
        "precision_agriculture": lambda: (
            setattr(country, "farms", country.farms + 12),
            setattr(country, "food", min(100, country.food + 25)),
        ),
        "supply_chain": lambda: None,
        "universal_health": lambda: (
            setattr(country, "stability", min(100, country.stability + 8)),
            setattr(
                country, "government_support",
                min(100, country.government_support + 6),
            ),
        ),
        "export_dominance": lambda: None,
        "total_mobilization": lambda: None,
        "resource_independence": lambda: None,
        "resilient_supply": lambda: None,
        "national_research": lambda: None,
        "sovereign_trade": lambda: None,
        "integrated_command": lambda: None,
        "circular_economy": lambda: None,
        "civil_industry": lambda: setattr(
            country, "industry", min(100, country.industry + 12)
        ),
        "defense_research": lambda: None,
        "market_stability": lambda: None,
        "precision_command": lambda: None,
        "green_autonomy": lambda: None,
        "automated_resilience": lambda: None,
        "social_compact": lambda: None,
        "global_standards": lambda: None,
        "strategic_arsenal": lambda: None,
        "future_energy": lambda: None,
        "green_transition": lambda: None,
        "market_consolidation": lambda: None,
        "defense_first": lambda: None,
        "resilient_cities": lambda: None,
        "social_investment": lambda: None,
        "global_innovation": lambda: None,
        "credit_deregulation": lambda: None,
        "strategic_reserves": lambda: None,
        "permanent_mobilization": lambda: None,
    }
    effects.get(technology_id, lambda: None)()
    return True, f"Исследование завершено: {node['name']}"
