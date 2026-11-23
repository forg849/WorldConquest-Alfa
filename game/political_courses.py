POLITICAL_COURSES = (
    {
        "id": "national_reconstruction",
        "name": "Национальное восстановление",
        "description": "Единая программа восстановления институтов и инфраструктуры.",
        "cost": 700,
        "political_power": 120,
        "days": 25,
        "requires": (),
        "position": (1, 0),
        "bonuses": {"production": 0.04, "stability": 0.01},
        "immediate": {"stability": 3, "unrest": -2},
    },
    {
        "id": "industrial_mobilization",
        "name": "Индустриальный рывок",
        "description": "Ускоряет промышленный выпуск ценой части налоговых поступлений.",
        "cost": 950,
        "political_power": 160,
        "days": 35,
        "requires": ("national_reconstruction",),
        "choice_group": "national_model",
        "position": (0, 1),
        "bonuses": {"production": 0.10, "taxes": -0.03, "military": 0.04},
        "immediate": {"industry": 6},
    },
    {
        "id": "social_contract",
        "name": "Общественный договор",
        "description": "Повышает поддержку и снижает недовольство за счёт бюджета.",
        "cost": 1000,
        "political_power": 170,
        "days": 40,
        "requires": ("national_reconstruction",),
        "choice_group": "national_model",
        "position": (1, 1),
        "bonuses": {"stability": 0.025, "support": 0.025, "taxes": -0.08, "unrest": -0.02},
        "immediate": {"government_support": 5, "unrest": -4},
    },
    {
        "id": "fiscal_reform",
        "name": "Финансовая либерализация",
        "description": "Увеличивает доходы и исследования, но повышает внутреннее напряжение.",
        "cost": 900,
        "political_power": 180,
        "days": 32,
        "requires": ("national_reconstruction",),
        "choice_group": "national_model",
        "position": (2, 1),
        "bonuses": {"taxes": 0.14, "research": 0.08, "stability": -0.02, "unrest": 0.02},
        "immediate": {"economy_level": 1},
    },
    {
        "id": "leadership_mandate",
        "name": "Новый политический мандат",
        "description": "Сменяет руководство государства и укрепляет общественную легитимность.",
        "cost": 850,
        "political_power": 140,
        "days": 30,
        "requires": ("national_reconstruction",),
        "position": (3, 1),
        "bonuses": {"support": 0.015, "stability": 0.01, "political_power": 0.04},
        "immediate": {"government_support": 6, "stability": 4},
        "change_leader": True,
    },
    {
        "id": "strategic_industry",
        "name": "Стратегическая промышленность",
        "description": "Создаёт резерв для армии и повышает выпуск, увеличивая содержание.",
        "cost": 1350,
        "political_power": 210,
        "days": 45,
        "requires": ("industrial_mobilization",),
        "position": (0, 2),
        "bonuses": {"military": 0.10, "production": 0.10, "upkeep": 0.08, "unrest": 0.01},
        "immediate": {"industry": 8, "army_readiness": 5},
    },
    {
        "id": "universal_welfare",
        "name": "Всеобщие общественные службы",
        "description": "Укрепляет стабильность, поддержку и устойчивость населения.",
        "cost": 1250,
        "political_power": 220,
        "days": 45,
        "requires": ("social_contract",),
        "position": (1, 2),
        "bonuses": {"stability": 0.03, "support": 0.03, "unrest": -0.03, "taxes": -0.06},
        "immediate": {"government_support": 7, "stability": 5},
    },
    {
        "id": "export_economy",
        "name": "Экспортная экономика",
        "description": "Расширяет налоговую базу, повышая нагрузку на общество.",
        "cost": 1300,
        "political_power": 230,
        "days": 42,
        "requires": ("fiscal_reform",),
        "position": (2, 2),
        "bonuses": {"taxes": 0.16, "production": 0.08, "unrest": 0.025},
        "immediate": {"economy_level": 1, "development": 4},
    },
    {
        "id": "molotov_ribbentrop_pact",
        "name": "Пакт о ненападении с Германией",
        "description": "Секретное соглашение: временное ненападение и улучшение отношений.",
        "cost": 1600,
        "political_power": 250,
        "days": 60,
        "requires": (),
        "position": (4, 1),
        "scenario": "ww2",
        "country": "ussr",
        "partner": "germany",
        "min_year": 1939,
        "bonuses": {"political_power": 0.05},
        "immediate": {},
        "pact_days": 365,
        "pact_type": "non_aggression",
        "partner_bonuses": {"political_power": 0.04},
        "relation_change": 30,
    },
    {
        "id": "steel_pact",
        "name": "Стальной пакт",
        "description": "Союз Германии и Италии: общая оборона и координация промышленности.",
        "cost": 1450,
        "political_power": 230,
        "days": 45,
        "requires": (),
        "position": (4, 2),
        "scenario": "ww2",
        "country": "germany",
        "partner": "italy",
        "min_year": 1939,
        "pact_type": "alliance",
        "bonuses": {"military": 0.08, "production": 0.05, "upkeep": 0.04},
        "partner_bonuses": {"military": 0.06, "readiness": 0.04},
        "immediate": {"army_readiness": 5},
        "partner_immediate": {"army_readiness": 4},
        "relation_change": 30,
    },
    {
        "id": "atlantic_charter",
        "name": "Атлантическая хартия",
        "description": "Оборонный союз США и Британии с общей логистикой и научным обменом.",
        "cost": 1800,
        "political_power": 270,
        "days": 50,
        "requires": (),
        "position": (4, 3),
        "scenario": "ww2",
        "country": "usa",
        "partner": "uk",
        "min_year": 1941,
        "pact_type": "alliance",
        "bonuses": {"production": 0.05, "research": 0.08, "military": 0.05},
        "partner_bonuses": {"production": 0.05, "research": 0.06, "readiness": 0.04},
        "immediate": {"army_readiness": 4},
        "partner_immediate": {"army_readiness": 4},
        "relation_change": 35,
    },
    {
        "id": "european_recovery_compact",
        "name": "Европейский пакт восстановления",
        "description": "Торговый договор Франции и Германии: рост выпуска и совместные инвестиции.",
        "cost": 1600,
        "political_power": 240,
        "days": 40,
        "requires": (),
        "position": (4, 4),
        "scenario": "modern",
        "country": "france",
        "partner": "germany",
        "pact_type": "trade",
        "treaty_days": 730,
        "bonuses": {"taxes": 0.08, "production": 0.06},
        "partner_bonuses": {"taxes": 0.06, "production": 0.05, "research": 0.04},
        "immediate": {"development": 3},
        "partner_immediate": {"development": 2},
        "relation_change": 25,
    },
    {
        "id": "pacific_trade_accord",
        "name": "Тихоокеанское торговое соглашение",
        "description": "США и Япония открывают рынки и обмениваются гражданскими технологиями.",
        "cost": 1750,
        "political_power": 250,
        "days": 40,
        "requires": (),
        "position": (4, 5),
        "scenario": "modern",
        "country": "usa",
        "partner": "japan",
        "pact_type": "trade",
        "treaty_days": 730,
        "bonuses": {"taxes": 0.07, "research": 0.06},
        "partner_bonuses": {"taxes": 0.07, "production": 0.06},
        "immediate": {"development": 2},
        "partner_immediate": {"development": 2},
        "relation_change": 20,
    },
)

