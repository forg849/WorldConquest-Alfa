ZOMBIE_IDEOLOGIES = {
    "z_emergency": {
        "name": "Чрезвычайное правительство",
        "description": "Сохраняет управление и координирует оборону.",
        "bonuses": {"stability": 0.015, "war_support": 0.02},
    },
    "z_science": {
        "name": "Научная мобилизация",
        "description": "Ставит исследования вакцин и лечения выше обычной экономики.",
        "bonuses": {"research": 0.12, "production": -0.03},
    },
    "z_defense": {
        "name": "Доктрина удержания",
        "description": "Укрепляет фронт и снабжение ценой внутренней нагрузки.",
        "bonuses": {"military": 0.08, "upkeep": 0.04},
    },
    "z_horde": {
        "name": "Коллективный инстинкт",
        "description": "Заражённые не ведут переговоров и действуют единой ордой.",
        "bonuses": {"military": 0.10, "war_support": 0.05},
    },
}


_IDEOLOGY_PATHS = {
    "z_emergency": (
        (
            ("civil_defense", "Гражданская оборона", "Стабильность и готовность выше",
             {"stability": 0.025, "readiness": 0.04}),
            ("security_council", "Чрезвычайный совет", "Военная сила +10%, политическая сила +8%",
             {"military": 0.10, "political_power": 0.08, "unrest": 0.01}),
            ("regional_militias", "Региональные ополчения", "Готовность +8%, содержание +5%",
             {"readiness": 0.08, "military": 0.05, "upkeep": 0.05}),
        ),
        (
            ("safe_corridors", "Безопасные коридоры", "Поддержка растёт, производство −4%",
             {"support": 0.035, "unrest": -0.025, "production": -0.04}),
            ("unified_command", "Единое командование", "Сила армии +14%, содержание +8%",
             {"military": 0.14, "readiness": 0.05, "upkeep": 0.08}),
            ("local_supply", "Местные склады снабжения", "Содержание −8%, доход −4%",
             {"upkeep": -0.08, "taxes": -0.04}),
        ),
        (
            ("evacuation_network", "Сеть эвакуации", "Стабильность растёт, доход −5%",
             {"stability": 0.03, "support": 0.025, "taxes": -0.05}),
            ("joint_operations", "Совместные операции", "Военная сила +16%, усталость войны выше",
             {"military": 0.16, "war_support": 0.025, "unrest": 0.015}),
            ("volunteer_reserves", "Добровольческий резерв", "Готовность и поддержка растут",
             {"readiness": 0.08, "support": 0.025, "political_power": 0.05}),
        ),
    ),
    "z_science": (
        (
            ("vaccine_program", "Программа вакцины", "Исследования +18%, доход −5%",
             {"research": 0.18, "taxes": -0.05}),
            ("biosecurity", "Биологическая безопасность", "Стабильность и сопротивляемость растут",
             {"stability": 0.03, "unrest": -0.025, "research": 0.06}),
            ("open_labs", "Открытые лаборатории", "Исследования +14%, поддержка −0,01 в день",
             {"research": 0.14, "production": 0.04, "support": -0.01}),
        ),
        (
            ("field_vaccine", "Полевые испытания", "Исследования +22%, содержание +4%",
             {"research": 0.22, "upkeep": 0.04}),
            ("screening_network", "Сеть раннего выявления", "Недовольство снижается, доход −4%",
             {"unrest": -0.035, "stability": 0.02, "taxes": -0.04}),
            ("research_exchange", "Обмен данными", "Исследования и доход растут",
             {"research": 0.12, "taxes": 0.05}),
        ),
        (
            ("mass_immunization", "Массовая иммунизация", "Поддержка и стабильность растут",
             {"support": 0.04, "stability": 0.025, "unrest": -0.02}),
            ("antiviral_stockpiles", "Запасы противовирусных средств", "Боеготовность +8%, содержание +6%",
             {"readiness": 0.08, "upkeep": 0.06, "war_support": 0.02}),
            ("global_cure", "Международный протокол лечения", "Исследования +20%, производство +6%",
             {"research": 0.20, "production": 0.06, "political_power": 0.05}),
        ),
    ),
    "z_defense": (
        (
            ("fortified_lines", "Укреплённые рубежи", "Военная сила +12%, содержание +6%",
             {"military": 0.12, "upkeep": 0.06}),
            ("mobile_columns", "Мобильные колонны", "Боеготовность и скорость операций выше",
             {"readiness": 0.10, "military": 0.06, "upkeep": 0.04}),
            ("scorched_zones", "Выжженные зоны", "Военная сила +16%, недовольство +0,02",
             {"military": 0.16, "war_support": 0.03, "unrest": 0.02}),
        ),
        (
            ("urban_strongholds", "Городские укрепрайоны", "Военная сила +14%, доход −5%",
             {"military": 0.14, "stability": 0.015, "taxes": -0.05}),
            ("rapid_redeployment", "Быстрая переброска", "Готовность +12%, содержание +8%",
             {"readiness": 0.12, "military": 0.06, "upkeep": 0.08}),
            ("controlled_retreat", "Плановый отход", "Потери снижаются, но поддержка падает",
             {"war_support": 0.035, "stability": 0.015, "support": -0.02}),
        ),
        (
            ("counteroffensive", "Контрнаступление", "Военная сила +18%, усталость войны выше",
             {"military": 0.18, "readiness": 0.06, "unrest": 0.02}),
            ("secure_supply", "Защищённые коммуникации", "Содержание −8%, исследования +5%",
             {"upkeep": -0.08, "research": 0.05}),
            ("perimeter_command", "Периметр обороны", "Стабильность +0,03, доход −4%",
             {"stability": 0.03, "support": 0.02, "taxes": -0.04}),
        ),
    ),
    "z_horde": (
        (
            ("swarm_instinct", "Инстинкт роя", "Военная сила +12%, готовность выше",
             {"military": 0.12, "readiness": 0.05}),
            ("hardened_hosts", "Устойчивые носители", "Усталость войны накапливается медленнее",
             {"military": 0.07, "war_exhaustion": -0.10, "upkeep": 0.04}),
            ("airborne_strain", "Воздушный штамм", "Сила орды выше, но управление ухудшается",
             {"military": 0.10, "stability": -0.02, "unrest": 0.02}),
        ),
        (
            ("coordinated_hordes", "Скоординированные орды", "Военная сила +16%, боеготовность выше",
             {"military": 0.16, "readiness": 0.06}),
            ("regenerative_strain", "Регенеративный штамм", "Орда сильнее, содержание выше",
             {"military": 0.13, "upkeep": 0.08}),
            ("spore_dispersal", "Рассеивание спор", "Распространение ускоряется, стабильность −0,03",
             {"military": 0.08, "stability": -0.03, "unrest": 0.03}),
        ),
        (
            ("endless_horde", "Бесконечная орда", "Военная сила +18%, поддержка +0,03",
             {"military": 0.18, "war_support": 0.03, "upkeep": 0.08}),
            ("adaptive_mutations", "Адаптивные мутации", "Армия лучше приспосабливается к потерям",
             {"military": 0.15, "readiness": 0.08, "unrest": 0.02}),
            ("global_outbreak", "Глобальная вспышка", "Военная сила +20%, снабжение дороже",
             {"military": 0.20, "upkeep": 0.12, "stability": -0.04}),
        ),
    ),
}

