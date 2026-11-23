from .zombie_mode import ZOMBIE_IDEOLOGIES, ZOMBIE_IDEOLOGY_TREES

IDEOLOGIES = {
    "communism": {
        "name": "Коммунизм",
        "description": "Государственное планирование, общественные программы и массовая армия.",
        "bonuses": {"production": 0.02, "support": 0.025},
    },
    "fascism": {
        "name": "Фашизм",
        "description": "Централизация власти и мобилизация страны вокруг армии.",
        "bonuses": {"military": 0.08, "upkeep": 0.06, "war_support": 0.025},
    },
    "monarchy": {
        "name": "Монархия",
        "description": "Традиционные институты, общественная стабильность и сильная власть.",
        "bonuses": {"stability": 0.025, "political_power": 0.08},
    },
    "democracy": {
        "name": "Демократия",
        "description": "Гражданские институты, образование и открытая экономика.",
        "bonuses": {"production": 0.025, "research": 0.08},
    },
}

IDEOLOGY_TREES = {
    "communism": (
        {
            "id": "communism_collectivization",
            "name": "Коллективное хозяйство",
            "effect": "Производство +5%",
            "cost": 35,
            "requires": (),
            "position": (0, 0),
            "bonuses": {"production": 0.05},
        },
        {
            "id": "communism_planned_industry",
            "name": "Плановая индустрия",
            "effect": "Промышленность +8, производство +4%",
            "cost": 55,
            "requires": ("communism_collectivization",),
            "position": (0, 1),
            "bonuses": {"production": 0.04, "industry": 8},
        },
        {
            "id": "communism_national_industry",
            "name": "Национальные проекты",
            "effect": "Производство +7%, доход +4%",
            "cost": 75,
            "requires": ("communism_planned_industry",),
            "position": (0, 2),
            "bonuses": {"production": 0.07, "taxes": 0.04},
        },
        {
            "id": "communism_workers_state",
            "name": "Рабочее государство",
            "effect": "Поддержка правительства растёт быстрее",
            "cost": 35,
            "requires": (),
            "position": (1, 0),
            "bonuses": {"support": 0.04, "unrest": -0.025},
        },
        {
            "id": "communism_social_welfare",
            "name": "Социальные гарантии",
            "effect": "Стабильность +0,04 в день",
            "cost": 55,
            "requires": ("communism_workers_state",),
            "position": (1, 1),
            "bonuses": {"stability": 0.04, "unrest": -0.02},
        },
        {
            "id": "communism_popular_army",
            "name": "Народная армия",
            "effect": "Военная сила +7%",
            "cost": 75,
            "requires": ("communism_social_welfare",),
            "position": (1, 2),
            "bonuses": {"military": 0.07, "readiness": 0.02},
        },
        {
            "id": "communism_industrial_autonomy",
            "name": "Технологическая самообеспеченность",
            "effect": "Производство +10%, содержание +6%",
            "cost": 95,
            "requires": ("communism_national_industry",),
            "position": (0, 3),
            "bonuses": {"production": 0.10, "upkeep": 0.06},
        },
        {
            "id": "communism_mass_mobilization",
            "name": "Массовая мобилизация",
            "effect": "Военная сила +12%, недовольство +0,015 в день",
            "cost": 95,
            "requires": ("communism_popular_army",),
            "position": (1, 3),
            "bonuses": {"military": 0.12, "unrest": 0.015},
        },
        {
            "id": "communism_state_ownership",
            "name": "Государственная собственность",
            "effect": "Производство +7%, содержание +3%",
            "cost": 55,
            "requires": (),
            "position": (2, 0),
            "bonuses": {"production": 0.07, "upkeep": 0.03},
        },
        {
            "id": "communism_directive_planning",
            "name": "Директивное планирование",
            "effect": "Производство +10%, исследования −8%",
            "cost": 75,
            "requires": ("communism_state_ownership",),
            "position": (2, 1),
            "bonuses": {"production": 0.10, "research": -0.08},
        },
        {
            "id": "communism_party_control",
            "name": "Партийный контроль",
            "effect": "Политическая сила +15%, недовольство +0,015 в день",
            "cost": 95,
            "requires": ("communism_directive_planning",),
            "position": (2, 2),
            "bonuses": {"political_power": 0.15, "unrest": 0.015},
        },
        {
            "id": "communism_collective_security",
            "name": "Коллективная безопасность",
            "effect": "Поддержка и стабильность растут, доход −4%",
            "cost": 115,
            "requires": ("communism_party_control",),
            "position": (2, 3),
            "bonuses": {"support": 0.025, "stability": 0.025, "taxes": -0.04},
        },
        {
            "id": "communism_central_plans",
            "name": "Центральное планирование",
            "effect": "Промышленность и производство растут, доход −4%",
            "cost": 135,
            "requires": ("communism_industrial_autonomy",),
            "position": (0, 4),
            "bonuses": {"production": 0.09, "industry": 8, "taxes": -0.04},
        },
        {
            "id": "communism_productive_targets",
            "name": "Пятилетние нормативы",
            "effect": "Производство +12%, недовольство +0,015 в день",
            "cost": 165,
            "requires": ("communism_central_plans",),
            "position": (0, 5),
            "bonuses": {"production": 0.12, "unrest": 0.015},
        },
        {
            "id": "communism_reserve_army",
            "name": "Стратегический резерв",
            "effect": "Военная сила +14%, содержание +6%",
            "cost": 135,
            "requires": ("communism_mass_mobilization",),
            "position": (1, 4),
            "bonuses": {"military": 0.14, "upkeep": 0.06},
        },
        {
            "id": "communism_people_militia",
            "name": "Народное ополчение",
            "effect": "Военная сила +8%, стабильность −0,02 в день",
            "cost": 165,
            "requires": ("communism_reserve_army",),
            "position": (1, 5),
            "bonuses": {"military": 0.08, "war_support": 0.02, "stability": -0.02},
        },
        {
            "id": "communism_public_distribution",
            "name": "Общественное распределение",
            "effect": "Поддержка и стабильность растут, доход −8%",
            "cost": 135,
            "requires": ("communism_collective_security",),
            "position": (2, 4),
            "bonuses": {"support": 0.03, "unrest": -0.02, "taxes": -0.08},
        },
        {
            "id": "communism_party_discipline",
            "name": "Партийная дисциплина",
            "effect": "Политическая сила +20%, исследования −10%",
            "cost": 165,
            "requires": ("communism_public_distribution",),
            "position": (2, 5),
            "bonuses": {"political_power": 0.20, "research": -0.10, "unrest": 0.02},
        },
    ),
    "fascism": (
        {
            "id": "fascism_national_unity",
            "name": "Национальное единство",
            "effect": "Поддержка правительства растёт быстрее",
            "cost": 35,
            "requires": (),
            "position": (0, 0),
            "bonuses": {"support": 0.04, "war_support": 0.02},
        },
        {
            "id": "fascism_state_propaganda",
            "name": "Государственная пропаганда",
            "effect": "Усталость войны накапливается медленнее",
            "cost": 55,
            "requires": ("fascism_national_unity",),
            "position": (0, 1),
            "bonuses": {"war_exhaustion": -0.12, "war_support": 0.025},
        },
        {
            "id": "fascism_total_mobilization",
            "name": "Тотальная мобилизация",
            "effect": "Военная сила +12%, содержание армии выше",
            "cost": 75,
            "requires": ("fascism_state_propaganda",),
            "position": (0, 2),
            "bonuses": {"military": 0.12, "upkeep": 0.04},
        },
        {
            "id": "fascism_security_apparatus",
            "name": "Аппарат безопасности",
            "effect": "Недовольство снижается быстрее",
            "cost": 35,
            "requires": (),
            "position": (1, 0),
            "bonuses": {"unrest": -0.035, "stability": 0.015},
        },
        {
            "id": "fascism_officer_corps",
            "name": "Корпус офицеров",
            "effect": "Военная сила +7%, боеготовность растёт",
            "cost": 55,
            "requires": ("fascism_security_apparatus",),
            "position": (1, 1),
            "bonuses": {"military": 0.07, "readiness": 0.035},
        },
        {
            "id": "fascism_war_economy",
            "name": "Военная экономика",
            "effect": "Производство +8%, содержание армии выше",
            "cost": 75,
            "requires": ("fascism_officer_corps",),
            "position": (1, 2),
            "bonuses": {"production": 0.08, "upkeep": 0.05},
        },
        {
            "id": "fascism_armaments_industry",
            "name": "Военно-промышленный комплекс",
            "effect": "Военная сила +10%, содержание +8%",
            "cost": 95,
            "requires": ("fascism_total_mobilization",),
            "position": (0, 3),
            "bonuses": {"military": 0.10, "upkeep": 0.08},
        },
        {
            "id": "fascism_militarized_state",
            "name": "Милитаризованное общество",
            "effect": "Производство +6%, недовольство +0,02 в день",
            "cost": 95,
            "requires": ("fascism_war_economy",),
            "position": (1, 3),
            "bonuses": {"production": 0.06, "unrest": 0.02},
        },
        {
            "id": "fascism_corporatism",
            "name": "Корпоративная экономика",
            "effect": "Производство +8%, поддержка −0,01 в день",
            "cost": 55,
            "requires": (),
            "position": (2, 0),
            "bonuses": {"production": 0.08, "support": -0.01},
        },
        {
            "id": "fascism_autarky",
            "name": "Экономическая автаркия",
            "effect": "Содержание −5%, исследования −8%",
            "cost": 75,
            "requires": ("fascism_corporatism",),
            "position": (2, 1),
            "bonuses": {"upkeep": -0.05, "research": -0.08},
        },
        {
            "id": "fascism_secret_police",
            "name": "Внутренняя безопасность",
            "effect": "Недовольство снижается, поддержка −0,02 в день",
            "cost": 95,
            "requires": ("fascism_autarky",),
            "position": (2, 2),
            "bonuses": {"unrest": -0.04, "support": -0.02},
        },
        {
            "id": "fascism_total_war",
            "name": "Всеобщая война",
            "effect": "Военная сила +20%, стабильность −0,025 и недовольство +0,03 в день",
            "cost": 115,
            "requires": ("fascism_secret_police",),
            "position": (2, 3),
            "bonuses": {"military": 0.20, "upkeep": 0.12, "stability": -0.025, "unrest": 0.03},
        },
        {
            "id": "fascism_heavy_industry",
            "name": "Тяжёлая промышленность",
            "effect": "Производство +10%, содержание +8%",
            "cost": 135,
            "requires": ("fascism_armaments_industry",),
            "position": (0, 4),
            "bonuses": {"production": 0.10, "upkeep": 0.08},
        },
        {
            "id": "fascism_army_state",
            "name": "Государство армии",
            "effect": "Военная сила +12%, поддержка −0,025 в день",
            "cost": 165,
            "requires": ("fascism_heavy_industry", "fascism_militarized_state"),
            "position": (0, 5),
            "bonuses": {"military": 0.12, "support": -0.025},
        },
        {
            "id": "fascism_mass_conscription",
            "name": "Всеобщий призыв",
            "effect": "Армия и боеготовность растут, недовольство +0,02 в день",
            "cost": 135,
            "requires": ("fascism_militarized_state",),
            "position": (1, 4),
            "bonuses": {"military": 0.12, "readiness": 0.02, "unrest": 0.02},
        },
        {
            "id": "fascism_war_bonds",
            "name": "Военные облигации",
            "effect": "Производство и доход +8%, стабильность −0,025 в день",
            "cost": 165,
            "requires": ("fascism_mass_conscription", "fascism_total_war"),
            "position": (1, 5),
            "bonuses": {"production": 0.08, "taxes": 0.08, "stability": -0.025},
        },
        {
            "id": "fascism_command_economy",
            "name": "Военная командная экономика",
            "effect": "Военная сила +16%, налоговый доход −6%",
            "cost": 135,
            "requires": ("fascism_total_war",),
            "position": (2, 4),
            "bonuses": {"military": 0.16, "taxes": -0.06, "unrest": 0.025},
        },
        {
            "id": "fascism_permanent_emergency",
            "name": "Постоянная чрезвычайная мобилизация",
            "effect": "Военная сила +12%, содержание +15%, поддержка −0,02 в день",
            "cost": 165,
            "requires": ("fascism_command_economy",),
            "position": (2, 5),
            "bonuses": {"military": 0.12, "upkeep": 0.15, "support": -0.02},
        },
    ),
    "monarchy": (
        {
            "id": "monarchy_royal_authority",
            "name": "Королевская власть",
            "effect": "Политическая сила +12%",
            "cost": 35,
            "requires": (),
            "position": (0, 0),
            "bonuses": {"political_power": 0.12, "support": 0.015},
        },
        {
            "id": "monarchy_civil_service",
            "name": "Королевская служба",
            "effect": "Доход +7%",
            "cost": 55,
            "requires": ("monarchy_royal_authority",),
            "position": (0, 1),
            "bonuses": {"taxes": 0.07, "political_power": 0.05},
        },
        {
            "id": "monarchy_national_projects",
            "name": "Национальные проекты",
            "effect": "Развитие +6, производство +4%",
            "cost": 75,
            "requires": ("monarchy_civil_service",),
            "position": (0, 2),
            "bonuses": {"development": 6, "production": 0.04},
        },
        {
            "id": "monarchy_aristocratic_compact",
            "name": "Сословный договор",
            "effect": "Стабильность +0,04 в день",
            "cost": 35,
            "requires": (),
            "position": (1, 0),
            "bonuses": {"stability": 0.04, "unrest": -0.02},
        },
        {
            "id": "monarchy_royal_guard",
            "name": "Королевская гвардия",
            "effect": "Военная сила +8%",
            "cost": 55,
            "requires": ("monarchy_aristocratic_compact",),
            "position": (1, 1),
            "bonuses": {"military": 0.08, "readiness": 0.02},
        },
        {
            "id": "monarchy_imperial_court",
            "name": "Имперский двор",
            "effect": "Политическая сила +10%, стабильность +0,02 в день",
            "cost": 75,
            "requires": ("monarchy_royal_guard",),
            "position": (1, 2),
            "bonuses": {"political_power": 0.10, "stability": 0.02},
        },
        {
            "id": "monarchy_imperial_administration",
            "name": "Имперская администрация",
            "effect": "Производство +8%, содержание +4%",
            "cost": 95,
            "requires": ("monarchy_national_projects",),
            "position": (0, 3),
            "bonuses": {"production": 0.08, "upkeep": 0.04},
        },
        {
            "id": "monarchy_royal_mandate",
            "name": "Королевский мандат",
            "effect": "Стабильность +0,03 в день, исследования −5%",
            "cost": 95,
            "requires": ("monarchy_imperial_court",),
            "position": (1, 3),
            "bonuses": {"stability": 0.03, "research": -0.05},
        },
        {
            "id": "monarchy_court_patronage",
            "name": "Покровительство двора",
            "effect": "Налоговый доход +8%, содержание +4%",
            "cost": 55,
            "requires": (),
            "position": (2, 0),
            "bonuses": {"taxes": 0.08, "upkeep": 0.04},
        },
        {
            "id": "monarchy_estate_privileges",
            "name": "Привилегии сословий",
            "effect": "Стабильность +0,02 в день, производство −5%",
            "cost": 75,
            "requires": ("monarchy_court_patronage",),
            "position": (2, 1),
            "bonuses": {"stability": 0.02, "production": -0.05},
        },
        {
            "id": "monarchy_dynastic_network",
            "name": "Династическая сеть",
            "effect": "Политическая сила +12%, недовольство +0,01 в день",
            "cost": 95,
            "requires": ("monarchy_estate_privileges",),
            "position": (2, 2),
            "bonuses": {"political_power": 0.12, "unrest": 0.01},
        },
        {
            "id": "monarchy_crown_army",
            "name": "Армия короны",
            "effect": "Военная сила +12%, содержание +6%",
            "cost": 115,
            "requires": ("monarchy_dynastic_network",),
            "position": (2, 3),
            "bonuses": {"military": 0.12, "readiness": 0.03, "upkeep": 0.06},
        },
        {
            "id": "monarchy_national_railways",
            "name": "Королевские железные дороги",
            "effect": "Производство +8%, военная сила +5%, содержание +4%",
            "cost": 135,
            "requires": ("monarchy_imperial_administration",),
            "position": (0, 4),
            "bonuses": {"production": 0.08, "military": 0.05, "upkeep": 0.04},
        },
        {
            "id": "monarchy_royal_industrialists",
            "name": "Королевская промышленная хартия",
            "effect": "Доход и производство растут, поддержка −0,015 в день",
            "cost": 165,
            "requires": ("monarchy_national_railways",),
            "position": (0, 5),
            "bonuses": {"taxes": 0.08, "production": 0.06, "support": -0.015},
        },
        {
            "id": "monarchy_constitutional_charter",
            "name": "Конституционная хартия",
            "effect": "Исследования +8%, стабильность растёт, политическая сила −8%",
            "cost": 135,
            "requires": ("monarchy_royal_mandate",),
            "position": (1, 4),
            "bonuses": {"research": 0.08, "stability": 0.025, "political_power": -0.08},
        },
        {
            "id": "monarchy_parliamentary_council",
            "name": "Представительный совет",
            "effect": "Поддержка растёт, недовольство снижается, военная сила −5%",
            "cost": 165,
            "requires": ("monarchy_constitutional_charter",),
            "position": (1, 5),
            "bonuses": {"support": 0.03, "unrest": -0.015, "military": -0.05},
        },
        {
            "id": "monarchy_noble_officers",
            "name": "Офицерская знать",
            "effect": "Военная сила +12%, боеготовность растёт, доход −4%",
            "cost": 135,
            "requires": ("monarchy_crown_army",),
            "position": (2, 4),
            "bonuses": {"military": 0.12, "readiness": 0.04, "taxes": -0.04},
        },
        {
            "id": "monarchy_imperial_levy",
            "name": "Имперский сбор",
            "effect": "Военная сила +14%, содержание +10%, недовольство +0,015 в день",
            "cost": 165,
            "requires": ("monarchy_noble_officers",),
            "position": (2, 5),
            "bonuses": {"military": 0.14, "upkeep": 0.10, "unrest": 0.015},
        },
    ),
    "democracy": (
        {
            "id": "democracy_civil_rights",
            "name": "Гражданские институты",
            "effect": "Поддержка правительства растёт быстрее",
            "cost": 35,
            "requires": (),
            "position": (0, 0),
            "bonuses": {"support": 0.035, "unrest": -0.02},
        },
        {
            "id": "democracy_public_services",
            "name": "Общественные службы",
            "effect": "Стабильность +0,035 в день",
            "cost": 55,
            "requires": ("democracy_civil_rights",),
            "position": (0, 1),
            "bonuses": {"stability": 0.035, "unrest": -0.015},
        },
        {
            "id": "democracy_civic_research",
            "name": "Гражданская наука",
            "effect": "Исследования +15%",
            "cost": 75,
            "requires": ("democracy_public_services",),
            "position": (0, 2),
            "bonuses": {"research": 0.15, "political_power": 0.04},
        },
        {
            "id": "democracy_free_press",
            "name": "Свободная пресса",
            "effect": "Производство +5%",
            "cost": 35,
            "requires": (),
            "position": (1, 0),
            "bonuses": {"production": 0.05, "political_power": 0.04},
        },
        {
            "id": "democracy_public_debate",
            "name": "Общественные дебаты",
            "effect": "Недовольство снижается, политическая сила +8%",
            "cost": 55,
            "requires": ("democracy_free_press",),
            "position": (1, 1),
            "bonuses": {"unrest": -0.03, "political_power": 0.08},
        },
        {
            "id": "democracy_strategic_diplomacy",
            "name": "Стратегическая дипломатия",
            "effect": "Доход +5%, политическая сила +8%",
            "cost": 75,
            "requires": ("democracy_public_debate",),
            "position": (1, 2),
            "bonuses": {"taxes": 0.05, "political_power": 0.08},
        },
        {
            "id": "democracy_public_research",
            "name": "Общественные инвестиции в науку",
            "effect": "Исследования +20%, налоговый доход −4%",
            "cost": 95,
            "requires": ("democracy_civic_research",),
            "position": (0, 3),
            "bonuses": {"research": 0.20, "taxes": -0.04},
        },
        {
            "id": "democracy_accountable_government",
            "name": "Подотчётное правительство",
            "effect": "Стабильность растёт, военная сила −4%",
            "cost": 95,
            "requires": ("democracy_strategic_diplomacy",),
            "position": (1, 3),
            "bonuses": {"stability": 0.025, "support": 0.025, "military": -0.04},
        },
        {
            "id": "democracy_market_reform",
            "name": "Либерализация рынка",
            "effect": "Производство +10%, стабильность −0,01 в день",
            "cost": 55,
            "requires": (),
            "position": (2, 0),
            "bonuses": {"production": 0.10, "stability": -0.01},
        },
        {
            "id": "democracy_labor_protections",
            "name": "Защита труда",
            "effect": "Недовольство снижается, содержание +4%",
            "cost": 75,
            "requires": ("democracy_market_reform",),
            "position": (2, 1),
            "bonuses": {"unrest": -0.035, "upkeep": 0.04},
        },
        {
            "id": "democracy_civic_mobilization",
            "name": "Гражданская мобилизация",
            "effect": "Боеготовность растёт, доход −5%",
            "cost": 95,
            "requires": ("democracy_labor_protections",),
            "position": (2, 2),
            "bonuses": {"readiness": 0.025, "war_support": 0.02, "taxes": -0.05},
        },
        {
            "id": "democracy_global_coalitions",
            "name": "Глобальные коалиции",
            "effect": "Военная сила +5%, содержание +2%, политическая сила +15%",
            "cost": 115,
            "requires": ("democracy_civic_mobilization",),
            "position": (2, 3),
            "bonuses": {"military": 0.05, "upkeep": 0.02, "political_power": 0.15},
        },
        {
            "id": "democracy_research_councils",
            "name": "Национальные научные советы",
            "effect": "Исследования +25%, налоговый доход −6%",
            "cost": 135,
            "requires": ("democracy_public_research",),
            "position": (0, 4),
            "bonuses": {"research": 0.25, "taxes": -0.06},
        },
        {
            "id": "democracy_open_science",
            "name": "Открытая наука",
            "effect": "Исследования +20%, политическая сила +5%, недовольство +0,01",
            "cost": 165,
            "requires": ("democracy_research_councils",),
            "position": (0, 5),
            "bonuses": {"research": 0.20, "political_power": 0.05, "unrest": 0.01},
        },
        {
            "id": "democracy_coalition_command",
            "name": "Общее командование коалиции",
            "effect": "Военная сила +8%, содержание +5%",
            "cost": 135,
            "requires": ("democracy_global_coalitions",),
            "position": (1, 4),
            "bonuses": {"military": 0.08, "upkeep": 0.05},
        },
        {
            "id": "democracy_reserve_service",
            "name": "Служба в резерве",
            "effect": "Боеготовность растёт, поддержка −0,01 в день",
            "cost": 165,
            "requires": ("democracy_coalition_command",),
            "position": (1, 5),
            "bonuses": {"military": 0.07, "readiness": 0.05, "support": -0.01},
        },
        {
            "id": "democracy_market_consolidation",
            "name": "Консолидация рынка",
            "effect": "Доход и производство растут, стабильность −0,02 в день",
            "cost": 135,
            "requires": ("democracy_global_coalitions",),
            "position": (2, 4),
            "bonuses": {"taxes": 0.10, "production": 0.08, "stability": -0.02},
        },
        {
            "id": "democracy_global_finance",
            "name": "Мировая финансовая система",
            "effect": "Доход и исследования растут, недовольство +0,01 в день",
            "cost": 165,
            "requires": ("democracy_market_consolidation",),
            "position": (2, 5),
            "bonuses": {"taxes": 0.12, "research": 0.08, "unrest": 0.01},
        },
    ),
}