ZOMBIE_POLITICAL_COURSES = (
    {
        "id": "outbreak_emergency_command",
        "name": "Единое командование кризисом",
        "description": "Сводит гражданскую и военную координацию в общий штаб.",
        "cost": 900, "political_power": 110, "days": 18,
        "requires": (), "position": (1, 0), "scenario": "zombie",
        "bonuses": {"military": 0.04, "stability": 0.015},
        "immediate": {"army_readiness": 5, "government_support": 3},
    },
    {
        "id": "outbreak_vaccine_program",
        "name": "Национальная программа вакцины",
        "description": "Финансирует лаборатории и массовый поиск устойчивости.",
        "cost": 1250, "political_power": 155, "days": 28,
        "requires": ("outbreak_emergency_command",),
        "position": (0, 1),
        "scenario": "zombie",
        "bonuses": {"research": 0.12, "taxes": -0.035},
        "immediate": {"research_points": 12},
    },
    {
        "id": "outbreak_quarantine_network",
        "name": "Континентальные карантины",
        "description": "Укрепляет рубежи, ограничивая торговлю и передвижение.",
        "cost": 1200, "political_power": 150, "days": 25,
        "requires": ("outbreak_emergency_command",),
        "position": (1, 1),
        "scenario": "zombie",
        "bonuses": {"military": 0.10, "upkeep": 0.06, "production": -0.03},
        "immediate": {"army_readiness": 7},
    },
    {
        "id": "outbreak_evacuation_network",
        "name": "Сеть эвакуационных коридоров",
        "description": "Снижает общественную напряжённость ценой бюджетных расходов.",
        "cost": 1150, "political_power": 145, "days": 24,
        "requires": ("outbreak_emergency_command",),
        "position": (2, 1),
        "scenario": "zombie",
        "bonuses": {"stability": 0.025, "support": 0.025, "taxes": -0.05},
        "immediate": {"unrest": -5, "government_support": 5},
    },
    {
        "id": "outbreak_field_trials",
        "name": "Полевые испытания вакцины",
        "description": "Ускоряет исследования, увеличивая содержание институтов.",
        "cost": 1600, "political_power": 195, "days": 35,
        "requires": ("outbreak_vaccine_program",), "position": (0, 2),
        "scenario": "zombie",
        "bonuses": {"research": 0.16, "upkeep": 0.04},
        "immediate": {"research_points": 20},
    },
    {
        "id": "outbreak_global_immunization",
        "name": "План массовой иммунизации",
        "description": "Снижает недовольство и укрепляет доверие общества.",
        "cost": 2100, "political_power": 245, "days": 42,
        "requires": ("outbreak_field_trials",), "position": (0, 3),
        "scenario": "zombie",
        "bonuses": {"support": 0.035, "stability": 0.025, "unrest": -0.025},
        "immediate": {"government_support": 7, "unrest": -6},
    },
    {
        "id": "outbreak_fortified_corridors",
        "name": "Укреплённые коридоры снабжения",
        "description": "Усиливает оборону важных маршрутов, повышая её цену.",
        "cost": 1550, "political_power": 185, "days": 32,
        "requires": ("outbreak_quarantine_network",), "position": (1, 2),
        "scenario": "zombie",
        "bonuses": {"military": 0.12, "readiness": 0.05, "upkeep": 0.07},
        "immediate": {"army_readiness": 5},
    },
    {
        "id": "outbreak_counteroffensive",
        "name": "Континентальное контрнаступление",
        "description": "Повышает боеспособность, усиливая нагрузку от войны.",
        "cost": 2200, "political_power": 260, "days": 45,
        "requires": ("outbreak_fortified_corridors",), "position": (1, 3),
        "scenario": "zombie",
        "bonuses": {"military": 0.16, "readiness": 0.06, "unrest": 0.015},
        "immediate": {"army_readiness": 8, "war_support": 5},
    },
    {
        "id": "outbreak_civil_defense",
        "name": "Гражданская защита населения",
        "description": "Снижает потери стабильности и повышает поддержку.",
        "cost": 1500, "political_power": 180, "days": 30,
        "requires": ("outbreak_evacuation_network",), "position": (2, 2),
        "scenario": "zombie",
        "bonuses": {"stability": 0.025, "support": 0.03, "unrest": -0.02},
        "immediate": {"stability": 4, "government_support": 5},
    },
    {
        "id": "outbreak_joint_operations",
        "name": "Международные совместные операции",
        "description": "Объединяет армии и исследовательские центры союзников.",
        "cost": 2150, "political_power": 255, "days": 44,
        "requires": ("outbreak_civil_defense",), "position": (2, 3),
        "scenario": "zombie",
        "bonuses": {"military": 0.10, "research": 0.10, "political_power": 0.05},
        "immediate": {"army_readiness": 7, "research_points": 15},
    },
    {
        "id": "horde_mutation_program",
        "name": "Программа адаптации орды",
        "description": "Ускоряет эволюцию заражённых и усиливает наступление.",
        "cost": 900, "political_power": 110, "days": 20,
        "requires": (), "position": (3, 0), "scenario": "zombie",
        "country": "zombies",
        "bonuses": {"military": 0.06, "readiness": 0.03},
        "immediate": {"army_readiness": 4},
    },
    {
        "id": "horde_swarm_tactics",
        "name": "Тактика бесконечного роя",
        "description": "Повышает натиск орды ценой управляемости.",
        "cost": 1450, "political_power": 170, "days": 30,
        "requires": ("horde_mutation_program",),
        "choice_group": "horde_evolution", "position": (2, 1),
        "scenario": "zombie", "country": "zombies",
        "bonuses": {"military": 0.12, "war_support": 0.03, "unrest": 0.01},
        "immediate": {},
    },
    {
        "id": "horde_hardened_hosts",
        "name": "Устойчивые носители",
        "description": "Снижает влияние потерь и усиливает восстановление армии.",
        "cost": 1450, "political_power": 170, "days": 30,
        "requires": ("horde_mutation_program",),
        "choice_group": "horde_evolution", "position": (3, 1),
        "scenario": "zombie", "country": "zombies",
        "bonuses": {"military": 0.08, "war_exhaustion": -0.10},
        "immediate": {},
    },
)

