DECISION_EVENTS = (
    {
        "id": "france_quarantine_resistance",
        "title": "Сопротивление во французских карантинных зонах",
        "description": (
            "В заражённых районах Франции начались бои. Правительство "
            "Европейского союза просит выбрать дальнейшие действия."
        ),
        "country": "eu",
        "choices": (
            {
                "name": "Зачистить карантинные зоны",
                "consequence": (
                    "Заражённым достанутся 5 регионов; население −30 тыс., "
                    "военная сила −3%, политическая сила +10, недовольство +2%."
                ),
                "effects": {
                    "lose_regions": 5, "population": -30000,
                    "military_strength": -0.03, "political_power": 10,
                    "unrest": 2,
                },
            },
            {
                "name": "Укрепить карантинные зоны",
                "consequence": (
                    "Заражённым достанутся 5 регионов; военная сила +20%, "
                    "недовольство −20%, рост недовольства −5%, "
                    "политическая сила +50, казна −2000."
                ),
                "effects": {
                    "lose_regions": 5, "military_strength": 0.20,
                    "unrest": -20, "unrest_growth": -0.05,
                    "political_power": 50, "money": -2000,
                },
            },
        ),
    },
    {
        "id": "refugee_corridor",
        "title": "Гуманитарный коридор для беженцев",
        "description": "Соседние страны просят открыть безопасный путь эвакуации.",
        "choices": (
            {
                "name": "Открыть коридор",
                "consequence": "Стабильность +5; риск 35%: вспышка в одном регионе.",
                "effects": {"stability": 5, "money": -450},
                "risk": {
                    "chance": 0.35, "effects": {"infect_regions": 1},
                    "consequence": "Заражение проникло в один регион.",
                },
            },
            {
                "name": "Закрыть границу",
                "consequence": "Казна +250; недовольство +5%.",
                "effects": {"money": 250, "unrest": 5},
            },
        ),
    },
    {
        "id": "vaccine_field_trial",
        "title": "Испытание вакцины в полевых условиях",
        "description": "Учёные предлагают проверить экспериментальную вакцину.",
        "choices": (
            {
                "name": "Начать испытания",
                "consequence": "Исследования +12; риск 30%: заражение региона.",
                "effects": {"research_points": 12, "money": -500},
                "risk": {
                    "chance": 0.30, "effects": {"infect_regions": 1},
                    "consequence": "Во время испытания заражён один регион.",
                },
            },
            {
                "name": "Отложить испытания",
                "consequence": "Стабильность +2; исследования −3.",
                "effects": {"stability": 2, "research_points": -3},
            },
        ),
    },
    {
        "id": "bridge_demolition",
        "title": "Подрыв моста на заражённом направлении",
        "description": "Командование просит перекрыть путь орде взрывом моста.",
        "choices": (
            {
                "name": "Подорвать мост",
                "consequence": (
                    "Заражённым достанется 1 регион; военная сила +7%, "
                    "стабильность −3%."
                ),
                "effects": {
                    "lose_regions": 1, "military_strength": 0.07,
                    "stability": -3,
                },
            },
            {
                "name": "Сохранить переправу",
                "consequence": "Развитие +3; риск 25%: заражение региона.",
                "effects": {"development": 3},
                "risk": {
                    "chance": 0.25, "effects": {"infect_regions": 1},
                    "consequence": "Заражённые прорвались через переправу.",
                },
            },
        ),
    },
    {
        "id": "civil_defense_fund",
        "title": "Фонд гражданской обороны",
        "description": "Города просят профинансировать укрытия и запасы.",
        "choices": (
            {
                "name": "Выделить средства",
                "consequence": "Казна −900; стабильность +6%, недовольство −5%.",
                "effects": {"money": -900, "stability": 6, "unrest": -5},
            },
            {
                "name": "Оставить бюджет без изменений",
                "consequence": "Казна +300; стабильность −4%.",
                "effects": {"money": 300, "stability": -4},
            },
        ),
    },
    {
        "id": "emergency_draft",
        "title": "Чрезвычайный набор в резерв",
        "description": "Военные предлагают расширить резервные подразделения.",
        "choices": (
            {
                "name": "Призвать резерв",
                "consequence": (
                    "Размер армии +6%, боеготовность +8%; "
                    "недовольство +6%."
                ),
                "effects": {
                    "army_growth": 0.06, "army_readiness": 8, "unrest": 6,
                },
            },
            {
                "name": "Сохранить обычный набор",
                "consequence": "Недовольство −2%; военная сила −3%.",
                "effects": {"unrest": -2, "military_strength": -0.03},
            },
        ),
    },
    {
        "id": "food_convoy",
        "title": "Продовольственный конвой",
        "description": "К изолированным городам можно отправить запасы еды.",
        "choices": (
            {
                "name": "Отправить конвой",
                "consequence": "Продовольствие +20; риск 25%: заражение региона.",
                "effects": {"food": 20, "money": -350},
                "risk": {
                    "chance": 0.25, "effects": {"infect_regions": 1},
                    "consequence": "Заражённые проникли в один регион по следу конвоя.",
                },
            },
            {
                "name": "Оставить запасы внутри страны",
                "consequence": "Продовольствие −5; политическая сила +8.",
                "effects": {"food": -5, "political_power": 8},
            },
        ),
    },
    {
        "id": "armored_supply_route",
        "title": "Бронированный маршрут снабжения",
        "description": "Снабжение фронта можно усилить бронетехникой.",
        "choices": (
            {
                "name": "Защитить маршрут",
                "consequence": "Военная сила +8%; казна −700.",
                "effects": {"military_strength": 0.08, "money": -700},
            },
            {
                "name": "Не рисковать техникой",
                "consequence": "Боеготовность −6%; казна +200.",
                "effects": {"army_readiness": -6, "money": 200},
            },
        ),
    },
    {
        "id": "scientific_archive",
        "title": "Доступ к научному архиву",
        "description": "Исследователи просят открыть закрытые вирусологические данные.",
        "choices": (
            {
                "name": "Открыть архив",
                "consequence": "Исследования +16, политическая сила +8.",
                "effects": {"research_points": 16, "political_power": 8},
            },
            {
                "name": "Сохранить секретность",
                "consequence": "Стабильность +3%; исследования −4.",
                "effects": {"stability": 3, "research_points": -4},
            },
        ),
    },
    {
        "id": "border_screening",
        "title": "Проверка прибывающих на границе",
        "description": "Медики просят ввести обязательный санитарный досмотр.",
        "choices": (
            {
                "name": "Ввести досмотр",
                "consequence": "Недовольство −6%; торговый доход временно снижен.",
                "effects": {"unrest": -6, "money": -500},
            },
            {
                "name": "Оставить границы открытыми",
                "consequence": "Казна +350; риск 30%: заражение региона.",
                "effects": {"money": 350},
                "risk": {
                    "chance": 0.30, "effects": {"infect_regions": 1},
                    "consequence": "Заражённые проникли через границу.",
                },
            },
        ),
    },
    {
        "id": "quarantine_broadcast",
        "title": "Обращение из карантинной зоны",
        "description": "Жители просят объяснить правила эвакуации и ограничения.",
        "choices": (
            {
                "name": "Провести открытый брифинг",
                "consequence": "Стабильность +5%, политическая сила +12.",
                "effects": {"stability": 5, "political_power": 12},
            },
            {
                "name": "Ограничить распространение сведений",
                "consequence": "Боеготовность +5%; недовольство +7%.",
                "effects": {"army_readiness": 5, "unrest": 7},
            },
        ),
    },
    {
        "id": "power_grid_repair",
        "title": "Ремонт энергосети у линии сдерживания",
        "description": "Аварийные бригады могут восстановить питание укреплений.",
        "choices": (
            {
                "name": "Направить ремонтные бригады",
                "consequence": "Энергия +18, развитие +2; казна −600.",
                "effects": {"energy": 18, "development": 2, "money": -600},
            },
            {
                "name": "Сохранить бригады в резерве",
                "consequence": "Казна +200; стабильность −3%.",
                "effects": {"money": 200, "stability": -3},
            },
        ),
    },
    {
        "id": "safe_zone_withdrawal",
        "title": "Отступление из небезопасного района",
        "description": "Местное командование просит разрешить организованный отход.",
        "choices": (
            {
                "name": "Отвести подразделения",
                "consequence": (
                    "Заражённым достанется 2 региона; недовольство −8%, "
                    "боеготовность +5%."
                ),
                "effects": {
                    "lose_regions": 2, "unrest": -8, "army_readiness": 5,
                },
            },
            {
                "name": "Удерживать позицию",
                "consequence": "Военная сила +5%; риск 30%: заражение региона.",
                "effects": {"military_strength": 0.05},
                "risk": {
                    "chance": 0.30, "effects": {"infect_regions": 1},
                    "consequence": "Позиция была прорвана, заражён один регион.",
                },
            },
        ),
    },
    {
        "id": "international_research_exchange",
        "title": "Международный обмен исследованиями",
        "description": "Страны предлагают объединить лабораторные данные.",
        "choices": (
            {
                "name": "Поделиться данными",
                "consequence": (
                    "Исследования +8; военная сила всех стран людей +3%."
                ),
                "effects": {
                    "research_points": 8, "global_military_strength": 0.03,
                },
            },
            {
                "name": "Сохранить разработки внутри страны",
                "consequence": "Политическая сила +15; отношения ухудшены.",
                "effects": {"political_power": 15, "unrest": 2},
            },
        ),
    },
    {
        "id": "volunteer_medics",
        "title": "Добровольцы-медики у фронта",
        "description": "Медицинские команды готовы работать рядом с очагом заражения.",
        "choices": (
            {
                "name": "Разрешить работу медиков",
                "consequence": (
                    "Стабильность +4%, недовольство −4%; риск 20%: "
                    "заражение региона."
                ),
                "effects": {"stability": 4, "unrest": -4},
                "risk": {
                    "chance": 0.20, "effects": {"infect_regions": 1},
                    "consequence": "Один регион заражён во время спасательной операции.",
                },
            },
            {
                "name": "Не допускать добровольцев к фронту",
                "consequence": "Боеготовность +4%; стабильность −2%.",
                "effects": {"army_readiness": 4, "stability": -2},
            },
        ),
    },
    {
        "id": "unified_command",
        "title": "Единое командование операциями",
        "description": "Штаб предлагает передать координацию сил международному центру.",
        "choices": (
            {
                "name": "Передать координацию штабу",
                "consequence": (
                    "Военная сила всех стран людей +5%; политическая сила +10."
                ),
                "effects": {
                    "global_military_strength": 0.05, "political_power": 10,
                },
            },
            {
                "name": "Оставить решения национальным штабам",
                "consequence": "Стабильность +3%; военная сила −2%.",
                "effects": {"stability": 3, "military_strength": -0.02},
            },
        ),
    },
)

DECISION_EVENTS_BY_ID = {
    event["id"]: event for event in DECISION_EVENTS
}
