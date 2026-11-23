EMERGENCY_MEASURE_TREE = (
    {
        "id": "emergency_crisis_headquarters",
        "name": "Международный кризисный штаб",
        "short": "Кризисный штаб",
        "effect": "Политическая сила +5%, координация мер",
        "cost": 850,
        "points": 10,
        "days": 10,
        "requires": (),
        "position": (1, 0),
        "bonuses": {"political_power": 0.05},
    },
    {
        "id": "emergency_airspace_control",
        "name": "Ограничение воздушного пространства",
        "short": "Воздушный кордон",
        "effect": "Вероятность катастрофического заражения −20%, производство −3%",
        "cost": 1100,
        "points": 14,
        "days": 14,
        "requires": ("emergency_crisis_headquarters",),
        "position": (0, 1),
        "bonuses": {
            "outbreak_event_reduction": 0.20,
            "production": -0.03,
        },
    },
    {
        "id": "emergency_maritime_quarantine",
        "name": "Морской карантин",
        "short": "Морской карантин",
        "effect": "Морские прорывы реже на 25%, торговый доход −5%",
        "cost": 1250,
        "points": 16,
        "days": 16,
        "requires": ("emergency_crisis_headquarters",),
        "position": (1, 1),
        "bonuses": {
            "sea_breach_reduction": 0.25,
            "taxes": -0.05,
            "upkeep": 0.03,
        },
    },
    {
        "id": "emergency_full_readiness",
        "name": "Полная боевая готовность",
        "short": "Боевая готовность",
        "effect": "Военная сила +15%, содержание +12%, недовольство растёт",
        "cost": 1400,
        "points": 18,
        "days": 18,
        "requires": ("emergency_crisis_headquarters",),
        "position": (2, 1),
        "bonuses": {
            "military": 0.15,
            "readiness": 0.06,
            "upkeep": 0.12,
            "unrest": 0.015,
        },
    },
    {
        "id": "emergency_core_quarantine",
        "name": "Карантин ключевых столиц",
        "short": "Защита столиц",
        "effect": "Кризисные вспышки реже затрагивают столицы, производство −6%",
        "cost": 1550,
        "points": 20,
        "days": 20,
        "requires": ("emergency_airspace_control",),
        "position": (0, 2),
        "bonuses": {
            "core_outbreak_reduction": 0.75,
            "production": -0.06,
            "unrest": 0.006,
        },
    },
    {
        "id": "emergency_medical_mobilization",
        "name": "Мобилизация медицинской науки",
        "short": "Медицинская наука",
        "effect": "Исследования +15%, налоговый доход −4%",
        "cost": 1450,
        "points": 18,
        "days": 18,
        "requires": ("emergency_crisis_headquarters",),
        "position": (3, 1),
        "bonuses": {
            "research": 0.15,
            "taxes": -0.04,
        },
    },
    {
        "id": "emergency_global_coordination",
        "name": "Глобальная координация",
        "short": "Общий протокол",
        "effect": "Вспышки реже, исследования +8%, содержание +5%",
        "cost": 1900,
        "points": 24,
        "days": 24,
        "requires": (
            "emergency_maritime_quarantine",
            "emergency_medical_mobilization",
        ),
        "position": (2, 2),
        "bonuses": {
            "outbreak_event_reduction": 0.15,
            "research": 0.08,
            "upkeep": 0.05,
        },
    },
    {
        "id": "emergency_evacuation_corridors",
        "name": "Коридоры эвакуации",
        "short": "Эвакуационные коридоры",
        "effect": "Случайные вспышки реже на 12%, производство −2%, недовольство растёт медленнее",
        "cost": 1350,
        "points": 17,
        "days": 17,
        "requires": ("emergency_core_quarantine",),
        "position": (0, 3),
        "bonuses": {
            "outbreak_event_reduction": 0.12,
            "production": -0.02,
            "unrest": -0.006,
        },
    },
    {
        "id": "emergency_mobile_laboratories",
        "name": "Мобильные лаборатории",
        "short": "Мобильные лаборатории",
        "effect": "Исследования +12%, налоговый доход −3%",
        "cost": 1600,
        "points": 20,
        "days": 20,
        "requires": ("emergency_medical_mobilization",),
        "position": (1, 3),
        "bonuses": {
            "research": 0.12,
            "taxes": -0.03,
        },
    },
    {
        "id": "emergency_import_labor_force",
        "name": "Импорт рабочей силы",
        "short": "Исследование заражённых",
        "effect": "Закупка заражённых у Китая. 60% — авария в Калифорнии; 40% — боеготовность заражённых −10% на полгода",
        "cost": 2100,
        "points": 28,
        "days": 28,
        "requires": (
            "emergency_crisis_headquarters",
            "emergency_medical_mobilization",
        ),
        "required_region": "usa_admin1_USA-3521",
        "required_region_owner": "usa",
        "position": (2, 3),
        "bonuses": {},
    },
    {
        "id": "emergency_civil_defense_reserves",
        "name": "Резервы гражданской обороны",
        "short": "Гражданская оборона",
        "effect": "Боеготовность +4%, содержание +4%, недовольство растёт медленнее",
        "cost": 1750,
        "points": 22,
        "days": 22,
        "requires": (
            "emergency_core_quarantine",
            "emergency_full_readiness",
        ),
        "position": (3, 3),
        "bonuses": {
            "readiness": 0.04,
            "upkeep": 0.04,
            "unrest": -0.005,
        },
    },
    {
        "id": "emergency_international_evacuation",
        "name": "Международная эвакуация",
        "short": "Международная эвакуация",
        "effect": "50% — военная сила всех стран людей +10%; 50% — вспышки в 7 случайных регионах мира",
        "cost": 2800,
        "points": 36,
        "days": 35,
        "requires": (
            "emergency_evacuation_corridors",
            "emergency_mobile_laboratories",
        ),
        "global_once": True,
        "position": (2, 4),
        "bonuses": {},
    },
    {
        "id": "emergency_continental_watch",
        "name": "Континентальная система наблюдения",
        "short": "Континентальное наблюдение",
        "effect": "Вероятность случайных вспышек −15%, исследования +8%, производство −3%",
        "cost": 2200,
        "points": 28,
        "days": 28,
        "requires": (
            "emergency_airspace_control",
            "emergency_global_coordination",
        ),
        "position": (3, 2),
        "bonuses": {
            "outbreak_event_reduction": 0.15,
            "research": 0.08,
            "production": -0.03,
        },
    },
    {
        "id": "emergency_rapid_response_units",
        "name": "Мобильные группы быстрого реагирования",
        "short": "Группы реагирования",
        "effect": "Военная сила +8%, содержание +5%, боеготовность +3%",
        "cost": 2300,
        "points": 29,
        "days": 29,
        "requires": (
            "emergency_full_readiness",
            "emergency_mobile_laboratories",
        ),
        "position": (0, 4),
        "bonuses": {
            "military": 0.08,
            "upkeep": 0.05,
            "readiness": 0.03,
        },
    },
    {
        "id": "emergency_recovery_fund",
        "name": "Международный фонд восстановления",
        "short": "Фонд восстановления",
        "effect": "Налоговый доход +5%, политическая сила +5%, исследования −3%",
        "cost": 2450,
        "points": 31,
        "days": 31,
        "requires": (
            "emergency_global_coordination",
            "emergency_evacuation_corridors",
        ),
        "position": (1, 4),
        "bonuses": {
            "taxes": 0.05,
            "political_power": 0.05,
            "research": -0.03,
        },
    },
)