IDEOLOGY_LATE_BRANCHES = {
    "communism": (
        (
            ("state_planned_economy", "Плановая индустрия", "Промышленность +8, производство +12%, исследования −5%",
             {"industry": 8, "production": 0.12, "research": -0.05}),
            ("social_investment", "Социальные гарантии", "Стабильность и поддержка растут, доход −7%",
             {"stability": 0.035, "support": 0.04, "taxes": -0.07}),
            ("people_defense", "Оборона народа", "Военная сила +16%, содержание +12%, недовольство +0,02",
             {"military": 0.16, "upkeep": 0.12, "unrest": 0.02}),
        ),
        (
            ("state_industry", "Государственные индустриальные планы", "Производство +12%, политическая сила +8%",
             {"production": 0.12, "political_power": 0.08}),
            ("public_health", "Всеобщая медицина", "Поддержка растёт быстрее, исследования −5%",
             {"support": 0.04, "unrest": -0.025, "research": -0.05}),
            ("strategic_reserves", "Стратегический резерв", "Военная сила +12%, стабильность −0,02 в день",
             {"military": 0.12, "war_support": 0.03, "stability": -0.02}),
        ),
        (
            ("automation", "Механизация планов", "Производство +15%, содержание +7%",
             {"production": 0.15, "upkeep": 0.07}),
            ("education", "Национальное образование", "Исследования +18%, доход −6%",
             {"research": 0.18, "support": 0.025, "taxes": -0.06}),
            ("mobilized_industry", "Мобилизованная промышленность", "Военная сила +18%, содержание +16%",
             {"military": 0.18, "upkeep": 0.16, "unrest": 0.02}),
        ),
    ),
    "fascism": (
        (
            ("rearmament", "Программа перевооружения", "Военная сила +20%, содержание +16%",
             {"military": 0.20, "upkeep": 0.16, "stability": -0.02}),
            ("corporate_growth", "Корпоративный рост", "Производство +14%, поддержка −0,02 в день",
             {"production": 0.14, "taxes": 0.06, "support": -0.02}),
            ("state_security", "Государственная безопасность", "Стабильность растёт, исследования −10%",
             {"stability": 0.035, "unrest": -0.03, "research": -0.10}),
        ),
        (
            ("armaments_network", "Сеть военных заводов", "Военная сила +12%, промышленность +8",
             {"military": 0.12, "industry": 8, "upkeep": 0.08}),
            ("managed_labor", "Управляемый рынок труда", "Производство +12%, недовольство +0,02",
             {"production": 0.12, "unrest": 0.02}),
            ("internal_control", "Внутренний контроль", "Поддержка растёт, доход −8%",
             {"support": 0.035, "unrest": -0.035, "taxes": -0.08}),
        ),
        (
            ("total_rearmament", "Полное перевооружение", "Военная сила +22%, содержание +20%, стабильность −0,03",
             {"military": 0.22, "upkeep": 0.20, "stability": -0.03}),
            ("export_state", "Экспортная экономика", "Доход +14%, недовольство +0,025",
             {"taxes": 0.14, "production": 0.08, "unrest": 0.025}),
            ("security_apparatus", "Аппарат безопасности", "Недовольство снижается, политическая сила +12%",
             {"unrest": -0.04, "political_power": 0.12, "research": -0.06}),
        ),
    ),
    "monarchy": (
        (
            ("constitutional_compromise", "Конституционный компромисс", "Поддержка и стабильность растут, военная сила −6%",
             {"support": 0.04, "stability": 0.035, "military": -0.06}),
            ("royal_authority", "Укрепление короны", "Политическая сила +20%, недовольство +0,02",
             {"political_power": 0.20, "stability": 0.02, "unrest": 0.02}),
            ("imperial_economy", "Имперская экономика", "Доход +12%, содержание +8%",
             {"taxes": 0.12, "production": 0.08, "upkeep": 0.08}),
        ),
        (
            ("parliamentary_reforms", "Парламентские реформы", "Стабильность растёт, политическая сила −8%",
             {"stability": 0.035, "unrest": -0.02, "political_power": -0.08}),
            ("court_industry", "Промышленная хартия", "Производство +12%, поддержка −0,015",
             {"production": 0.12, "industry": 6, "support": -0.015}),
            ("royal_officers", "Королевский офицерский корпус", "Военная сила +15%, доход −6%",
             {"military": 0.15, "readiness": 0.04, "taxes": -0.06}),
        ),
        (
            ("civic_monarchy", "Ответственная монархия", "Поддержка растёт, недовольство снижается, доход −5%",
             {"support": 0.04, "unrest": -0.03, "taxes": -0.05}),
            ("dynastic_finance", "Династические финансы", "Доход +16%, недовольство +0,02",
             {"taxes": 0.16, "political_power": 0.08, "unrest": 0.02}),
            ("imperial_guard", "Имперская гвардия", "Военная сила +18%, содержание +14%",
             {"military": 0.18, "readiness": 0.04, "upkeep": 0.14}),
        ),
    ),
    "democracy": (
        (
            ("social_democracy", "Общественный договор", "Стабильность и поддержка растут, доход −8%",
             {"stability": 0.04, "support": 0.04, "taxes": -0.08}),
            ("market_liberalization", "Рыночная либерализация", "Производство и доход растут, недовольство +0,025",
             {"production": 0.14, "taxes": 0.12, "unrest": 0.025}),
            ("collective_defense", "Коллективная оборона", "Военная сила +14%, содержание +12%",
             {"military": 0.14, "political_power": 0.08, "upkeep": 0.12}),
        ),
        (
            ("public_housing", "Доступное жильё", "Поддержка и стабильность растут, производство −5%",
             {"support": 0.04, "stability": 0.03, "production": -0.05}),
            ("financial_services", "Финансовый сектор", "Доход +14%, стабильность −0,02",
             {"taxes": 0.14, "research": 0.08, "stability": -0.02}),
            ("reserve_service", "Резервная служба", "Боеготовность растёт, доход −6%",
             {"military": 0.10, "readiness": 0.05, "taxes": -0.06}),
        ),
        (
            ("universal_services", "Всеобщие общественные услуги", "Недовольство снижается, доход −8%",
             {"support": 0.04, "stability": 0.035, "unrest": -0.035, "taxes": -0.08}),
            ("global_finance", "Глобальные рынки капитала", "Доход +16%, недовольство +0,03",
             {"taxes": 0.16, "production": 0.10, "unrest": 0.03}),
            ("integrated_reserves", "Интегрированный военный резерв", "Военная сила +16%, содержание +15%",
             {"military": 0.16, "readiness": 0.06, "upkeep": 0.15}),
        ),
    ),
}

