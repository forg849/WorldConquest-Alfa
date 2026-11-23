import pygame

from game.ideology import ideology_branch_locked
from game.political_courses import (
    course_available, course_branch_locked,
)
from game.save_system import SaveSystem
from game.technology import technology_branch_locked
from game.emergency_measures import (
    EMERGENCY_MEASURE_TREE, emergency_measure_available,
)
from ui.buttons import Button
from ui.panels import Panel
from ui.theme import (
    BACKGROUND, BLUE, CARD, CARD_HOVER, EDGE, GOLD, GREEN, MUTED, PANEL_ALT, RED, TEXT,
    draw_flag, fit_text, font, rounded_panel, section_label, set_scale,
)
from ui.world_map import WorldMap
import config

PEACE_TERM_NAMES = {
    "status_quo": "перемирие без изменения границ",
    "transfer": "сохранение занятых территорий",
    "reparations": "выплата компенсации",
    "capitulation": "капитуляция",
}


class GameScreen:
    TABS = (
        ("diplomacy", "Дипломатия"),
        ("economy", "Экономика"),
        ("ideology", "Идеологии"),
        ("technology", "Технологии"),
        ("politics", "Политкурсы"),
        ("emergency", "Экстренные меры"),
        ("war", "Война"),
        ("events", "События"),
        ("relations", "Отношения"),
    )

    def __init__(self, screen, world):
        self.screen = screen
        self.world = world
        self.save_system = SaveSystem(config.SAVE_DIR)
        self.world_map = WorldMap(pygame.Rect(0, 0, 1, 1))
        self.world_map.selected_id = world.player_id
        self.selected_id = world.player_id
        self.day_timer = 0.0
        self.auto_skip_news = world.auto_skip_news
        self.active_tab = "diplomacy"
        self.selected_ideology = world.countries[world.player_id].ideology
        self.buttons = []
        self.decision_button_ids = set()
        self.last_message = ""
        self.message_ttl = 0
        self.war_scroll = 0
        self.war_content_height = 0
        self.war_content_rect = pygame.Rect(0, 0, 0, 0)
        self.war_scroll_country = world.player_id
        self.relationship_scroll = 0
        self.relationship_content_height = 0
        self.relationship_content_rect = pygame.Rect(0, 0, 0, 0)
        self.technology_scroll = 0
        self.emergency_scroll = 0
        self.ideology_scroll = 0
        self.politics_scroll = 0
        self.tree_viewport = pygame.Rect(0, 0, 0, 0)
        self.tree_content_height = 0
        self.tree_button_ids = set()
        self.resize(screen)

    def resize(self, screen):
        self.screen = screen
        width, height = screen.get_size()
        set_scale(min(1.1, max(0.9, min(width / 1280, height / 720))))
        self.font = font(17)
        self.small_font = font(13)
        self.title_font = font(20, True)
        top_height = 66
        bottom_height = 68
        side_margin = 12
        gap = 8
        if width < 1000:
            left_width = 210
            right_width = 250
        else:
            left_width = min(320, max(250, round(width * 0.17)))
            right_width = min(380, max(300, round(width * 0.205)))
        body_y = top_height + 8
        body_bottom = height - bottom_height - 10
        body_height = max(240, body_bottom - body_y)
        self.left_rect = pygame.Rect(side_margin, body_y, left_width, body_height)
        map_x = self.left_rect.right + gap
        right_x = width - side_margin - right_width
        map_width = max(280, right_x - gap - map_x)
        self.map_rect = pygame.Rect(map_x, body_y, map_width, body_height)
        self.right_rect = pygame.Rect(right_x, body_y, right_width, body_height)
        self.top_rect = pygame.Rect(0, 0, width, top_height)
        self.bottom_rect = pygame.Rect(side_margin, height - bottom_height, width - side_margin * 2, 58)
        self.world_map.resize(self.map_rect)

    def selected(self):
        return self.world.countries.get(self.selected_id)

    def handle_event(self, event):
        if event.type == pygame.VIDEORESIZE:
            self.resize(pygame.display.get_surface())
            return None
        player_defeated = self.world.countries[self.world.player_id].is_defeated
        if player_defeated or self.world.scenario_outcome:
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                return "menu"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for button in reversed(self.buttons):
                    if button.enabled and button.rect.collidepoint(event.pos):
                        button.handle_event(event)
                        return "menu"
            return None
        if self.world.pending_modal_events:
            is_decision = bool(
                self.world.pending_modal_events[0].get("decision_id")
            )
            if event.type == pygame.KEYDOWN and event.key in (
                pygame.K_RETURN, pygame.K_SPACE,
            ) and not is_decision:
                self.world.acknowledge_modal_event()
                return None
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for button in reversed(self.buttons):
                    if is_decision and id(button) not in self.decision_button_ids:
                        continue
                    if button.enabled and button.rect.collidepoint(event.pos):
                        button.handle_event(event)
                        return None
            return None
        if (
            event.type == pygame.MOUSEWHEEL
            and self.active_tab == "war"
            and self.war_content_rect.collidepoint(
                getattr(event, "pos", None) or pygame.mouse.get_pos()
            )
        ):
            max_scroll = max(
                0, self.war_content_height - self.war_content_rect.height
            )
            self.war_scroll = max(
                0, min(max_scroll, self.war_scroll - event.y * 48)
            )
            return None
        if (
            event.type == pygame.MOUSEWHEEL
            and self.active_tab == "relations"
            and self.relationship_content_rect.collidepoint(
                getattr(event, "pos", None) or pygame.mouse.get_pos()
            )
        ):
            self.relationship_scroll = max(
                0,
                min(
                    max(
                        0,
                        self.relationship_content_height
                        - self.relationship_content_rect.height,
                    ),
                    self.relationship_scroll - event.y * 48,
                ),
            )
            return None
        if (
            event.type == pygame.MOUSEWHEEL
            and self.active_tab in (
                "technology", "ideology", "politics", "emergency"
            )
            and self.tree_viewport.collidepoint(
                getattr(event, "pos", None) or pygame.mouse.get_pos()
            )
        ):
            scroll = (
                self.technology_scroll
                if self.active_tab == "technology"
                else self.ideology_scroll if self.active_tab == "ideology"
                else self.emergency_scroll if self.active_tab == "emergency"
                else self.politics_scroll
            )
            scroll = max(
                0,
                min(
                    max(0, self.tree_content_height - self.tree_viewport.height),
                    scroll - event.y * 48,
                ),
            )
            if self.active_tab == "technology":
                self.technology_scroll = scroll
            elif self.active_tab == "ideology":
                self.ideology_scroll = scroll
            elif self.active_tab == "emergency":
                self.emergency_scroll = scroll
            else:
                self.politics_scroll = scroll
            return None
        if event.type == pygame.MOUSEMOTION:
            for button in self.buttons:
                button.handle_event(event)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for button in reversed(self.buttons):
                if (
                    id(button) in self.tree_button_ids
                    and not self.tree_viewport.collidepoint(event.pos)
                ):
                    continue
                if (
                    self.active_tab == "war"
                    and self.war_content_rect.collidepoint(event.pos)
                    and not button.rect.collidepoint(event.pos)
                ):
                    continue
                if button.enabled and button.rect.collidepoint(event.pos):
                    button.handle_event(event)
                    return None

        clicked = self.world_map.handle_event(event, self.world)
        if clicked is not None:
            self.selected_id = clicked

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.world.time.toggle_pause()
            elif event.key == pygame.K_1:
                self.world.time.set_speed(1)
            elif event.key == pygame.K_2:
                self.world.time.set_speed(2)
            elif event.key == pygame.K_3:
                self.world.time.set_speed(4)
            elif event.key == pygame.K_4:
                self.world.time.set_speed(8)
            elif event.key in (pygame.K_HOME, pygame.K_0):
                self.world_map.reset_camera()
            elif event.key in (pygame.K_EQUALS, pygame.K_KP_PLUS):
                self.world_map.zoom_at(self.map_rect.center, 1.25)
            elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                self.world_map.zoom_at(self.map_rect.center, 1 / 1.25)
            elif event.key == pygame.K_ESCAPE:
                if self.active_tab in (
                    "technology", "ideology", "politics", "emergency"
                ):
                    self.active_tab = "diplomacy"
                    return None
                return "menu"
        return None

    def update(self, dt):
        player_defeated = self.world.countries[self.world.player_id].is_defeated
        if player_defeated or self.world.scenario_outcome:
            self.world.time.paused = True
            self.day_timer = 0.0
        elif not self.world.time.paused:
            self.day_timer += dt * self.world.time.speed
            while self.day_timer >= config.DAY_SECONDS:
                self.world.advance_day()
                self.day_timer -= config.DAY_SECONDS
                if (
                    self.world.countries[self.world.player_id].is_defeated
                    or self.world.scenario_outcome
                ):
                    self.world.time.paused = True
                    self.day_timer = 0.0
                    break
        self.world.update(dt)
        self.message_ttl = max(0, self.message_ttl - dt)

    def draw(self, surface):
        self.buttons = []
        self.decision_button_ids = set()
        self.tree_button_ids = set()
        surface.fill(BACKGROUND)
        if self.world.countries[self.world.player_id].is_defeated:
            self._draw_defeat_screen(surface)
            return
        if self.world.scenario_outcome:
            self._draw_scenario_outcome(surface)
            return
        self._draw_top(surface)
        if self.active_tab == "technology":
            self._draw_research_screen(surface)
        elif self.active_tab == "ideology":
            self._draw_ideology_screen(surface)
        elif self.active_tab == "politics":
            self._draw_politics_screen(surface)
        elif self.active_tab == "emergency":
            self._draw_emergency_measures_screen(surface)
        else:
            self.world_map.draw(surface, self.world)
            self._draw_left(surface)
            self._draw_right(surface)
        self._draw_bottom(surface)
        if self.active_tab not in (
            "technology", "ideology", "politics", "emergency"
        ):
            self._draw_notifications(surface)
        if self.world.pending_modal_events:
            self._draw_event_modal(surface)

    def _draw_defeat_screen(self, surface):
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((9, 15, 21, 235))
        surface.blit(overlay, (0, 0))
        width = min(620, surface.get_width() - 40)
        height = 300
        panel = pygame.Rect(0, 0, width, height)
        panel.center = surface.get_rect().center
        rounded_panel(surface, panel, (24, 34, 42), EDGE, 12)

        title = font(12, True).render("КАМПАНИЯ ЗАВЕРШЕНА", True, GOLD)
        surface.blit(title, title.get_rect(center=(panel.centerx, panel.y + 43)))
        defeated = font(29, True).render("ГОСУДАРСТВО ПОВЕРЖЕНО", True, RED)
        surface.blit(defeated, defeated.get_rect(center=(panel.centerx, panel.y + 91)))
        country = self.world.countries[self.world.player_id]
        country_name = fit_text(
            surface, country.name, panel.width - 54, 18, TEXT, True
        )
        surface.blit(country_name, country_name.get_rect(center=(panel.centerx, panel.y + 139)))
        summary = font(12).render(
            "Последняя территория потеряна. Ваша кампания окончена.",
            True, MUTED,
        )
        surface.blit(summary, summary.get_rect(center=(panel.centerx, panel.y + 177)))
        self.add_button(
            (panel.centerx - 140, panel.bottom - 67, 280, 42),
            "В ГЛАВНОЕ МЕНЮ",
            lambda: None,
            color=(65, 48, 47),
            size=12,
        )

    def _draw_scenario_outcome(self, surface):
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((9, 15, 21, 235))
        surface.blit(overlay, (0, 0))
        width = min(660, surface.get_width() - 40)
        panel = pygame.Rect(0, 0, width, 310)
        panel.center = surface.get_rect().center
        rounded_panel(surface, panel, (24, 34, 42), EDGE, 12)
        title, color, summary = {
            "humans_win": (
                "ЧЕЛОВЕЧЕСТВО ПОБЕДИЛО", GREEN,
                "Все заражённые регионы освобождены.",
            ),
            "zombies_win": (
                "МИР ЗАХВАЧЕН", RED,
                "Заражённые распространились на 75% территорий.",
            ),
        }.get(
            self.world.scenario_outcome,
            ("КАМПАНИЯ ЗАВЕРШЕНА", GOLD,
             "Государство игрока потеряло всю территорию."),
        )
        heading = font(12, True).render(
            "2031 · ВСПЫШКА ЗАРАЖЕНИЯ", True, GOLD
        )
        surface.blit(heading, heading.get_rect(center=(panel.centerx, panel.y + 48)))
        result = fit_text(surface, title, panel.width - 44, 27, color, True)
        surface.blit(result, result.get_rect(center=(panel.centerx, panel.y + 108)))
        detail = fit_text(surface, summary, panel.width - 50, 13, MUTED)
        surface.blit(detail, detail.get_rect(center=(panel.centerx, panel.y + 158)))
        self.add_button(
            (panel.centerx - 140, panel.bottom - 69, 280, 42),
            "В ГЛАВНОЕ МЕНЮ",
            lambda: None,
            color=(65, 48, 47),
            size=12,
        )

    def add_button(self, rect, text, callback, enabled=True, color=None, size=14):
        button = Button(rect, text, callback, color=color)
        button.enabled = enabled
        button.draw(self.screen, font(size, True))
        self.buttons.append(button)
        return button

    def perform(self, action, log_success=False):
        success, message = action()
        self.last_message = message
        self.message_ttl = 5
        if not success or log_success:
            self.world.add_event(message)
        return success, message

    def _draw_top(self, surface):
        pygame.draw.rect(surface, (18, 27, 35), self.top_rect)
        pygame.draw.line(surface, EDGE, (0, self.top_rect.bottom - 1),
                         (self.top_rect.right, self.top_rect.bottom - 1), 1)
        brand = font(18, True).render("WORLD", True, TEXT)
        brand2 = font(18, True).render("CONQUEST", True, GOLD)
        surface.blit(brand, (14, 9))
        surface.blit(brand2, (14, 32))
        scenario = fit_text(surface, self.world.scenario_name.upper(), 172, 10, MUTED, True)
        surface.blit(scenario, (134, 24))
        pygame.draw.line(surface, EDGE, (298, 13), (298, 53), 1)

        player = self.world.countries[self.world.player_id]
        report = player.economy_report(
            self.world.province_count(player.id),
            len(self.world.wars_for(player.id)),
            zombie_scenario=self.world.scenario_id == "zombie",
        )
        cards = [
            ("ДАТА", self.world.date_text(), f"ДЕНЬ {self.world.day + 1}", 154),
            ("КАЗНА", f"{player.money:,.0f}", "ДЕНЬГИ", 142),
            ("БАЛАНС", f"{report['net']:+.1f}", "ЗА ИГРОВОЙ ДЕНЬ", 154),
            ("ПРОДОВОЛЬСТВИЕ", f"{player.food:.0f}%", "ЗАПАС", 140),
            ("ЭНЕРГИЯ", f"{player.energy:.0f}%", f"ПОЛИТСИЛА {player.political_power:.0f}", 150),
        ]
        x = 314
        for title, value, subtitle, width in cards:
            self._draw_top_stat(surface, pygame.Rect(x, 9, width, 48), title, value, subtitle)
            x += width + 7

        pause_rect = pygame.Rect(self.top_rect.right - 112, 12, 98, 42)
        self.add_button(
            pause_rect,
            "▶  ИДЁТ" if self.world.time.paused else "Ⅱ  ПАУЗА",
            self.world.time.toggle_pause,
            color=(56, 71, 66) if self.world.time.paused else (58, 53, 47),
            size=12,
        )

    def _draw_top_stat(self, surface, rect, title, value, subtitle):
        rounded_panel(surface, rect, PANEL_ALT, None, 6)
        title_surface = font(9, True).render(title, True, MUTED)
        value_surface = fit_text(surface, value, rect.width - 16, 14, TEXT, True)
        subtitle_surface = font(8).render(subtitle, True, MUTED)
        surface.blit(title_surface, (rect.x + 8, rect.y + 3))
        surface.blit(value_surface, (rect.x + 8, rect.y + 17))
        surface.blit(subtitle_surface, (rect.right - subtitle_surface.get_width() - 8, rect.y + 37))

    def _draw_left(self, surface):
        panel = Panel(self.left_rect, "Государство")
        panel.draw(surface, self.font, self.title_font)
        country = self.selected()
        if not country:
            return
        x = self.left_rect.x + 13
        width = self.left_rect.width - 26
        y = self.left_rect.y + 49
        flag_rect = pygame.Rect(x, y, width, 76)
        draw_flag(surface, flag_rect, country.id, country.color)
        name_y = flag_rect.bottom + 12
        name = fit_text(surface, country.name, width, 21, TEXT, True)
        surface.blit(name, (x, name_y))
        y = name_y + 34

        count = self.world.territory_count(country.id)
        tiles = [
            ("НАСЕЛЕНИЕ", self._population(country.population)),
            ("РЕГИОНЫ", f"{count:,}"),
            ("ЭКОНОМИКА", f"{country.economy_level}/10"),
            ("СТАБИЛЬНОСТЬ", f"{country.stability:.0f}%"),
        ]
        tile_width = (width - 7) // 2
        tile_height = 49
        for index, (label, value) in enumerate(tiles):
            column, row = index % 2, index // 2
            rect = pygame.Rect(x + column * (tile_width + 7), y + row * (tile_height + 7),
                               tile_width, tile_height)
            rounded_panel(surface, rect, CARD, None, 6)
            surface.blit(font(9, True).render(label, True, MUTED), (rect.x + 8, rect.y + 7))
            value_surface = fit_text(surface, value, rect.width - 14, 15, TEXT, True)
            surface.blit(value_surface, (rect.x + 8, rect.y + 24))
        y += tile_height * 2 + 19

        report = country.economy_report(
            self.world.province_count(country.id),
            len(self.world.wars_for(country.id)),
            zombie_scenario=self.world.scenario_id == "zombie",
        )
        self._draw_meter(surface, x, y, width, "Чистый доход", report["net"], -20, 100,
                         GREEN if report["net"] >= 0 else RED,
                         f"{report['net']:+.1f} / день")
        y += 37
        self._draw_meter(surface, x, y, width, "Армия", country.military, 0, 100, BLUE,
                         f"{country.military:.0f} / 100")
        y += 39
        unrest_color = RED if country.unrest >= 60 else GOLD
        self._draw_meter(
            surface, x, y, width, "Недовольство", country.unrest, 0, 100,
            unrest_color, f"{country.unrest:.0f}%",
        )
        y += 39
        surface.blit(font(11).render(
            f"Идеология: {self.world.ideology_name_for(country.id)}",
            True, MUTED,
        ), (x, y))
        y += 20
        if self.world_map.selected_province_id:
            province = self.world.provinces_by_id.get(self.world_map.selected_province_id)
            if province:
                region_text = fit_text(surface, f"Регион: {province.name}", width, 12, GOLD)
                surface.blit(region_text, (x, y))
                y += 24

        y = max(y + 5, self.left_rect.y + self.left_rect.height - 192)
        section_label(surface, "Развитие государства", (x, y))
        y += 24
        player_selected = country.id == self.world.player_id
        investments = (
            ("industry", f"Завод  −${country.investment_cost('industry')}"),
            ("economy", f"Экономика  −${country.investment_cost('economy')}"),
            ("infrastructure", f"Инфраструктура  −${country.investment_cost('infrastructure')}"),
            ("farms", f"Фермы  −${country.investment_cost('farms')}"),
            ("power", f"Энергия  −${country.investment_cost('power')}"),
            ("military", f"Армия  −${country.investment_cost('military')}"),
        )
        button_gap = 6
        button_width = (width - button_gap) // 2
        for index, (kind, label) in enumerate(investments):
            column, row = index % 2, index // 2
            rect = pygame.Rect(x + column * (button_width + button_gap),
                               y + row * 34, button_width, 29)
            self.add_button(
                rect, label,
                lambda value=kind: self.perform(
                    lambda: self.world.countries[self.world.player_id].invest(value),
                    log_success=True,
                ),
                enabled=player_selected,
                size=11,
            )

    @staticmethod
    def _population(value):
        if value >= 1_000_000_000:
            return f"{value / 1_000_000_000:.1f} млрд"
        return f"{value / 1_000_000:.1f} млн"

    def _draw_meter(self, surface, x, y, width, label, value, minimum, maximum, color, value_text):
        surface.blit(font(10, True).render(label.upper(), True, MUTED), (x, y))
        label_value = font(11, True).render(value_text, True, TEXT)
        surface.blit(label_value, (x + width - label_value.get_width(), y))
        bar = pygame.Rect(x, y + 17, width, 5)
        pygame.draw.rect(surface, (42, 55, 62), bar, border_radius=3)
        ratio = max(0, min(1, (value - minimum) / max(1, maximum - minimum)))
        if ratio:
            pygame.draw.rect(surface, color, (bar.x, bar.y, max(4, round(bar.width * ratio)), bar.height),
                             border_radius=3)

    def _draw_right(self, surface):
        Panel(self.right_rect, "Оперативный штаб").draw(surface, self.font, self.title_font)
        country = self.selected()
        if not country:
            return
        x = self.right_rect.x + 12
        y = self.right_rect.y + 47
        gap = 5
        tab_width = (self.right_rect.width - 24 - gap * 2) // 3
        tabs = self.TABS if self.world.scenario_id == "zombie" else tuple(
            item for item in self.TABS if item[0] != "emergency"
        )
        for index, (tab_id, label) in enumerate(tabs):
            column, row = index % 3, index // 3
            rect = pygame.Rect(x + column * (tab_width + gap), y + row * 31, tab_width, 27)
            self.add_button(
                rect, label,
                lambda value=tab_id: setattr(self, "active_tab", value),
                color=(70, 61, 43) if self.active_tab == tab_id else CARD,
                size=11,
            )

        content_y = y + ((len(tabs) + 2) // 3) * 31 + 8
        content = pygame.Rect(
            self.right_rect.x + 10, content_y,
            self.right_rect.width - 20, self.right_rect.bottom - content_y - 10,
        )
        self.war_content_rect = content
        if self.active_tab == "war" and self.war_scroll_country != country.id:
            self.war_scroll = 0
            self.war_content_height = 0
            self.war_scroll_country = country.id
        if self.active_tab == "relations":
            self.relationship_content_rect = content
            self.relationship_scroll = min(
                self.relationship_scroll,
                max(
                    0,
                    self.relationship_content_height - content.height,
                ),
            )
        previous_clip = surface.get_clip()
        surface.set_clip(content)
        if self.message_ttl > 0:
            message = fit_text(surface, self.last_message, content.width, 12, GOLD)
            surface.blit(message, (content.x + 2, content.y + 2))
            content_y += 23

        if self.active_tab == "diplomacy":
            self._draw_diplomacy(surface, country, content_y)
        elif self.active_tab == "economy":
            self._draw_economy(surface, country, content_y)
        elif self.active_tab == "ideology":
            self._draw_ideology_screen(surface)
        elif self.active_tab == "war":
            self._draw_war(surface, country, content_y)
        elif self.active_tab == "relations":
            self._draw_relationships(surface, content_y, content)
        else:
            self._draw_events(surface, content_y)
        surface.set_clip(previous_clip)

    def _draw_diplomacy(self, surface, country, y):
        player = self.world.countries[self.world.player_id]
        x, width = self.right_rect.x + 14, self.right_rect.width - 28
        if country.id == player.id:
            section_label(surface, "Международное положение", (x, y + 4))
            surface.blit(font(14, True).render("Выбрано ваше государство", True, TEXT), (x, y + 27))
            alliance = self.world.alliance_partner(player.id)
            surface.blit(font(12).render(
                f"Союз: {alliance.name if alliance else 'нет'}", True, MUTED
            ), (x, y + 52))
            surface.blit(font(12).render(
                f"Активные конфликты: {len(self.world.wars_for(player.id))}", True, MUTED
            ), (x, y + 73))
            if alliance:
                self.add_button(
                    (x, y + 103, width, 34),
                    "Расторгнуть союз",
                    lambda: self.perform(
                        lambda: self.world.diplomacy.break_alliance(player.id, alliance.id)
                    ),
                    color=(69, 47, 45),
                )
            return

        relation = self.world.diplomacy.get_relation(player.id, country.id)
        at_war = country.id in player.wars
        war = self.world.war_between(player.id, country.id)
        section_label(surface, "Отношения", (x, y + 3))
        relation_color = RED if relation < -25 else GREEN if relation > 25 else GOLD
        surface.blit(font(27, True).render(f"{relation:+d}", True, relation_color), (x, y + 20))
        surface.blit(font(12).render(
            f"Доверие  {max(0, min(100, 50 + relation // 2))}%", True, MUTED
        ), (x + 80, y + 31))
        surface.blit(font(11).render(
            f"Военная сила   {player.military_strength(self.world):.0f} : "
            f"{country.military_strength(self.world):.0f}",
            True, MUTED,
        ), (x, y + 60))

        if self.world.scenario_id == "zombie" and country.id == "zombies":
            surface.blit(font(11, True).render(
                "Заражённые не ведут переговоров.",
                True, RED,
            ), (x, y + 88))
            return

        button_y = y + 88
        half = (width - 6) // 2
        self.add_button(
            (x, button_y, half, 34), "Улучшить  −80",
            lambda: self.perform(lambda: self.world.diplomacy.improve(player.id, country.id)),
            color=CARD_HOVER,
        )
        allied = player.alliance == country.id
        self.add_button(
            (x + half + 6, button_y, half, 34),
            "Расторгнуть союз" if allied else "Предложить союз",
            lambda: self.perform(
                lambda: self.world.diplomacy.break_alliance(player.id, country.id)
                if allied
                else self.world.diplomacy.form_alliance(player.id, country.id)
            ),
            enabled=allied or not at_war,
            color=(69, 47, 45) if allied else CARD_HOVER,
            size=11 if allied else 12,
        )
        button_y += 45
        if at_war and war and war.peace_offer:
            offer = war.peace_offer
            if offer["proposer"] == player.id:
                peace_text = "Отозвать предложение мира"
                peace_action = lambda: self.world.withdraw_peace_offer(war.id, player.id)
            elif offer["recipient"] == player.id:
                peace_text = "Ответить на предложение"
                peace_action = lambda: setattr(self, "active_tab", "war")
            else:
                peace_text = "Мирное предложение активно"
                peace_action = lambda: (False, "Предложение адресовано другому государству")
        elif at_war:
            if war and war.objective.get("type") == "zombie_outbreak":
                peace_text = "Перемирие с заражёнными недоступно"
                peace_action = lambda: (
                    False, "Заражённым нельзя предложить мир в этом сценарии"
                )
            else:
                peace_text = "Предложить перемирие"
                peace_action = lambda: self.world.offer_peace(
                    player.id, country.id, "status_quo"
                )
        else:
            peace_text = "Объявить войну"
            peace_action = lambda: self.world.declare_war(player.id, country.id)
        self.add_button(
            (x, button_y, width, 38),
            peace_text,
            lambda: self.perform(peace_action),
            enabled=(
                not (war and war.objective.get("type") == "zombie_outbreak")
                and not (war and war.peace_offer and offer["recipient"] != player.id)
            ),
            color=(69, 47, 45) if not at_war else (48, 69, 58),
        )
        if at_war:
            button_y += 47
            self.add_button(
                (x, button_y, width, 38), "Провести операцию  −120",
                lambda: self.perform(lambda: self.world.resolve_conflict(player.id, country.id)),
                color=(69, 47, 45),
            )

    def _draw_economy(self, surface, country, y):
        x, width = self.right_rect.x + 14, self.right_rect.width - 28
        report = country.economy_report(
            self.world.province_count(country.id),
            len(self.world.wars_for(country.id)),
            zombie_scenario=self.world.scenario_id == "zombie",
        )
        section_label(surface, "Экономика государства", (x, y + 3))
        y += 29
        rows = (
            ("Производство", f"{report['output']:.1f}"),
            (f"Налоги · {country.tax_rate}%", f"+{report['taxes']:.1f} / день"),
            ("Содержание", f"−{report['upkeep']:.1f} / день"),
            ("Чистый баланс", f"{report['net']:+.1f} / день"),
            ("Продовольствие", f"{report['food_balance']:+.2f} / день"),
            ("Энергия", f"{report['energy_balance']:+.2f} / день"),
            ("Исследования", f"{report['research']:.2f} оч. / день"),
            ("Недовольство", f"{country.unrest:.0f}%"),
        )
        for label, value in rows:
            surface.blit(font(12).render(label, True, MUTED), (x, y))
            value_surface = fit_text(surface, value, width * 0.48, 12, TEXT, True)
            surface.blit(value_surface, (x + width - value_surface.get_width(), y))
            y += 28
        y += 6
        player_selected = country.id == self.world.player_id
        half = (width - 6) // 2
        self.add_button((x, y, half, 34), "Налог  −1%",
                        lambda: self.change_tax(-1), enabled=player_selected)
        self.add_button((x + half + 6, y, half, 34), "Налог  +1%",
                        lambda: self.change_tax(1), enabled=player_selected)
        y += 47
        relief_cost = self.world.unrest_relief_cost(country.id)
        self.add_button(
            (x, y, width, 34),
            f"Снизить недовольство на 2%  ·  ${relief_cost}",
            lambda: self.perform(
                lambda: self.world.reduce_unrest(self.world.player_id)
            ),
            enabled=(
                player_selected and country.unrest >= 2
                and country.money >= relief_cost
            ),
            color=(55, 66, 53),
            size=10,
        )
        y += 40
        surface.blit(font(10).render(
            "Высокие налоги и усталость от войны снижают стабильность.", True, MUTED
        ), (x, y))

    def change_tax(self, adjustment):
        country = self.world.countries[self.world.player_id]
        previous = country.tax_rate
        new_rate = country.set_tax_rate(adjustment)
        if previous == new_rate:
            self.last_message = "Ставка уже на пределе"
            self.message_ttl = 4
            return
        message = f"Налоговая ставка: {new_rate}%"
        self.last_message = message
        self.message_ttl = 5
        self.world.add_event(message)

    def _draw_ideology_screen(self, surface):
        country = self.world.countries[self.world.player_id]
        ideologies = self.world.ideology_options_for(country.id)
        if self.selected_ideology not in ideologies:
            self.selected_ideology = country.ideology
        ideology_id = self.selected_ideology
        ideology = ideologies[ideology_id]
        nodes = self.world.ideology_tree_for(country.id, ideology_id)
        body = pygame.Rect(
            12, 74, surface.get_width() - 24, surface.get_height() - 150
        )
        rounded_panel(surface, body, (20, 30, 38), EDGE, 8)
        section_label(surface, "Идеология и государственное развитие",
                      (body.x + 20, body.y + 15), 14)
        report = country.economy_report(
            self.world.province_count(country.id),
            len(self.world.wars_for(country.id)),
            zombie_scenario=self.world.scenario_id == "zombie",
        )
        stats = font(11).render(
            f"Действующая: {ideologies[country.ideology]['name']}   ·   "
            f"Политическая сила: {country.political_power:.1f} "
            f"(+{report['political_power']:.2f} в день)   ·   "
            f"Казна: ${country.money:,.0f}",
            True, MUTED,
        )
        surface.blit(stats, (body.x + 20, body.y + 41))
        self.add_button(
            (body.right - 126, body.y + 13, 106, 34),
            "НАЗАД",
            lambda: setattr(self, "active_tab", "diplomacy"),
            color=CARD,
            size=11,
        )

        selector_y = body.y + 69
        selector_gap = 9
        selector_columns = min(4, len(ideologies))
        selector_width = (
            body.width - 40 - selector_gap * (selector_columns - 1)
        ) // selector_columns
        for index, (option_id, option) in enumerate(ideologies.items()):
            rect = pygame.Rect(
                body.x + 20 + index * (selector_width + selector_gap),
                selector_y, selector_width, 77,
            )
            selected = ideology_id == option_id
            rounded_panel(
                surface, rect, (45, 54, 46) if selected else CARD,
                GOLD if selected else EDGE, 6,
            )
            surface.blit(
                fit_text(surface, option["name"], rect.width - 16, 13, TEXT, True),
                (rect.x + 9, rect.y + 6),
            )
            surface.blit(
                fit_text(surface, option["description"], rect.width - 16, 9, MUTED),
                (rect.x + 9, rect.y + 25),
            )
            self.add_button(
                (rect.x + 8, rect.bottom - 24, rect.width - 16, 19),
                "ВЫБРАНО" if selected else "ОТКРЫТЬ ВЕТКУ",
                lambda value=option_id: self._select_ideology(value),
                color=(64, 71, 57) if selected else None,
                size=9,
            )

        action_y = selector_y + 86
        is_current = country.ideology == ideology_id
        self.add_button(
            (body.x + 20, action_y, body.width - 40, 35),
            (
                "ДЕЙСТВУЮЩАЯ ИДЕОЛОГИЯ"
                if is_current
                else f"ПРИНЯТЬ {ideology['name'].upper()}  ·  $500  ·  50 ПОЛИТСИЛЫ"
            ),
            lambda: self.perform(
                lambda: self.world.change_ideology(
                    self.world.player_id, ideology_id
                )
            ),
            enabled=not is_current,
            color=(55, 67, 55) if is_current else (65, 53, 42),
            size=10,
        )

        tree_top = action_y + 49
        section_label(
            surface,
            f"ВЕТКА: {ideology['name'].upper()}  ·  "
            f"{len(nodes)} УЛУЧШЕНИЙ  ·  "
            f"{sum(node['id'] in country.ideology_upgrades for node in nodes)} ИЗУЧЕНО",
            (body.x + 20, tree_top), 11,
        )
        self.tree_viewport = pygame.Rect(
            body.x + 12, tree_top + 24, body.width - 24,
            body.bottom - tree_top - 40,
        )
        columns = max(node["position"][0] for node in nodes) + 1
        rows = max(node["position"][1] for node in nodes) + 1
        gap_x, gap_y = 12, 12
        node_height = 124
        node_width = min(
            390,
            (body.width - 60 - gap_x * (columns - 1)) // columns,
        )
        tree_width = columns * node_width + (columns - 1) * gap_x
        tree_x = body.centerx - tree_width // 2
        self.tree_content_height = rows * node_height + (rows - 1) * gap_y
        max_scroll = max(
            0, self.tree_content_height - self.tree_viewport.height
        )
        self.ideology_scroll = max(0, min(self.ideology_scroll, max_scroll))
        tree_y = self.tree_viewport.y - self.ideology_scroll
        rectangles = {}
        for node in nodes:
            column, row = node["position"]
            rectangles[node["id"]] = pygame.Rect(
                tree_x + column * (node_width + gap_x),
                tree_y + row * (node_height + gap_y),
                node_width, node_height,
            )
        previous_clip = surface.get_clip()
        surface.set_clip(self.tree_viewport)
        for node in nodes:
            target_rect = rectangles[node["id"]]
            for requirement in node["requires"]:
                source_rect = rectangles[requirement]
                color = (
                    (112, 151, 125)
                    if requirement in country.ideology_upgrades
                    else (66, 83, 91)
                )
                pygame.draw.line(
                    surface, color, source_rect.midbottom, target_rect.midtop, 2
                )

        names = {node["id"]: node["name"] for node in nodes}
        for node in nodes:
            rect = rectangles[node["id"]]
            if not rect.colliderect(self.tree_viewport):
                continue
            researched = node["id"] in country.ideology_upgrades
            unlocked = all(
                required in country.ideology_upgrades
                for required in node["requires"]
            )
            branch_locked = ideology_branch_locked(
                country.ideology_upgrades, ideology_id, node["id"]
            )
            active_upgrade = country.active_upgrade or {}
            is_active = (
                active_upgrade.get("kind") == "ideology"
                and active_upgrade.get("id") == node["id"]
            )
            current_branch = country.ideology == ideology_id
            affordable = country.political_power >= node["cost"]
            available = (
                current_branch and unlocked and affordable
                and not researched and not branch_locked
                and not active_upgrade
            )
            fill = (
                (43, 64, 54) if researched
                else (56, 61, 46) if available
                else (52, 35, 35) if branch_locked
                else CARD if current_branch and unlocked
                else (25, 34, 41)
            )
            border = GREEN if researched else GOLD if available else EDGE
            rounded_panel(surface, rect, fill, border, 7)
            surface.blit(
                fit_text(surface, node["name"], rect.width - 18, 12, TEXT, True),
                (rect.x + 9, rect.y + 7),
            )
            surface.blit(
                fit_text(surface, node["effect"], rect.width - 18, 10, MUTED),
                (rect.x + 9, rect.y + 29),
            )
            requirement_text = (
                "Начальная ступень" if not node["requires"]
                else "Требует: " + ", ".join(names[item] for item in node["requires"])
            )
            surface.blit(
                fit_text(surface, requirement_text, rect.width - 18, 9, MUTED),
                (rect.x + 9, rect.y + 50),
            )
            label = (
                "ИЗУЧЕНО" if researched
                else f"ИЗУЧАЕТСЯ · {active_upgrade['remaining_days']} дн."
                if is_active
                else "ВЫБРАНА ДРУГАЯ ВЕТКА" if branch_locked
                else f"ИЗУЧИТЬ  ·  {node['cost']} ПС" if current_branch and unlocked
                else "СНАЧАЛА ПРЕДЫДУЩИЙ УРОВЕНЬ" if current_branch
                else "НУЖНО ПРИНЯТЬ ИДЕОЛОГИЮ"
            )
            button_rect = pygame.Rect(
                rect.x + 8, rect.bottom - 29, rect.width - 16, 22
            )
            if not self.tree_viewport.contains(button_rect):
                continue
            button = self.add_button(
                button_rect,
                label,
                lambda value=node["id"]: self.perform(
                    lambda: self.world.develop_ideology(
                        self.world.player_id, value
                    )
                ),
                enabled=available,
                color=(54, 69, 58) if researched else None,
                size=9,
            )
            self.tree_button_ids.add(id(button))
        surface.set_clip(previous_clip)
        self._draw_tree_scrollbar(
            surface, self.tree_viewport, self.tree_content_height,
            self.ideology_scroll,
        )

    def _select_ideology(self, ideology_id):
        self.selected_ideology = ideology_id
        self.ideology_scroll = 0

    @staticmethod
    def _draw_tree_scrollbar(surface, viewport, content_height, scroll):
        max_scroll = max(0, content_height - viewport.height)
        if not max_scroll:
            return
        track = pygame.Rect(viewport.right - 5, viewport.y, 3, viewport.height)
        thumb_height = max(28, round(track.height * viewport.height / content_height))
        thumb_y = track.y + round(
            (track.height - thumb_height) * scroll / max_scroll
        )
        pygame.draw.rect(surface, (49, 63, 70), track, border_radius=2)
        pygame.draw.rect(
            surface, (174, 137, 80),
            (track.x, thumb_y, track.width, thumb_height), border_radius=2,
        )

    def _draw_politics_screen(self, surface):
        country = self.world.countries[self.world.player_id]
        courses = self.world.political_courses_for(country.id)
        body = pygame.Rect(12, 74, surface.get_width() - 24, surface.get_height() - 150)
        rounded_panel(surface, body, (20, 30, 38), EDGE, 8)
        section_label(surface, "Политические курсы и национальные приоритеты",
                      (body.x + 20, body.y + 16), 14)
        active = country.active_political_course
        active_name = (
            next(
                item["name"] for item in courses
                if item["id"] == active["id"]
            )
            if active else "нет"
        )
        status = font(11).render(
            f"Лидер: {country.leader}  ·  Курс: {active_name}"
            + (f" ({active['remaining_days']} дн.)" if active else "")
            + f"  ·  Политическая сила: {country.political_power:.1f}"
            + f"  ·  Казна: ${country.money:,.0f}",
            True, MUTED,
        )
        surface.blit(status, (body.x + 20, body.y + 42))
        self.add_button(
            (body.right - 126, body.y + 13, 106, 34),
            "НАЗАД",
            lambda: setattr(self, "active_tab", "diplomacy"),
            color=CARD,
            size=11,
        )

        columns = max(item["position"][0] for item in courses) + 1
        rows = max(item["position"][1] for item in courses) + 1
        node_width = min(330, (body.width - 56 - (columns - 1) * 12) // columns)
        node_height, gap_x, gap_y = 126, 12, 14
        tree_width = columns * node_width + (columns - 1) * gap_x
        tree_x = body.centerx - tree_width // 2
        self.tree_viewport = pygame.Rect(
            body.x + 12, body.y + 76, body.width - 24, body.height - 94
        )
        self.tree_content_height = rows * node_height + (rows - 1) * gap_y
        max_scroll = max(0, self.tree_content_height - self.tree_viewport.height)
        self.politics_scroll = max(0, min(self.politics_scroll, max_scroll))
        tree_y = self.tree_viewport.y - self.politics_scroll
        rectangles = {
            item["id"]: pygame.Rect(
                tree_x + item["position"][0] * (node_width + gap_x),
                tree_y + item["position"][1] * (node_height + gap_y),
                node_width, node_height,
            )
            for item in courses
        }
        names = {item["id"]: item["name"] for item in courses}
        previous_clip = surface.get_clip()
        surface.set_clip(self.tree_viewport)
        for item in courses:
            target = rectangles[item["id"]]
            for requirement in item["requires"]:
                source = rectangles[requirement]
                color = (
                    (112, 151, 125)
                    if requirement in country.political_policies
                    else (66, 83, 91)
                )
                pygame.draw.line(surface, color, source.midbottom, target.midtop, 2)

        for item in courses:
            rect = rectangles[item["id"]]
            if not rect.colliderect(self.tree_viewport):
                continue
            completed = item["id"] in country.political_policies
            is_active = bool(active and active["id"] == item["id"])
            locked_by_choice = course_branch_locked(
                country.political_policies, item["id"]
            )
            available = (
                course_available(self.world, country, item["id"])
                and country.money >= item["cost"]
                and country.political_power >= item["political_power"]
            )
            fill = (
                (43, 64, 54) if completed
                else (64, 57, 38) if is_active
                else (56, 61, 46) if available
                else (52, 35, 35) if locked_by_choice
                else CARD if all(
                    req in country.political_policies for req in item["requires"]
                )
                else (25, 34, 41)
            )
            border = GREEN if completed else GOLD if (available or is_active) else EDGE
            rounded_panel(surface, rect, fill, border, 7)
            surface.blit(
                fit_text(surface, item["name"], rect.width - 18, 12, TEXT, True),
                (rect.x + 9, rect.y + 7),
            )
            surface.blit(
                fit_text(surface, item["description"], rect.width - 18, 9, MUTED),
                (rect.x + 9, rect.y + 29),
            )
            requirement_text = (
                "Начальный курс" if not item["requires"]
                else "Нужно завершить: "
                + ", ".join(names[req] for req in item["requires"])
            )
            if item.get("min_year"):
                requirement_text += f" · не ранее {item['min_year']} г."
            surface.blit(
                fit_text(surface, requirement_text, rect.width - 18, 8, MUTED),
                (rect.x + 9, rect.y + 54),
            )
            cost_text = (
                f"${item['cost']}  ·  {item['political_power']} ПС"
                f"  ·  {item['days']} дн."
            )
            surface.blit(
                fit_text(surface, cost_text, rect.width - 18, 9, TEXT),
                (rect.x + 9, rect.y + 72),
            )
            button_rect = pygame.Rect(
                rect.x + 8, rect.bottom - 29, rect.width - 16, 22
            )
            if not self.tree_viewport.contains(button_rect):
                continue
            label = (
                "ЗАВЕРШЕНО" if completed
                else f"В ПРОЦЕССЕ · {active['remaining_days']} ДН."
                if is_active
                else "ВЫБРАНА ДРУГАЯ ВЕТКА" if locked_by_choice
                else "НАЧАТЬ КУРС" if available
                else "НЕДОСТУПНО"
            )
            button = self.add_button(
                button_rect,
                label,
                lambda value=item["id"]: self.perform(
                    lambda: self.world.start_political_course(
                        self.world.player_id, value
                    )
                ),
                enabled=available,
                color=(54, 69, 58) if completed else None,
                size=8,
            )
            self.tree_button_ids.add(id(button))
        surface.set_clip(previous_clip)
        self._draw_tree_scrollbar(
            surface, self.tree_viewport, self.tree_content_height,
            self.politics_scroll,
        )

    def _draw_research_screen(self, surface):
        country = self.world.countries[self.world.player_id]
        tech_tree = self.world.technology_tree_for(country.id)
        body = pygame.Rect(12, 74, surface.get_width() - 24, surface.get_height() - 150)
        rounded_panel(surface, body, (20, 30, 38), EDGE, 8)
        section_label(surface, "Дерево исследований", (body.x + 20, body.y + 16), 14)
        research = country.economy_report(
            zombie_scenario=self.world.scenario_id == "zombie"
        )["research"]
        stats = font(11).render(
            f"{country.research_points:.1f} очков  ·  +{research:.2f} в день  ·  "
            f"{len(country.techs)}/{len(tech_tree)} технологий",
            True, MUTED,
        )
        surface.blit(stats, (body.x + 20, body.y + 42))
        self.add_button(
            (body.right - 126, body.y + 16, 106, 34),
            "НАЗАД",
            lambda: setattr(self, "active_tab", "diplomacy"),
            color=CARD,
            size=11,
        )

        columns = max(node["position"][0] for node in tech_tree) + 1
        rows = max(node["position"][1] for node in tech_tree) + 1
        column_gap = 12
        node_width = min(
            340,
            (body.width - 48 - column_gap * (columns - 1)) // columns,
        )
        node_height = 100
        row_gap = 16
        tree_width = columns * node_width + (columns - 1) * column_gap
        tree_x = body.centerx - tree_width // 2
        self.tree_viewport = pygame.Rect(
            body.x + 12, body.y + 72, body.width - 24, body.height - 90
        )
        self.tree_content_height = rows * node_height + (rows - 1) * row_gap
        max_scroll = max(
            0, self.tree_content_height - self.tree_viewport.height
        )
        self.technology_scroll = max(
            0, min(self.technology_scroll, max_scroll)
        )
        tree_y = self.tree_viewport.y - self.technology_scroll
        rectangles = {}
        for node in tech_tree:
            column, row = node["position"]
            rectangles[node["id"]] = pygame.Rect(
                tree_x + column * (node_width + column_gap),
                tree_y + row * (node_height + row_gap),
                node_width,
                node_height,
            )

        previous_clip = surface.get_clip()
        surface.set_clip(self.tree_viewport)
        for node in tech_tree:
            target_rect = rectangles[node["id"]]
            for requirement in node["requires"]:
                source_rect = rectangles[requirement]
                line_color = (
                    (112, 151, 125)
                    if requirement in country.techs else (66, 83, 91)
                )
                pygame.draw.line(
                    surface, line_color,
                    source_rect.midbottom, target_rect.midtop, 2,
                )

        names = {node["id"]: node["short"] for node in tech_tree}
        active_upgrade = country.active_upgrade or {}
        for node in tech_tree:
            rect = rectangles[node["id"]]
            if not rect.colliderect(self.tree_viewport):
                continue
            researched = node["id"] in country.techs
            unlocked = all(required in country.techs for required in node["requires"])
            branch_locked = technology_branch_locked(
                country.techs, node["id"], tech_tree
            )
            affordable = (
                country.money >= node["cost"]
                and country.research_points >= node["points"]
            )
            is_active = (
                active_upgrade.get("kind") == "technology"
                and active_upgrade.get("id") == node["id"]
            )
            available = (
                unlocked and affordable and not branch_locked
                and not researched and not active_upgrade
            )
            fill = (
                (43, 64, 54) if researched
                else (56, 61, 46) if available
                else (52, 35, 35) if branch_locked
                else CARD if unlocked
                else (25, 34, 41)
            )
            border = GREEN if researched else GOLD if available else EDGE
            rounded_panel(surface, rect, fill, border, 7)
            surface.blit(
                fit_text(surface, node["name"], rect.width - 16, 12, TEXT, True),
                (rect.x + 8, rect.y + 6),
            )
            surface.blit(
                fit_text(surface, node["effect"], rect.width - 16, 10, MUTED),
                (rect.x + 8, rect.y + 27),
            )
            requirement_text = "Основа" if not node["requires"] else "Требует: " + ", ".join(
                names[required] for required in node["requires"]
            )
            surface.blit(
                fit_text(surface, requirement_text, rect.width - 16, 9, MUTED),
                (rect.x + 8, rect.y + 45),
            )
            cost = font(9, True).render(
                f"${node['cost']}  ·  {node['points']} оч.",
                True, TEXT if available else MUTED,
            )
            surface.blit(cost, (rect.x + 8, rect.y + 62))
            button_rect = pygame.Rect(
                rect.x + 7, rect.bottom - 27, rect.width - 14, 21
            )
            if not self.tree_viewport.contains(button_rect):
                continue
            button = self.add_button(
                button_rect,
                (
                    "ИЗУЧЕНО" if researched
                    else f"ИЗУЧАЕТСЯ · {active_upgrade['remaining_days']} дн."
                    if is_active
                    else "ДРУГАЯ ВЕТКА ВЫБРАНА" if branch_locked
                    else "ИЗУЧАТЬ" if unlocked
                    else "ЗАБЛОКИРОВАНО"
                ),
                lambda value=node["id"]: self.perform(
                    lambda: self.world.research_technology(self.world.player_id, value)
                ),
                enabled=available,
                size=9,
            )
            self.tree_button_ids.add(id(button))
        surface.set_clip(previous_clip)
        self._draw_tree_scrollbar(
            surface, self.tree_viewport, self.tree_content_height,
            self.technology_scroll,
        )

    def _draw_emergency_measures_screen(self, surface):
        country = self.world.countries[self.world.player_id]
        body = pygame.Rect(
            12, 74, surface.get_width() - 24, surface.get_height() - 150
        )
        rounded_panel(surface, body, (20, 30, 38), EDGE, 8)
        section_label(
            surface, "Глобальные экстренные меры",
            (body.x + 20, body.y + 16), 14,
        )
        active = country.active_upgrade or {}
        active_name = (
            active.get("id", "—") if active.get("kind") == "emergency_measure"
            else "нет"
        )
        stats = font(11).render(
            f"Введено мер: {len(country.emergency_measures)}/"
            f"{len(EMERGENCY_MEASURE_TREE)}  ·  "
            f"В разработке: {active_name}  ·  "
            f"Очки исследований: {country.research_points:.1f}  ·  "
            f"Казна: ${country.money:,.0f}",
            True, MUTED,
        )
        surface.blit(stats, (body.x + 20, body.y + 42))
        self.add_button(
            (body.right - 126, body.y + 16, 106, 34),
            "НАЗАД",
            lambda: setattr(self, "active_tab", "diplomacy"),
            color=CARD,
            size=11,
        )

        columns = max(node["position"][0] for node in EMERGENCY_MEASURE_TREE) + 1
        rows = max(node["position"][1] for node in EMERGENCY_MEASURE_TREE) + 1
        gap_x, gap_y = 12, 14
        node_width = min(
            340, (body.width - 48 - gap_x * (columns - 1)) // columns
        )
        node_height = 112
        self.tree_viewport = pygame.Rect(
            body.x + 12, body.y + 72, body.width - 24, body.height - 90
        )
        self.tree_content_height = rows * node_height + (rows - 1) * gap_y
        max_scroll = max(
            0, self.tree_content_height - self.tree_viewport.height
        )
        self.emergency_scroll = max(
            0, min(self.emergency_scroll, max_scroll)
        )
        tree_width = columns * node_width + (columns - 1) * gap_x
        tree_x = body.centerx - tree_width // 2
        tree_y = self.tree_viewport.y - self.emergency_scroll
        rectangles = {}
        names = {
            node["id"]: node["short"] for node in EMERGENCY_MEASURE_TREE
        }
        for node in EMERGENCY_MEASURE_TREE:
            column, row = node["position"]
            rectangles[node["id"]] = pygame.Rect(
                tree_x + column * (node_width + gap_x),
                tree_y + row * (node_height + gap_y),
                node_width, node_height,
            )

        previous_clip = surface.get_clip()
        surface.set_clip(self.tree_viewport)
        for node in EMERGENCY_MEASURE_TREE:
            target = rectangles[node["id"]]
            for requirement in node["requires"]:
                pygame.draw.line(
                    surface,
                    GREEN if requirement in country.emergency_measures
                    else (66, 83, 91),
                    rectangles[requirement].midbottom, target.midtop, 2,
                )

        for node in EMERGENCY_MEASURE_TREE:
            rect = rectangles[node["id"]]
            if not rect.colliderect(self.tree_viewport):
                continue
            completed = node["id"] in country.emergency_measures
            is_active = (
                active.get("kind") == "emergency_measure"
                and active.get("id") == node["id"]
            )
            available, _ = emergency_measure_available(
                country, node["id"], self.world
            )
            requirements_met = all(
                requirement in country.emergency_measures
                for requirement in node["requires"]
            )
            fill = (
                (43, 64, 54) if completed
                else (64, 57, 38) if is_active
                else (56, 61, 46) if available
                else CARD if requirements_met else (25, 34, 41)
            )
            rounded_panel(
                surface, rect, fill,
                GREEN if completed else GOLD if available else EDGE, 7,
            )
            surface.blit(
                fit_text(surface, node["name"], rect.width - 16, 12, TEXT, True),
                (rect.x + 8, rect.y + 6),
            )
            surface.blit(
                fit_text(surface, node["effect"], rect.width - 16, 9, MUTED),
                (rect.x + 8, rect.y + 27),
            )
            requirement_text = (
                "Международная инициатива" if not node["requires"]
                else "Нужно: " + ", ".join(
                    names[item] for item in node["requires"]
                )
            )
            surface.blit(
                fit_text(surface, requirement_text, rect.width - 16, 8, MUTED),
                (rect.x + 8, rect.y + 48),
            )
            surface.blit(
                fit_text(
                    surface,
                    f"${node['cost']}  ·  {node['points']} оч.  ·  {node['days']} дн.",
                    rect.width - 16, 9, TEXT,
                ),
                (rect.x + 8, rect.y + 65),
            )
            button_rect = pygame.Rect(
                rect.x + 7, rect.bottom - 26, rect.width - 14, 20
            )
            if not self.tree_viewport.contains(button_rect):
                continue
            label = (
                "ВВЕДЕНА" if completed
                else f"В ПРОЦЕССЕ · {active['remaining_days']} ДН."
                if is_active
                else "ВВЕСТИ МЕРУ" if available
                else "НЕДОСТУПНО"
            )
            button = self.add_button(
                button_rect,
                label,
                lambda value=node["id"]: self.perform(
                    lambda: self.world.start_emergency_measure(
                        self.world.player_id, value
                    )
                ),
                enabled=available,
                size=9,
            )
            self.tree_button_ids.add(id(button))
        surface.set_clip(previous_clip)
        self._draw_tree_scrollbar(
            surface, self.tree_viewport, self.tree_content_height,
            self.emergency_scroll,
        )

    def _draw_war(self, surface, country, y):
        viewport = self.war_content_rect
        max_scroll = max(0, self.war_content_height - viewport.height)
        self.war_scroll = max(0, min(max_scroll, self.war_scroll))
        top = y
        bottom = self._draw_war_content(
            surface, country, y - self.war_scroll
        )
        self.war_content_height = max(
            viewport.height, bottom - top + self.war_scroll
        )
        max_scroll = max(0, self.war_content_height - viewport.height)
        self.war_scroll = min(self.war_scroll, max_scroll)
        if max_scroll:
            track = pygame.Rect(viewport.right - 5, viewport.y + 2, 3, viewport.height - 4)
            thumb_height = max(
                24, round(track.height * viewport.height / self.war_content_height)
            )
            thumb_y = track.y + round(
                (track.height - thumb_height) * self.war_scroll / max_scroll
            )
            pygame.draw.rect(surface, (49, 63, 70), track, border_radius=2)
            pygame.draw.rect(
                surface, (174, 137, 80),
                (track.x, thumb_y, track.width, thumb_height),
                border_radius=2,
            )
            hint = font(8).render("ПРОКРУТКА", True, MUTED)
            surface.blit(
                hint, (viewport.right - hint.get_width() - 11, viewport.bottom - 12)
            )
        return bottom

    def _draw_war_content(self, surface, country, y):
        x, width = self.right_rect.x + 14, self.right_rect.width - 28
        player = self.world.countries[self.world.player_id]
        war = self.world.war_between(player.id, country.id) if country.id != player.id else None
        player_wars = self.world.wars_for(player.id)
        country_wars = self.world.wars_for(country.id)
        section_label(surface, "Силы и конфликты", (x, y + 3))
        y += 29

        report = country.economy_report(
            self.world.province_count(country.id),
            len(self.world.wars_for(country.id)),
            zombie_scenario=self.world.scenario_id == "zombie",
        )
        rows = (
            ("Численность армии", f"{country.army_size:,}".replace(",", " ") + " чел."),
            ("Военная сила", f"{country.military_strength(self.world):.0f}"),
            ("Боеготовность", f"{country.army_readiness:.0f}%"),
            ("Поддержка / усталость", f"{country.war_support:.0f}% / {country.war_exhaustion:.0f}%"),
            ("Расходы армии", f"−{report['military_spending']:.1f} / день"),
        )
        for label, value in rows:
            surface.blit(font(11).render(label, True, MUTED), (x, y))
            value_surface = fit_text(surface, value, width * 0.53, 11, TEXT, True)
            surface.blit(value_surface, (x + width - value_surface.get_width(), y))
            y += 21

        alliance = self.world.alliance_partner(country.id)
        alliance_text = f"Союзник: {alliance.name if alliance else 'нет'}"
        surface.blit(
            fit_text(surface, alliance_text, width, 11, TEXT),
            (x, y + 3),
        )
        y += 24

        y += 5
        section_label(
            surface, f"Конфликты страны · {len(country_wars)}", (x, y)
        )
        y += 23
        if not country_wars:
            surface.blit(font(11).render("Государство не участвует в войнах.", True, MUTED), (x, y))
            y += 24
        else:
            for active_war in country_wars[:3]:
                if active_war.objective.get("type") == "zombie_outbreak":
                    attackers, defenders = "Заражённые", "Коалиция выживших"
                else:
                    attackers = ", ".join(
                        self.world.countries[item].name
                        for item in active_war.attackers
                        if item in self.world.countries
                    )
                    defenders = ", ".join(
                        self.world.countries[item].name
                        for item in active_war.defenders
                        if item in self.world.countries
                    )
                names = fit_text(
                    surface, f"Стороны: {attackers} ↔ {defenders}",
                    width, 10, TEXT, True,
                )
                surface.blit(names, (x, y))
                y += 17
                objective = self.world.countries.get(active_war.objective.get("target"))
                objective_name = objective.name if objective else "без цели"
                goal = fit_text(
                    surface, f"Цель: {objective_name}  ·  статус: активна",
                    width, 10, MUTED,
                )
                surface.blit(goal, (x, y))
                y += 16
                score = fit_text(
                    surface,
                    f"Счёт {active_war.attacker_score:.0f}:{active_war.defender_score:.0f}"
                    f"  ·  операции {active_war.battles}",
                    width, 10, MUTED,
                )
                surface.blit(score, (x, y))
                y += 27
                if active_war.peace_offer:
                    offer = active_war.peace_offer
                    offer_state = (
                        f"Мир: {self.world.countries[offer['proposer']].name} → "
                        f"{self.world.countries[offer['recipient']].name}"
                    )
                    surface.blit(
                        fit_text(surface, offer_state, width, 10, GOLD),
                        (x, y),
                    )
                    y += 17

        if country.id == player.id:
            offer_war = next(
                (
                    active_war for active_war in player_wars
                    if active_war.peace_offer
                    and player.id in (
                        active_war.peace_offer["proposer"],
                        active_war.peace_offer["recipient"],
                    )
                ),
                None,
            )
            if offer_war:
                y = self._draw_peace_offer_controls(
                    surface, offer_war, player, x, y, width
                )
            half = (width - 6) // 2
            self.add_button(
                (x, y, half, 34), "Мобилизовать  −300",
                lambda: self.perform(lambda: self.world.mobilize(player.id)),
                enabled=bool(player.wars) and player.war_support < 90,
                size=10,
            )
            self.add_button(
                (x + half + 6, y, half, 34), "Пополнить  −400",
                lambda: self.perform(lambda: self.world.recruit(player.id)),
                enabled=self.world.can_recruit(player.id),
                size=10,
            )
            return y + 34

        if not war:
            self.add_button(
                (x, y, width, 35), "Объявить войну",
                lambda: self.perform(lambda: self.world.declare_war(player.id, country.id)),
                enabled=not player.wars and not country.wars,
                color=(69, 47, 45),
            )
            return y + 35

        casualties_player = sum(war.casualties.get(item, 0) for item in war.side(player.id))
        casualties_enemy = sum(war.casualties.get(item, 0) for item in war.enemies(player.id))
        attacker_names = ", ".join(
            self.world.countries[item].name for item in war.attackers
        )
        defender_names = ", ".join(
            self.world.countries[item].name for item in war.defenders
        )
        sides = fit_text(
            surface, f"Стороны: {attacker_names}  ↔  {defender_names}",
            width, 10, TEXT,
        )
        surface.blit(sides, (x, y))
        y += 16
        summary = fit_text(
            surface,
            f"Участники: {len(war.attackers)} против {len(war.defenders)}"
            f"  ·  потери {casualties_player:,}:{casualties_enemy:,}".replace(",", " "),
            width, 10, MUTED,
        )
        surface.blit(summary, (x, y))
        y += 23
        half = (width - 6) // 2
        self.add_button(
            (x, y, half, 32), "Операция  −120",
            lambda: self.perform(lambda: self.world.resolve_conflict(player.id, country.id)),
            enabled=self.world.can_attack(player.id, country.id) and player.money >= 120,
            color=(69, 47, 45),
            size=10,
        )
        if war.peace_offer:
            y += 37
            return self._draw_peace_offer_controls(
                surface, war, player, x, y, width
            )

        y += 37
        section_label(surface, "Предложить условия мира", (x, y))
        y += 21
        self.add_button(
            (x, y, half, 31), "Перемирие · статус-кво",
            lambda: self.perform(
                lambda: self.world.offer_peace(player.id, country.id, "status_quo")
            ),
            color=(48, 69, 58),
            size=9,
        )
        self.add_button(
            (x + half + 6, y, half, 31), "Сохранить занятое",
            lambda: self.perform(
                lambda: self.world.offer_peace(player.id, country.id, "transfer")
            ),
            size=9,
        )
        y += 36
        self.add_button(
            (x, y, half, 31), "Репарации",
            lambda: self.perform(
                lambda: self.world.offer_peace(player.id, country.id, "reparations")
            ),
            size=9,
        )
        self.add_button(
            (x + half + 6, y, half, 31), "Капитуляция",
            lambda: self.perform(
                lambda: self.world.offer_peace(player.id, country.id, "capitulation")
            ),
            enabled=self.world.can_capitulate(war, player.id),
            color=(69, 47, 45),
            size=9,
        )
        return y + 31

    def _draw_peace_offer_controls(self, surface, war, player, x, y, width):
        offer = war.peace_offer
        proposer = self.world.countries[offer["proposer"]]
        recipient = self.world.countries[offer["recipient"]]
        term = PEACE_TERM_NAMES.get(offer["terms"], offer["terms"])
        message = fit_text(
            surface,
            f"{proposer.name} → {recipient.name}: {term}",
            width,
            10,
            GOLD,
        )
        surface.blit(message, (x, y))
        y += 20
        half = (width - 6) // 2
        if offer["recipient"] == player.id:
            self.add_button(
                (x, y, half, 32), "Принять условия",
                lambda: self.perform(
                    lambda: self.world.respond_peace_offer(war.id, player.id, True)
                ),
                color=(48, 69, 58),
                size=9,
            )
            self.add_button(
                (x + half + 6, y, half, 32), "Отклонить",
                lambda: self.perform(
                    lambda: self.world.respond_peace_offer(war.id, player.id, False)
                ),
                color=(69, 47, 45),
                size=9,
            )
            return y + 38
        if offer["proposer"] == player.id:
            self.add_button(
                (x, y, width, 32), "Отозвать предложение",
                lambda: self.perform(
                    lambda: self.world.withdraw_peace_offer(war.id, player.id)
                ),
                size=10,
            )
            return y + 38
        surface.blit(
            font(10).render("Предложение ожидает ответа сторон.", True, MUTED),
            (x, y),
        )
        return y + 18

    def _draw_events(self, surface, y):
        x, width = self.right_rect.x + 14, self.right_rect.width - 28
        gap = 5
        slot_width = (width - gap * 2) // 3
        for index in range(3):
            self.add_button(
                (x + index * (slot_width + gap), y, slot_width, 31),
                f"СЛОТ {index + 1}",
                lambda slot=index + 1: self.save_slot_game(slot),
                size=10,
            )
        y += 47
        section_label(surface, "Хронология", (x, y))
        y += 25
        for event in self.world.events[:8]:
            if y >= self.right_rect.bottom - 70:
                break
            date = f"{event['year']}  ·  ДЕНЬ {event['day'] + 1}"
            surface.blit(font(9, True).render(date, True, GOLD), (x, y))
            y += 15
            text_lines = self._draw_wrapped(
                surface, event["text"], x, y, font(10), MUTED, width, 2,
            )
            y += text_lines * 13 + 3
            consequences = event.get("consequences")
            if consequences:
                label = font(8, True).render("ПОСЛЕДСТВИЯ", True, GOLD)
                surface.blit(label, (x, y))
                y += 11
                consequence_lines = self._draw_wrapped(
                    surface, consequences, x, y, font(9),
                    (153, 177, 157), width, 2,
                )
                y += consequence_lines * 12 + 4
            y += 7

    def _draw_relationships(self, surface, y, viewport):
        start_y = y
        x = viewport.x + 4
        width = viewport.width - 14
        player = self.world.countries[self.world.player_id]
        y -= self.relationship_scroll
        previous_clip = surface.get_clip()
        surface.set_clip(viewport)

        section_label(surface, "Активные войны", (x, y + 3))
        y += 25
        wars = self.world.wars_for(player.id)
        if not wars:
            surface.blit(font(11).render("Активных войн нет", True, MUTED), (x, y))
            y += 24
        for war in wars:
            attackers = ", ".join(
                self.world.countries[item].name
                for item in war.attackers if item in self.world.countries
            )
            defenders = ", ".join(
                self.world.countries[item].name
                for item in war.defenders if item in self.world.countries
            )
            rect = pygame.Rect(x, y, width, 54)
            rounded_panel(surface, rect, CARD, None, 5)
            surface.blit(
                fit_text(surface, f"{attackers}  —  {defenders}", width - 14, 11, TEXT, True),
                (rect.x + 7, rect.y + 6),
            )
            details = (
                f"Начало: день {war.started_day}  ·  "
                f"Операций: {war.battles}  ·  "
                f"Счёт {war.attacker_score:.0f}:{war.defender_score:.0f}"
            )
            surface.blit(
                fit_text(surface, details, width - 14, 9, MUTED),
                (rect.x + 7, rect.y + 29),
            )
            y += 59

        y += 5
        section_label(surface, "Ваш союз", (x, y + 3))
        y += 25
        player_alliance = self.world.alliance_partner(player.id)
        if not player_alliance:
            surface.blit(font(11).render("У вас нет действующего союза", True, MUTED), (x, y))
            y += 24
        else:
            surface.blit(
                fit_text(
                    surface, f"{player.name}  ↔  {player_alliance.name}",
                    width, 11, TEXT,
                ),
                (x + 2, y),
            )
            y += 22

        y += 5
        section_label(surface, f"Дипломатические связи · {player.name}", (x, y + 3))
        y += 25
        countries = sorted(
            (country for country in self.world.countries.values()
             if country.id != player.id and not country.is_defeated),
            key=lambda country: country.relations.get(player.id, 0),
            reverse=True,
        )
        player_wars = self.world.wars_for(player.id)
        for country in countries:
            relation = country.relations.get(player.id, 0)
            conflict = next(
                (
                    war for war in player_wars
                    if country.id in war.attackers + war.defenders
                ),
                None,
            )
            if player_alliance and player_alliance.id == country.id:
                status = "Союзник"
            elif conflict:
                enemies = ", ".join(
                    self.world.countries[item].name
                    for item in (
                        conflict.enemies(player.id)
                        if conflict.side(country.id) != conflict.side(player.id)
                        else conflict.enemies(country.id)
                    )
                    if item in self.world.countries
                )
                status = (
                    f"Война против: {enemies}"
                    if conflict.side(country.id) != conflict.side(player.id)
                    else f"Союзник в войне против: {enemies}"
                )
            elif country.id in player.treaties:
                treaty = player.treaties[country.id]
                remaining = (
                    f" · {max(0, treaty['expires'] - self.world.absolute_day())} дн."
                    if treaty.get("expires") is not None else ""
                )
                status = f"{treaty['name']}{remaining}"
            elif player.pacts.get(country.id, 0) > self.world.absolute_day():
                remaining = player.pacts[country.id] - self.world.absolute_day()
                status = f"Ненападение · {remaining} дн."
            else:
                status = "Мир"
            surface.blit(
                fit_text(surface, country.name, width * 0.62, 10, TEXT, True),
                (x, y),
            )
            relation_text = f"{relation:+d}  ·  {status}"
            surface.blit(
                fit_text(surface, relation_text, width * 0.72, 9, MUTED),
                (x + width * 0.28, y),
            )
            y += 20

        surface.set_clip(previous_clip)
        self.relationship_content_height = max(
            viewport.height, y - start_y + self.relationship_scroll
        )
        self._draw_tree_scrollbar(
            surface, viewport, self.relationship_content_height,
            self.relationship_scroll,
        )

    def _draw_bottom(self, surface):
        rounded_panel(surface, self.bottom_rect, (18, 27, 35), EDGE, 8)
        x, y = self.bottom_rect.x + 15, self.bottom_rect.y
        section_label(surface, "Игровое время", (x, y + 10), 10)
        status = "ПАУЗА" if self.world.time.paused else f"СКОРОСТЬ  ×{self.world.time.speed:g}"
        status_color = GOLD if self.world.time.paused else GREEN
        surface.blit(font(13, True).render(status, True, status_color), (x, y + 30))
        progress = max(0, min(1, self.day_timer / max(0.01, config.DAY_SECONDS)))
        bar = pygame.Rect(x + 135, y + 31, 160, 5)
        pygame.draw.rect(surface, (43, 57, 64), bar, border_radius=3)
        if progress and not self.world.time.paused:
            pygame.draw.rect(surface, GOLD, (bar.x, bar.y, round(bar.width * progress), bar.height),
                             border_radius=3)
        surface.blit(font(10).render("1 день = 2 сек. при ×1", True, MUTED),
                     (x + 135, y + 39))

        labels = (("Ⅱ", "PAUSE"), ("×1", 1), ("×2", 2), ("×4", 4), ("×8", 8))
        button_width = 54
        gap = 6
        total_width = len(labels) * button_width + (len(labels) - 1) * gap
        start_x = self.bottom_rect.right - total_width - 14
        news_rect = pygame.Rect(start_x - 154, y + 12, 144, 37)
        self.add_button(
            news_rect,
            "НОВОСТИ: АВТО" if self.auto_skip_news else "НОВОСТИ: ВЫКЛ",
            self.toggle_auto_skip_news,
            color=(56, 76, 62) if self.auto_skip_news else CARD,
            size=10,
        )
        for index, (label, speed) in enumerate(labels):
            rect = pygame.Rect(start_x + index * (button_width + gap), y + 12,
                               button_width, 37)
            if speed == "PAUSE":
                callback = self.world.time.toggle_pause
                selected = self.world.time.paused
            else:
                callback = lambda value=speed: self.world.time.set_speed(value)
                selected = not self.world.time.paused and self.world.time.speed == speed
            self.add_button(
                rect, "▶" if speed == "PAUSE" and self.world.time.paused else label,
                callback,
                color=(72, 62, 42) if selected else CARD,
                size=12,
            )

    def _draw_notifications(self, surface):
        y = self.map_rect.y + 14
        for notification in self.world.notifications[:2]:
            text = fit_text(surface, notification["text"], self.map_rect.width - 40, 13, TEXT)
            width = text.get_width() + 24
            rect = pygame.Rect(self.map_rect.centerx - width // 2, y, width, 34)
            rounded_panel(surface, rect, (26, 40, 49), GOLD, 6)
            surface.blit(text, (rect.x + 12, rect.y + 9))
            y += 41

    def _draw_event_modal(self, surface):
        event = self.world.pending_modal_events[0]
        if event.get("decision_id"):
            self._draw_decision_modal(surface, event)
            return
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((5, 10, 15, 195))
        surface.blit(overlay, (0, 0))

        width = min(680, surface.get_width() - 36)
        height = min(300, surface.get_height() - 36)
        panel = pygame.Rect(0, 0, width, height)
        panel.center = surface.get_rect().center
        rounded_panel(surface, panel, (24, 35, 44), GOLD, 10)
        title = font(12, True).render("ВАЖНОЕ СОБЫТИЕ", True, GOLD)
        surface.blit(title, title.get_rect(center=(panel.centerx, panel.y + 34)))
        date_text = font(10).render(
            f"{event['year']} год  ·  день {event['day'] + 1}",
            True, MUTED,
        )
        surface.blit(
            date_text, date_text.get_rect(center=(panel.centerx, panel.y + 59))
        )
        text_y = panel.y + 88
        text_lines = self._draw_wrapped(
            surface, event["text"], panel.x + 28, panel.y + 88,
            font(15), TEXT, panel.width - 56, 4,
        )
        consequences = event.get("consequences")
        if consequences:
            consequence_y = text_y + text_lines * 14 + 14
            surface.blit(
                font(9, True).render("ПОСЛЕДСТВИЯ", True, GOLD),
                (panel.x + 28, consequence_y),
            )
            self._draw_wrapped(
                surface, consequences, panel.x + 28, consequence_y + 15,
                font(11), (173, 194, 174), panel.width - 56, 3,
            )
        self.add_button(
            (panel.centerx - 90, panel.bottom - 58, 180, 38),
            "ПРОДОЛЖИТЬ",
            self.world.acknowledge_modal_event,
            color=(67, 76, 57),
            size=12,
        )

    def _draw_decision_modal(self, surface, event):
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((5, 10, 15, 215))
        surface.blit(overlay, (0, 0))

        width = min(760, surface.get_width() - 36)
        height = min(560, surface.get_height() - 36)
        panel = pygame.Rect(0, 0, width, height)
        panel.center = surface.get_rect().center
        rounded_panel(surface, panel, (24, 35, 44), GOLD, 10)
        title = font(12, True).render(
            "МИРОВОЕ РЕШЕНИЕ · ВЫБОР НЕ ПРОПУСКАЕТСЯ", True, GOLD
        )
        surface.blit(title, title.get_rect(center=(panel.centerx, panel.y + 28)))
        country = self.world.countries.get(event["country_id"])
        subject = country.name if country else event["country_id"]
        event_title = fit_text(
            surface, event["text"], panel.width - 44, 19, TEXT, True
        )
        surface.blit(
            event_title,
            event_title.get_rect(center=(panel.centerx, panel.y + 60)),
        )
        description = f"{subject}: {event.get('description', '')}"
        self._draw_wrapped(
            surface, description, panel.x + 26, panel.y + 88,
            font(12), MUTED, panel.width - 52, 3,
        )

        card_height = 142
        gap = 12
        card_width = panel.width - 44
        card_x = panel.x + 22
        cards_y = panel.y + 172
        for index, choice in enumerate(event.get("choices", ())):
            rect = pygame.Rect(
                card_x, cards_y + index * (card_height + gap),
                card_width, card_height,
            )
            rounded_panel(surface, rect, CARD, EDGE, 8)
            text_width = rect.width - 205
            surface.blit(
                fit_text(
                    surface, choice["name"], text_width, 13, TEXT, True
                ),
                (rect.x + 12, rect.y + 10),
            )
            self._draw_wrapped(
                surface, choice["consequence"], rect.x + 12, rect.y + 34,
                font(10), MUTED, text_width, 5,
            )
            risk = choice.get("risk")
            if risk:
                risk_text = f"РИСК {risk['chance']:.0%}: {risk['consequence']}"
                self._draw_wrapped(
                    surface, risk_text, rect.x + 12, rect.y + 91,
                    font(9), GOLD, text_width, 3,
                )
            button = self.add_button(
                (rect.right - 178, rect.y + 49, 164, 42),
                "ВЫБРАТЬ",
                lambda value=index: self.world.resolve_decision_event(value),
                color=(67, 76, 57),
                size=11,
            )
            self.decision_button_ids.add(id(button))

    def toggle_auto_skip_news(self):
        self.auto_skip_news = not self.auto_skip_news
        self.world.auto_skip_news = self.auto_skip_news
        if self.auto_skip_news:
            while self.world.pending_modal_events:
                self.world.acknowledge_modal_event()

    @staticmethod
    def _draw_wrapped(surface, text, x, y, typeface, color, max_width, max_lines=3):
        if isinstance(text, (list, tuple)):
            text = " · ".join(str(item) for item in text)
        lines, line = [], ""
        for word in text.split():
            candidate = f"{line} {word}".strip()
            if line and typeface.size(candidate)[0] > max_width:
                lines.append(line)
                line = word
            else:
                line = candidate
        if line:
            lines.append(line)
        for index, content in enumerate(lines[:max_lines]):
            surface.blit(typeface.render(content, True, color), (x, y + index * 14))
        return min(len(lines), max_lines)

    def save_slot_game(self, slot):
        self.save_system.save(self.world, slot)
        message = f"Игра сохранена в слот {slot}."
        self.last_message = message
        self.message_ttl = 5
        self.world.add_event(message)