COURSES_BY_ID = {
    course["id"]: course
    for course in POLITICAL_COURSES + ZOMBIE_POLITICAL_COURSES
}


def political_courses_for(scenario_id, country_id=None):
    courses = (
        ZOMBIE_POLITICAL_COURSES
        if scenario_id == "zombie" else POLITICAL_COURSES
    )
    if country_id:
        return tuple(
            course for course in courses
            if not course.get("country") or course["country"] == country_id
        )
    return courses


def political_course_bonuses(completed_courses):
    bonuses = {}
    for course_id in completed_courses:
        course = COURSES_BY_ID.get(course_id)
        if not course:
            continue
        if course.get("pact_type"):
            continue
        for key, value in course["bonuses"].items():
            bonuses[key] = bonuses.get(key, 0) + value
    return bonuses


def course_branch_locked(completed_courses, course_id):
    course = COURSES_BY_ID.get(course_id)
    if not course or not course.get("choice_group"):
        return False
    return any(
        other_id != course_id
        and other.get("choice_group") == course["choice_group"]
        and other_id in completed_courses
        for other_id, other in COURSES_BY_ID.items()
    )


def course_available(world, country, course_id):
    course = COURSES_BY_ID.get(course_id)
    if (
        not course
        or course not in political_courses_for(world.scenario_id, country.id)
        or course_id in country.political_policies
        or country.active_political_course
        or course_branch_locked(country.political_policies, course_id)
        or any(required not in country.political_policies for required in course["requires"])
    ):
        return False
    if course.get("country") and country.id != course["country"]:
        return False
    if course.get("scenario") and world.scenario_id != course["scenario"]:
        return False
    if world.scenario_id == "zombie" and course.get("scenario") != "zombie":
        return False
    if course.get("min_year") and world.year < course["min_year"]:
        return False
    partner_id = course.get("partner")
    if partner_id:
        partner = world.countries.get(partner_id)
        if not partner or partner.is_defeated or world.war_between(country.id, partner_id):
            return False
        if partner.pacts.get(country.id, 0) > world.absolute_day():
            return False
        pact_type = course.get("pact_type", "non_aggression")
        if pact_type == "alliance" and (
            country.alliance or partner.alliance or country.wars or partner.wars
        ):
            return False
        if (
            pact_type == "trade"
            and (
                country.id in partner.treaties
                or partner_id in country.treaties
            )
        ):
            return False
    return True