ZOMBIE_IDEOLOGY_TREES = {}
for _ideology_id, _paths in _IDEOLOGY_PATHS.items():
    _root_id = f"{_ideology_id}_emergency_program"
    _nodes = [{
        "id": _root_id,
        "name": "Национальная программа",
        "effect": "Открывает три взаимоисключающих направления",
        "cost": 55,
        "requires": (),
        "position": (1, 0),
        "bonuses": {"political_power": 0.04},
    }]
    for _column, path in enumerate(_paths):
        _previous_id = _root_id
        for _row, (suffix, name, effect, bonuses) in enumerate(path, 1):
            node_id = f"{_ideology_id}_{suffix}"
            node = {
                "id": node_id,
                "name": name,
                "effect": effect,
                "cost": 65 + _row * 35,
                "requires": (_previous_id,),
                "position": (_column, _row),
                "bonuses": bonuses,
            }
            if _row == 1:
                node["choice_group"] = f"{_ideology_id}_response"
            _nodes.append(node)
            _previous_id = node_id
    ZOMBIE_IDEOLOGY_TREES[_ideology_id] = tuple(_nodes)


SURVIVOR_TECH_TREE = (
    {"id": "survivor_network", "name": "Объединённая сеть выживания", "short": "Сеть выживания",
     "cost": 650, "points": 18, "requires": (), "effect": "Политическая сила и стабильность растут",
     "position": (1, 0), "bonuses": {"political_power": 0.08, "stability": 0.01}},
    {"id": "survivor_vaccine", "name": "Программа вакцины", "short": "Вакцина",
     "cost": 900, "points": 25, "requires": ("survivor_network",),
     "choice_group": "survivor_strategy", "effect": "Исследования +18%, доход −4%",
     "position": (0, 1), "bonuses": {"research": 0.18, "taxes": -0.04}},
    {"id": "survivor_quarantine", "name": "Континентальные карантины", "short": "Карантин",
     "cost": 900, "points": 24, "requires": ("survivor_network",),
     "choice_group": "survivor_strategy", "effect": "Сила армии +12%, содержание +8%",
     "position": (1, 1), "bonuses": {"military": 0.12, "upkeep": 0.08}},
    {"id": "survivor_mobile_force", "name": "Мобильные группы реагирования", "short": "Мобильные группы",
     "cost": 950, "points": 26, "requires": ("survivor_network",),
     "choice_group": "survivor_strategy", "effect": "Готовность +12%, производство +5%",
     "position": (2, 1), "bonuses": {"readiness": 0.12, "production": 0.05}},
    {"id": "survivor_field_trials", "name": "Полевые испытания", "short": "Полевые испытания",
     "cost": 1300, "points": 36, "requires": ("survivor_vaccine",),
     "effect": "Исследования +22%, содержание +4%",
     "position": (0, 2), "bonuses": {"research": 0.22, "upkeep": 0.04}},
    {"id": "survivor_immunization", "name": "Массовая иммунизация", "short": "Иммунизация",
     "cost": 1800, "points": 48, "requires": ("survivor_field_trials",),
     "effect": "Поддержка и стабильность растут, доход −5%",
     "position": (0, 3), "bonuses": {"support": 0.04, "stability": 0.03, "taxes": -0.05}},
    {"id": "survivor_fortified_routes", "name": "Укреплённые коридоры", "short": "Укреплённые коридоры",
     "cost": 1300, "points": 36, "requires": ("survivor_quarantine",),
     "effect": "Военная сила +16%, недовольство +0,015",
     "position": (1, 2), "bonuses": {"military": 0.16, "unrest": 0.015}},
    {"id": "survivor_perimeter", "name": "Непрерывный периметр", "short": "Периметр",
     "cost": 1800, "points": 48, "requires": ("survivor_fortified_routes",),
     "effect": "Военная сила +18%, боеготовность выше, содержание +8%",
     "position": (1, 3), "bonuses": {"military": 0.18, "readiness": 0.06, "upkeep": 0.08}},
    {"id": "survivor_rapid_deployment", "name": "Экспедиционные колонны", "short": "Экспедиционные колонны",
     "cost": 1350, "points": 38, "requires": ("survivor_mobile_force",),
     "effect": "Готовность +14%, военная сила +8%",
     "position": (2, 2), "bonuses": {"readiness": 0.14, "military": 0.08}},
    {"id": "survivor_global_counteroffensive", "name": "Глобальное контрнаступление", "short": "Контрнаступление",
     "cost": 1900, "points": 52, "requires": ("survivor_rapid_deployment",),
     "effect": "Военная сила +20%, усталость войны растёт быстрее",
     "position": (2, 3), "bonuses": {"military": 0.20, "war_support": 0.04, "unrest": 0.02}},
)