for _ideology_id, (_choices, _followups, _final_nodes) in IDEOLOGY_LATE_BRANCHES.items():
    _nodes = list(IDEOLOGY_TREES[_ideology_id])
    _endpoints = tuple(
        max(
            (node for node in _nodes if node["position"][0] == column),
            key=lambda node: node["position"][1],
        )["id"]
        for column in range(3)
    )
    _root_id = f"{_ideology_id}_national_program"
    _nodes.append({
        "id": _root_id,
        "name": "Национальная программа",
        "effect": "Открывает три взаимоисключающих направления",
        "cost": 180,
        "requires": _endpoints,
        "position": (1, 6),
        "bonuses": {"political_power": 0.05},
    })
    for _column, (_choice, _followup, _final) in enumerate(
        zip(_choices, _followups, _final_nodes)
    ):
        for _row, _item in enumerate((_choice, _followup, _final), start=7):
            _suffix, _name, _effect, _bonuses = _item
            _node = {
                "id": f"{_ideology_id}_{_suffix}",
                "name": _name,
                "effect": _effect,
                "cost": 135 + (_row - 7) * 55,
                "requires": (
                    (_root_id,) if _row == 7
                    else (f"{_ideology_id}_{(_choice, _followup, _final)[_row - 8][0]}",)
                ),
                "position": (_column, _row),
                "bonuses": _bonuses,
            }
            if _row == 7:
                _node["choice_group"] = f"{_ideology_id}_national_program"
            _nodes.append(_node)
    IDEOLOGY_TREES[_ideology_id] = tuple(_nodes)