EMERGENCY_MEASURES_BY_ID = {
    item["id"]: item for item in EMERGENCY_MEASURE_TREE
}


def emergency_measure_bonuses(measures):
    bonuses = {}
    for measure_id in measures:
        measure = EMERGENCY_MEASURES_BY_ID.get(measure_id)
        if not measure:
            continue
        for key, value in measure["bonuses"].items():
            bonuses[key] = bonuses.get(key, 0) + value
    return bonuses


def emergency_measure_available(country, measure_id, world=None):
    measure = EMERGENCY_MEASURES_BY_ID.get(measure_id)
    if not measure:
        return False, "Экстренная мера не найдена"
    required_region = measure.get("required_region")
    if required_region and (
        not world
        or required_region not in world.provinces_by_id
        or world.provinces_by_id[required_region].owner
        != measure.get("required_region_owner", country.id)
    ):
        return False, "Для операции Калифорния должна оставаться под контролем США"
    if measure.get("global_once"):
        if not world:
            return False, "Для этой меры требуется глобальное состояние кампании"
        if world.international_evacuation_result is not None:
            return False, "Международная эвакуация уже завершена"
        if any(
            country.active_upgrade
            and country.active_upgrade.get("kind") == "emergency_measure"
            and country.active_upgrade.get("id") == measure_id
            for country in world.countries.values()
        ):
            return False, "Международная эвакуация уже готовится"
    if measure_id in country.emergency_measures:
        return False, "Эта мера уже введена"
    if country.active_upgrade:
        return False, "Сначала дождитесь завершения текущей прокачки"
    if any(
        required not in country.emergency_measures
        for required in measure["requires"]
    ):
        return False, "Сначала завершите предыдущую меру"
    if country.money < measure["cost"]:
        return False, f"Нужно денег: {measure['cost']}"
    if country.research_points < measure["points"]:
        return False, f"Нужно очков исследований: {measure['points']}"
    return True, measure