ZOMBIE_TECH_TREE = (
    {"id": "strain_adaptation", "name": "Адаптация патогена", "short": "Адаптация",
     "cost": 700, "points": 18, "requires": (), "effect": "Орда крепче, содержание растёт",
     "position": (1, 0), "bonuses": {"military": 0.08, "upkeep": 0.04}},
    {"id": "strain_swarming", "name": "Стратегия роя", "short": "Стратегия роя",
     "cost": 950, "points": 25, "requires": ("strain_adaptation",),
     "choice_group": "strain_evolution", "effect": "Военная сила +16%, готовность выше",
     "position": (0, 1), "bonuses": {"military": 0.16, "readiness": 0.06}},
    {"id": "strain_resilience", "name": "Устойчивые носители", "short": "Устойчивые носители",
     "cost": 950, "points": 25, "requires": ("strain_adaptation",),
     "choice_group": "strain_evolution", "effect": "Сила и устойчивость армии выше",
     "position": (1, 1), "bonuses": {"military": 0.10, "war_exhaustion": -0.12}},
    {"id": "strain_spores", "name": "Споровое распространение", "short": "Споровый штамм",
     "cost": 1000, "points": 27, "requires": ("strain_adaptation",),
     "choice_group": "strain_evolution", "effect": "Сила орды выше, стабильность падает",
     "position": (2, 1), "bonuses": {"military": 0.12, "stability": -0.02, "unrest": 0.02}},
    {"id": "horde_coordination", "name": "Координация заражённых", "short": "Координация",
     "cost": 1400, "points": 38, "requires": ("strain_swarming",),
     "effect": "Сила и готовность выше",
     "position": (0, 2), "bonuses": {"military": 0.16, "readiness": 0.08}},
    {"id": "horde_regeneration", "name": "Регенеративный штамм", "short": "Регенерация",
     "cost": 1400, "points": 38, "requires": ("strain_resilience",),
     "effect": "Орда сильнее, содержание дороже",
     "position": (1, 2), "bonuses": {"military": 0.15, "upkeep": 0.08}},
    {"id": "horde_airborne", "name": "Аэрозольное заражение", "short": "Аэрозоль",
     "cost": 1450, "points": 40, "requires": ("strain_spores",),
     "effect": "Сила орды +18%, стабильность −0,03",
     "position": (2, 2), "bonuses": {"military": 0.18, "stability": -0.03}},
    {"id": "horde_endless", "name": "Бесконечная волна", "short": "Бесконечная волна",
     "cost": 1900, "points": 52, "requires": ("horde_coordination",),
     "effect": "Военная сила +20%, содержание +12%",
     "position": (0, 3), "bonuses": {"military": 0.20, "upkeep": 0.12}},
    {"id": "horde_adaptive", "name": "Адаптивная мутация", "short": "Адаптивная мутация",
     "cost": 1900, "points": 52, "requires": ("horde_regeneration",),
     "effect": "Военная сила +18%, готовность +8%",
     "position": (1, 3), "bonuses": {"military": 0.18, "readiness": 0.08}},
    {"id": "horde_global", "name": "Глобальная вспышка", "short": "Глобальная вспышка",
     "cost": 2000, "points": 55, "requires": ("horde_airborne",),
     "effect": "Военная сила +22%, содержание +15%",
     "position": (2, 3), "bonuses": {"military": 0.22, "upkeep": 0.15}},
)


def ideology_options(scenario_id, country_id):
    if scenario_id != "zombie":
        from .ideology import IDEOLOGIES
        return IDEOLOGIES
    if country_id == "zombies":
        return {"z_horde": ZOMBIE_IDEOLOGIES["z_horde"]}
    return {
        key: value for key, value in ZOMBIE_IDEOLOGIES.items()
        if key != "z_horde"
    }


def ideology_tree(ideology_id):
    return ZOMBIE_IDEOLOGY_TREES.get(ideology_id)


def technology_tree(scenario_id, country_id):
    if scenario_id != "zombie":
        from .technology import TECH_TREE
        return TECH_TREE
    return ZOMBIE_TECH_TREE if country_id == "zombies" else SURVIVOR_TECH_TREE