LEGACY_IDEOLOGIES = {
    "balanced": "democracy",
    "market": "democracy",
    "welfare": "democracy",
    "mobilization": "fascism",
}


def migrate_ideology(country_id, ideology_id):
    if ideology_id in IDEOLOGIES or ideology_id in ZOMBIE_IDEOLOGIES:
        return ideology_id
    if ideology_id == "mobilization" and country_id in {"ussr", "china"}:
        return "communism"
    return LEGACY_IDEOLOGIES.get(ideology_id, "democracy")


def ideology_bonuses(ideology_id, upgrades):
    ideology = IDEOLOGIES.get(ideology_id) or ZOMBIE_IDEOLOGIES[ideology_id]
    nodes = IDEOLOGY_TREES.get(ideology_id) or ZOMBIE_IDEOLOGY_TREES[ideology_id]
    bonuses = dict(ideology["bonuses"])
    for node in nodes:
        if node["id"] not in upgrades:
            continue
        for key, value in node["bonuses"].items():
            bonuses[key] = bonuses.get(key, 0) + value
    return bonuses


def ideology_branch_locked(upgrades, ideology_id, doctrine_id):
    tree = IDEOLOGY_TREES.get(ideology_id) or ZOMBIE_IDEOLOGY_TREES.get(
        ideology_id, ()
    )
    node = next(
        (item for item in tree
         if item["id"] == doctrine_id),
        None,
    )
    if not node or not node.get("choice_group"):
        return False
    return any(
        item["id"] in upgrades
        and item.get("choice_group") == node["choice_group"]
        and item["id"] != doctrine_id
        for item in tree
    )


