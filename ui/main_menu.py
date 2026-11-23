import json
import os

import pygame

from ui.buttons import Button
from ui.theme import (
    BACKGROUND, CARD, EDGE, GOLD, MUTED, TEXT, fit_text, font, rounded_panel,
    draw_flag, set_scale,
)
from ui.world_map import WorldMap
from ui.localization import get_language, set_language, translate


class MainMenu:
    def __init__(self, screen, world, save_system, start_game_callback):
        self.screen = screen
        self.world = world
        self.save_system = save_system
        self.start_game_callback = start_game_callback
        self.mode = "menu"
        self.selected_country = None
        self.scenario_id = "modern"
        self.scroll = 0
        self.settings_path = os.path.join(save_system.save_dir, "settings.json")
        self.settings = self._load_settings()
        set_language(self.settings["language"])
        self.background = None
        self.background_map = None

        self.world.load_data(self.scenario_id, build_provinces=False)
        self.refresh_country_list()

    def refresh_country_list(self):
        selectable = self.world._scenario_settings().get("selectable_countries")
        self.countries = sorted(
            (
                country.to_dict()
                for country in self.world.countries.values()
                if not selectable or country.id in selectable
            ),
            key=lambda country: country["name"],
        )

    def choose_scenario(self, scenario_id):
        self.scenario_id = scenario_id
        self.world.load_data(scenario_id, build_provinces=False)
        self.refresh_country_list()
        self.selected_country = None
        self.scroll = 0
        self.background = None
        self.mode = "countries"

    def start_selected_country(self):
        if self.selected_country:
            self.world.new_game(self.selected_country, self.scenario_id)
            self.start_game_callback()

    def font(self, size, bold=False):
        return font(size, bold)

    def make_menu_buttons(self):
        width, height = self.screen.get_size()
        button_width = min(360, max(280, round(width * 0.24)))
        center_x = width // 2
        start_y = max(244, height // 2 - 28) + 22
        actions = [
            ("НОВАЯ КАМПАНИЯ", lambda: setattr(self, "mode", "scenarios")),
            ("ПРОДОЛЖИТЬ", self.continue_game),
            ("ВЫБРАТЬ СТРАНУ", lambda: setattr(self, "mode", "scenarios")),
            ("НАСТРОЙКИ", lambda: setattr(self, "mode", "settings")),
            ("ВЫХОД", lambda: setattr(self, "mode", "exit")),
        ]
        return [
            Button(
                (center_x - button_width // 2, start_y + index * 58, button_width, 46),
                label, callback,
                color=(59, 53, 42) if index == 0 else CARD,
            )
            for index, (label, callback) in enumerate(actions)
        ]

    def continue_game(self):
        for slot in range(1, 4):
            success, _ = self.save_system.load(self.world, slot)
            if success:
                self.start_game_callback()
                return

    def _load_settings(self):
        settings = {"fullscreen": False, "sound": True, "language": "en"}
        try:
            with open(self.settings_path, "r", encoding="utf-8") as file:
                saved = json.load(file)
        except FileNotFoundError:
            return settings
        except (OSError, json.JSONDecodeError) as error:
            print(f"Could not load settings from {self.settings_path}: {error}")
            return settings
        if isinstance(saved, dict):
            settings["sound"] = bool(saved.get("sound", settings["sound"]))
            language = saved.get("language", settings["language"])
            if language in ("en", "ru"):
                settings["language"] = language
        return settings

    def _save_settings(self):
        temporary = self.settings_path + ".tmp"
        with open(temporary, "w", encoding="utf-8") as file:
            json.dump(self.settings, file, ensure_ascii=False, indent=2)
        os.replace(temporary, self.settings_path)

    def _settings_rects(self, width, height):
        start_y = height // 2 - 84
        return tuple(
            pygame.Rect(width // 2 - 170, start_y + index * 62, 340, 48)
            for index in range(3)
        )

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if self.mode != "menu":
                self.mode = "menu"
                return
        if self.mode == "menu":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for button in self.make_menu_buttons():
                    if button.rect.collidepoint(event.pos):
                        button.handle_event(event)
                        break
        elif self.mode == "countries":
            self.handle_country_event(event)
        elif self.mode == "scenarios":
            self.handle_scenario_event(event)
        elif self.mode == "settings":
            self.handle_settings_event(event)

    def handle_settings_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            width, height = self.screen.get_size()
            sound_rect, language_rect, back_rect = self._settings_rects(width, height)
            if sound_rect.collidepoint(event.pos):
                self.settings["sound"] = not self.settings["sound"]
                self._save_settings()
            elif language_rect.collidepoint(event.pos):
                language = "ru" if get_language() == "en" else "en"
                set_language(language)
                self.settings["language"] = language
                self._save_settings()
                self.background = None
            elif back_rect.collidepoint(event.pos):
                self.mode = "menu"

    def handle_country_event(self, event):
        page_size = 12
        max_scroll = max(0, len(self.countries) - page_size)
        if event.type == pygame.MOUSEWHEEL:
            if self._country_area().collidepoint(pygame.mouse.get_pos()):
                self.scroll = max(0, min(max_scroll, self.scroll - event.y * 4))
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER) and self.selected_country:
                self.start_selected_country()
            elif event.key in (pygame.K_RIGHT, pygame.K_PAGEDOWN):
                self.scroll = min(max_scroll, self.scroll + page_size)
            elif event.key in (pygame.K_LEFT, pygame.K_PAGEUP):
                self.scroll = max(0, self.scroll - page_size)
            elif event.key == pygame.K_ESCAPE:
                self.mode = "scenarios"
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            width, height = self.screen.get_size()
            for index, country in enumerate(self.countries[self.scroll:self.scroll + page_size]):
                if self._country_card(index, width, height).collidepoint(event.pos):
                    self.selected_country = country["id"]
                    return
            if self._button_rects(width, height)["start"].collidepoint(event.pos):
                self.start_selected_country()
            elif self._button_rects(width, height)["back"].collidepoint(event.pos):
                self.mode = "scenarios"
            elif self._button_rects(width, height)["previous"].collidepoint(event.pos):
                self.scroll = max(0, self.scroll - page_size)
            elif self._button_rects(width, height)["next"].collidepoint(event.pos):
                self.scroll = min(max_scroll, self.scroll + page_size)

    def handle_scenario_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.mode = "menu"
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return
        width, height = self.screen.get_size()
        cards = self._scenario_cards(width, height)
        for scenario_id, rect in cards:
            if rect.collidepoint(event.pos):
                self.choose_scenario(scenario_id)
                return
        if pygame.Rect(width - 150, height - 66, 126, 42).collidepoint(event.pos):
            self.mode = "menu"

    def draw(self, surface):
        self.screen = surface
        width, height = surface.get_size()
        set_scale(min(1.1, max(0.9, min(width / 1280, height / 720))))
        self._ensure_background(surface.get_size())
        surface.blit(self.background, (0, 0))
        if self.mode == "menu":
            self._draw_home(surface, width, height)
        elif self.mode == "scenarios":
            self._draw_scenarios(surface, width, height)
        elif self.mode == "countries":
            self._draw_countries(surface, width, height)
        elif self.mode == "settings":
            self._draw_settings(surface, width, height)
        elif self.mode == "exit":
            pygame.event.post(pygame.event.Event(pygame.QUIT))
        pygame.display.flip()

    def _ensure_background(self, size):
        if self.background is not None and self.background.get_size() == size:
            return
        self.background = pygame.Surface(size)
        self.background.fill(BACKGROUND)
        self.background_map = WorldMap(pygame.Rect(0, 0, *size))
        self.background_map.zoom = min(size[0] / 1280, size[1] / 720) * 0.9
        self.background_map.camera_x = 640
        self.background_map.camera_y = 360
        self.background_map.draw(self.background, self.world)
        shade = pygame.Surface(size, pygame.SRCALPHA)
        shade.fill((8, 14, 21, 174))
        for y in range(size[1]):
            alpha = round(60 * y / max(1, size[1]))
            pygame.draw.line(shade, (8, 14, 21, alpha), (0, y), (size[0], y))
        self.background.blit(shade, (0, 0))

    def _draw_home(self, surface, width, height):
        logo = font(12, True).render("STRATEGIC ATLAS  ·  1936 / 2026", True, GOLD)
        surface.blit(logo, logo.get_rect(center=(width // 2, max(74, height // 6))))
        title = font(max(42, min(74, round(width * 0.046))), True).render(
            "WORLD CONQUEST", True, TEXT,
        )
        surface.blit(title, title.get_rect(center=(width // 2, max(124, height // 6 + 55))))
        subtitle = font(17).render(
            "ГЛОБАЛЬНАЯ СТРАТЕГИЯ • ЭКОНОМИКА • ДИПЛОМАТИЯ",
            True, (184, 197, 194),
        )
        surface.blit(subtitle, subtitle.get_rect(center=(width // 2, max(158, height // 6 + 100))))

        panel_width = min(470, max(340, round(width * 0.34)))
        panel_height = 354
        panel = pygame.Rect(width // 2 - panel_width // 2,
                            max(220, height // 2 - 28), panel_width, panel_height)
        rounded_panel(surface, panel, (19, 29, 37), (70, 89, 96), 10)
        pygame.draw.line(surface, GOLD, (panel.x + 18, panel.y + 1),
                         (panel.x + 82, panel.y + 1), 2)
        for button in self.make_menu_buttons():
            button.draw(surface, font(14, True))
        note = font(10).render("Колёсико — масштаб карты  ·  ЛКМ / СКМ — перемещение",
                               True, MUTED)
        surface.blit(note, note.get_rect(center=(width // 2, height - 26)))

    def _scenario_cards(self, width, height):
        card_width = min(430, max(190, (width - 72 - 36) // 3))
        card_height = 258
        gap = 18
        total_width = card_width * 3 + gap * 2
        start_x = (width - total_width) // 2
        y = max(174, height // 2 - card_height // 2)
        return [
            (
                scenario_id,
                pygame.Rect(start_x + index * (card_width + gap), y,
                            card_width, card_height),
            )
            for index, scenario_id in enumerate(("ww2", "modern", "zombie"))
        ]

    def _draw_scenarios(self, surface, width, height):
        self._draw_heading(surface, width, "Выберите кампанию",
                           "Сценарий задаёт дату, государства и особые правила мира")
        for scenario_id, rect in self._scenario_cards(width, height):
            selected = scenario_id == self.scenario_id
            rounded_panel(surface, rect, (23, 34, 43), GOLD if selected else EDGE, 10, 2)
            metadata = {
                "ww2": (
                    (94, 65, 53), "1936", "ВТОРАЯ МИРОВАЯ",
                    "Межвоенный мир, исторические державы\nи приближённые границы эпохи.",
                ),
                "modern": (
                    (51, 79, 83), "2026", "СОВРЕМЕННЫЙ МИР",
                    "Современные государства, реальные\nграницы и актуальный баланс сил.",
                ),
                "zombie": (
                    (70, 83, 49), "2031", "ВСПЫШКА ЗАРАЖЕНИЯ",
                    "Глобальная угроза, заражённые регионы\nна каждом континенте, единый фронт.",
                ),
            }[scenario_id]
            accent, era, label, description = metadata
            pygame.draw.rect(surface, accent, (rect.x + 12, rect.y + 12, rect.width - 24, 76),
                             border_radius=7)
            era_surface = font(32, True).render(era, True, GOLD)
            surface.blit(era_surface, (rect.x + 25, rect.y + 28))
            surface.blit(fit_text(surface, label, rect.width - 46, 20, TEXT, True),
                         (rect.x + 25, rect.y + 112))
            self._draw_lines(surface, description, rect.x + 25, rect.y + 150,
                             rect.width - 50, 14, MUTED, 23)
            choose = Button(
                (rect.x + 20, rect.bottom - 52, rect.width - 40, 36),
                "ВЫБРАТЬ СЦЕНАРИЙ  →",
                lambda value=scenario_id: self.choose_scenario(value),
                color=(62, 55, 42) if selected else CARD,
            )
            choose.draw(surface, font(12, True))
        self._draw_back(surface, width, height)

    def _country_area(self):
        width, height = self.screen.get_size()
        return pygame.Rect(30, 138, width - 60, height - 218)

    def _country_card(self, index, width, height):
        columns = 4 if width >= 1100 else 3 if width >= 780 else 2
        area = self._country_area()
        gap = 10
        card_width = (area.width - (columns - 1) * gap) // columns
        card_height = 127
        row, column = divmod(index, columns)
        return pygame.Rect(area.x + column * (card_width + gap),
                           area.y + row * (card_height + gap), card_width, card_height)

    def _button_rects(self, width, height):
        y = height - 62
        return {
            "back": pygame.Rect(24, y, 118, 40),
            "previous": pygame.Rect(154, y, 118, 40),
            "next": pygame.Rect(284, y, 118, 40),
            "start": pygame.Rect(width - 220, y, 194, 40),
        }

    def _draw_countries(self, surface, width, height):
        self._draw_heading(surface, width, "Выберите государство",
                           "Нажмите на страну на карточке — затем начните кампанию")
        area = self._country_area()
        for index, country in enumerate(self.countries[self.scroll:self.scroll + 12]):
            rect = self._country_card(index, width, height)
            selected = country["id"] == self.selected_country
            hovered = rect.collidepoint(pygame.mouse.get_pos())
            rounded_panel(
                surface, rect,
                (39, 48, 48) if selected else (29, 40, 48) if hovered else (22, 32, 40),
                GOLD if selected else EDGE, 8, 2 if selected else 1,
            )
            color = tuple(country["color"])
            pygame.draw.rect(surface, color, (rect.x + 12, rect.y + 13, 5, rect.height - 26),
                             border_radius=3)
            flag_rect = pygame.Rect(rect.right - 58, rect.y + 12, 42, 26)
            draw_flag(surface, flag_rect, country["id"], color)
            name = fit_text(surface, country["name"], rect.width - 99, 16, TEXT, True)
            surface.blit(name, (rect.x + 27, rect.y + 13))
            population = int(country["population"])
            lines = (
                f"Население  {self._population(population)}",
                f"Экономика  {country['economy_level']}/10",
                f"Сложность  {country['difficulty']}",
            )
            for line_index, text in enumerate(lines):
                rendered = fit_text(surface, text, rect.width - 40, 11, MUTED)
                surface.blit(rendered, (rect.x + 27, rect.y + 42 + line_index * 19))
            if selected:
                dot = pygame.Rect(rect.right - 25, rect.y + 15, 9, 9)
                pygame.draw.circle(surface, GOLD, dot.center, 4)
        rects = self._button_rects(width, height)
        for name, label in (
            ("back", "← НАЗАД"),
            ("previous", "← ПРЕД."),
            ("next", "СЛЕД. →"),
            ("start", "НАЧАТЬ КАМПАНИЮ  →"),
        ):
            button = Button(
                rects[name], label,
                self.start_selected_country if name == "start" else None,
                color=(64, 56, 42) if name == "start" else CARD,
            )
            button.enabled = name != "start" or bool(self.selected_country)
            button.draw(surface, font(11, True))
        page = font(11, True).render(
            f"{min(self.scroll + 1, len(self.countries))}–"
            f"{min(self.scroll + 12, len(self.countries))} / {len(self.countries)}",
            True, MUTED,
        )
        surface.blit(page, page.get_rect(center=(width // 2, height - 41)))

    def _draw_settings(self, surface, width, height):
        self._draw_heading(surface, width, "Настройки", "Управление параметрами игры")
        rects = self._settings_rects(width, height)
        labels = [
            f"Звук событий  ·  {'ВКЛ' if self.settings['sound'] else 'ВЫКЛ'}",
            f"Язык  ·  {translate('English' if self.settings['language'] == 'en' else 'Русский')}",
            "←  Назад",
        ]
        for rect, label in zip(rects, labels):
            rounded_panel(surface, rect, CARD, EDGE, 7)
            rendered = font(14, True).render(label, True, TEXT)
            surface.blit(rendered, rendered.get_rect(center=rect.center))

    def _draw_heading(self, surface, width, title, subtitle):
        title_surface = font(27, True).render(title, True, TEXT)
        surface.blit(title_surface, title_surface.get_rect(center=(width // 2, 79)))
        subtitle_surface = fit_text(surface, subtitle, width - 80, 12, MUTED)
        surface.blit(subtitle_surface, subtitle_surface.get_rect(center=(width // 2, 108)))

    def _draw_back(self, surface, width, height):
        button = Button((width - 150, height - 66, 126, 42), "←  НАЗАД",
                        lambda: setattr(self, "mode", "menu"))
        button.draw(surface, font(11, True))

    @staticmethod
    def _draw_lines(surface, text, x, y, width, size, color, line_height):
        for index, line in enumerate(text.splitlines()):
            rendered = fit_text(surface, line, width, size, color)
            surface.blit(rendered, (x, y + index * line_height))

    @staticmethod
    def _population(value):
        if value >= 1_000_000_000:
            return f"{value / 1_000_000_000:.1f} млрд"
        return f"{value / 1_000_000:.1f} млн"