def adopt(country, ideology_id):
    ideologies = {**IDEOLOGIES, **ZOMBIE_IDEOLOGIES}
    if ideology_id not in ideologies:
        return False, "Неизвестная идеология"
    if country.ideology == ideology_id:
        return False, "Эта идеология уже действует"
    if country.government_support < 20:
        return False, "Недостаточно поддержки для смены идеологии"
    if country.money < 500 or country.political_power < 50:
        return False, "Для смены идеологии нужно 500 денег и 50 политической силы"
    country.money -= 500
    country.political_power -= 50
    country.government_support = max(0, country.government_support - 12)
    country.stability = max(0, country.stability - 4)
    country.unrest = min(100, country.unrest + 5)
    country.ideology = ideology_id
    return True, f"Принята идеология: {ideologies[ideology_id]['name']}"


def validate_development(country, doctrine_id, paid=False):
    ideology_trees = {**IDEOLOGY_TREES, **ZOMBIE_IDEOLOGY_TREES}
    for ideology_id, nodes in ideology_trees.items():
        node = next((item for item in nodes if item["id"] == doctrine_id), None)
        if node is None:
            continue
        if country.ideology != ideology_id:
            return False, "Для этой ветки нужно принять соответствующую идеологию"
        if doctrine_id in country.ideology_upgrades:
            return False, "Это развитие уже изучено"
        if ideology_branch_locked(country.ideology_upgrades, ideology_id, doctrine_id):
            return False, "Вы уже выбрали другое направление развития"
        if any(required not in country.ideology_upgrades for required in node["requires"]):
            return False, "Сначала изучите предыдущий уровень ветки"
        if not paid and country.political_power < node["cost"]:
            return False, f"Нужно политической силы: {node['cost']}"
        return True, node
    return False, "Развитие идеологии не найдено"


def develop(country, doctrine_id, paid=False):
    valid, result = validate_development(country, doctrine_id, paid=paid)
    if not valid:
        return False, result
    node = result
    if not paid:
        country.political_power -= node["cost"]
    country.ideology_upgrades.add(doctrine_id)
    if "industry" in node["bonuses"]:
        country.industry = min(100, country.industry + node["bonuses"]["industry"])
    if "development" in node["bonuses"]:
        country.development = min(
            100, country.development + node["bonuses"]["development"]
        )
    return True, f"Развитие завершено: {node['name']}"
