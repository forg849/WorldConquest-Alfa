import math
import pygame

from game.world import point_in_polygon
from ui.theme import font as ui_font


OCEAN = (30, 55, 72)
OCEAN_GRID = (39, 67, 82)
COUNTRY_EDGE = (23, 35, 42)
REGION_EDGE = (42, 55, 60)
FRONT_DARK = (112, 19, 28)
FRONT_RED = (255, 67, 59)
TEXT = (232, 235, 226)
GOLD = (224, 184, 107)


class WorldMap:
    def __init__(self, rect):
        self.rect = pygame.Rect(rect)
        self.selected_id = None
        self.hovered_id = None
        self.selected_province_id = None
        self.hovered_province_id = None
        self.zoom = 1.0
        self.min_zoom = 0.6
        self.max_zoom = 32.0
        self.camera_x = 640
        self.camera_y = 360
        self.province_zoom = 3.0
        self.drag_button = None
        self.drag_start = None
        self.drag_position = None
        self.drag_moved = False
        self.is_dragging = False
        self.country_areas = {}
        self.country_label_rects = []
        self._small_font = ui_font(12)
        self._map_font = ui_font(14)
        self._map_surface = None
        self._map_cache_key = None
        self._hover_country_surface = None
        self._hover_country_key = None
        self._war_front_cache_key = None
        self._war_front_segments = ()
        self._drawing_offset = (0, 0)
        self._frame_scale = 1.0

    def resize(self, rect):
        self.rect = pygame.Rect(rect)

    def reset_camera(self):
        self.zoom = 1.0
        self.camera_x = 640
        self.camera_y = 360

    def _base_scale(self):
        return min(self.rect.width / 1280, self.rect.height / 720)

    def map_point(self, point):
        scale = self._base_scale() * self.zoom
        return (
            self.rect.centerx + (point[0] - self.camera_x) * scale,
            self.rect.centery + (point[1] - self.camera_y) * scale,
        )

    def unmap_point(self, position):
        scale = self._base_scale() * self.zoom
        return (
            (position[0] - self.rect.centerx) / scale + self.camera_x,
            (position[1] - self.rect.centery) / scale + self.camera_y,
        )

    def zoom_at(self, position, factor):
        scale = self._base_scale()
        if scale <= 0:
            return
        before = self.unmap_point(position)
        self.zoom = max(self.min_zoom, min(self.max_zoom, self.zoom * factor))
        scale *= self.zoom
        self.camera_x = before[0] - (position[0] - self.rect.centerx) / scale
        self.camera_y = before[1] - (position[1] - self.rect.centery) / scale

    def draw(self, surface, world, fonts=None):
        if self.rect.width <= 0 or self.rect.height <= 0:
            return
        previous_clip = surface.get_clip()
        surface.set_clip(self.rect)
        scale = self._base_scale() * self.zoom
        self._frame_scale = scale
        visible_bounds = (
            self.camera_x - self.rect.width / (2 * scale),
            self.camera_y - self.rect.height / (2 * scale),
            self.camera_x + self.rect.width / (2 * scale),
            self.camera_y + self.rect.height / (2 * scale),
        )
        self._cache_country_areas(world)
        cache_key = (
            self.rect.size, self.zoom, self.camera_x, self.camera_y,
            getattr(world, "map_revision", 0), self.selected_id, self.selected_province_id,
            self.is_dragging,
        )
        if self._map_surface is None or self._map_cache_key != cache_key:
            self._render_map_layer(world, visible_bounds, scale)
            self._map_cache_key = cache_key
        surface.blit(self._map_surface, self.rect.topleft)
        self._drawing_offset = (0, 0)
        self._draw_hovered_country(surface, world, visible_bounds)
        self._draw_hovered_admin_region(surface, world)
        self._draw_map_controls(surface)
        self._draw_hover_card(surface, world)
        surface.set_clip(previous_clip)
        pygame.draw.rect(surface, (78, 99, 111), self.rect, 1)

    def _render_map_layer(self, world, visible_bounds, scale):
        self._map_surface = pygame.Surface(self.rect.size)
        self._map_surface.fill(OCEAN)
        self._drawing_offset = self.rect.topleft
        self._map_surface.set_clip(self._map_surface.get_rect())
        self._draw_graticule(self._map_surface, scale)

        detailed = self.zoom >= 1.8 and not self.is_dragging
        base_regions = world.detailed_regions if detailed else world.regions
        for region in base_regions:
            if not self._bounds_visible(region.bounds, visible_bounds):
                continue
            country = world.countries.get(region.owner)
            if not country:
                continue
            source_points = region.points if not detailed or self.zoom >= 10 else region.render_points
            points = [self._screen_point(point) for point in source_points]
            if len(points) < 3:
                continue
            if region.owner == self.selected_id:
                fill = self._lighten(country.color, 13)
                edge = GOLD
                width = max(2, min(4, round(scale * 0.12)))
            else:
                fill = country.color
                edge = COUNTRY_EDGE
                width = max(1, min(2, round(scale * 0.055)))
            pygame.draw.polygon(self._map_surface, fill, points)
            pygame.draw.polygon(self._map_surface, edge, points, width)

        if world.scenario_id == "zombie" and self.zoom < self.province_zoom:
            self._draw_zombie_territories(
                self._map_surface, world, visible_bounds, scale
            )

        if self.zoom >= self.province_zoom and not self.is_dragging:
            self._draw_admin_regions(self._map_surface, world, visible_bounds, scale)
            self._draw_country_edges(self._map_surface, base_regions, visible_bounds, scale)
        if world.active_wars():
            self._draw_war_fronts(
                self._map_surface, world, visible_bounds,
                use_provinces=(
                    world.scenario_id == "zombie"
                    or self.zoom >= self.province_zoom and not self.is_dragging
                ),
                scale=scale,
            )
        if not self.is_dragging:
            self._draw_country_labels(self._map_surface, world, scale)
        self._map_surface.set_clip(None)

    def _draw_zombie_territories(self, surface, world, visible_bounds, scale):
        country = world.countries.get("zombies")
        if not country:
            return
        edge_width = max(1, min(2, round(scale * 0.06)))
        for province in world.visible_provinces(visible_bounds):
            if province.owner != "zombies":
                continue
            for polygon in province.render_polygons:
                points = [self._screen_point(point) for point in polygon]
                if len(points) < 3:
                    continue
                pygame.draw.polygon(surface, country.color, points)
                pygame.draw.polygon(surface, (49, 30, 25), points, edge_width)

    def _draw_war_fronts(self, surface, world, visible_bounds, use_provinces, scale):
        country_pairs = {
            tuple(sorted((attacker, defender)))
            for war in world.active_wars()
            for attacker in war.attackers
            for defender in war.defenders
        }
        if not country_pairs:
            return

        if use_provinces:
            regions = world.provinces_by_id
            border_segments = world.province_border_segments
        else:
            regions = world.regions_by_id
            border_segments = world.region_border_segments
        dark_width = max(4, min(7, round(scale * 0.17)))
        line_width = max(3, min(5, round(scale * 0.1)))

        cache_key = (getattr(world, "map_revision", 0), use_provinces)
        if self._war_front_cache_key != cache_key:
            front_segments = []
            if world.scenario_id == "zombie" and use_provinces:
                for province in world.provinces:
                    if province.owner != "zombies":
                        continue
                    for neighbor_id in world.province_neighbors.get(province.id, ()):
                        neighbor = regions[neighbor_id]
                        if (
                            neighbor.owner != province.owner
                            and tuple(sorted((province.owner, neighbor.owner)))
                            in country_pairs
                        ):
                            edge_id = tuple(sorted((province.id, neighbor_id)))
                            front_segments.extend(
                                border_segments.get(edge_id, ())
                            )
            else:
                for region_ids, segments in border_segments.items():
                    first = regions.get(region_ids[0])
                    second = regions.get(region_ids[1])
                    if (
                        first and second and first.owner != second.owner
                        and tuple(sorted((first.owner, second.owner))) in country_pairs
                    ):
                        front_segments.extend(segments)
            self._war_front_segments = tuple(front_segments)
            self._war_front_cache_key = cache_key

        for start, end in self._war_front_segments:
            if not self._bounds_visible(
                (
                    min(start[0], end[0]), min(start[1], end[1]),
                    max(start[0], end[0]), max(start[1], end[1]),
                ),
                visible_bounds,
            ):
                continue
            pygame.draw.line(
                surface, FRONT_DARK,
                self._screen_point(start), self._screen_point(end), dark_width,
            )
            pygame.draw.line(
                surface, FRONT_RED,
                self._screen_point(start), self._screen_point(end), line_width,
            )

    def _draw_hovered_country(self, surface, world, visible_bounds):
        country_id = self.hovered_id
        if not country_id or country_id == self.selected_id:
            return
        key = (
            self.rect.size, self.zoom, self.camera_x, self.camera_y,
            getattr(world, "map_revision", 0), country_id, self.is_dragging,
        )
        if self._hover_country_surface is None or self._hover_country_key != key:
            layer = pygame.Surface(self.rect.size, pygame.SRCALPHA)
            self._drawing_offset = self.rect.topleft
            layer.set_clip(layer.get_rect())
            detailed = self.zoom >= 1.8 and not self.is_dragging
            regions = world.detailed_regions if detailed else world.regions
            width = max(2, min(3, round(self._frame_scale * 0.09)))
            for region in regions:
                if region.owner != country_id or not self._bounds_visible(region.bounds, visible_bounds):
                    continue
                points = region.points if not detailed or self.zoom >= 10 else region.render_points
                pygame.draw.polygon(
                    layer, (215, 222, 209, 255),
                    [self._screen_point(point) for point in points], width,
                )
            layer.set_clip(None)
            self._hover_country_surface = layer
            self._hover_country_key = key
            self._drawing_offset = (0, 0)
        surface.blit(self._hover_country_surface, self.rect.topleft)

    def _draw_admin_regions(self, surface, world, visible_bounds, scale):
        width = max(1, min(2, round(scale * 0.045)))
        for region in world.visible_provinces(visible_bounds):
            country = world.countries.get(region.owner)
            if not country:
                continue
            if region.occupied:
                fill = country.color
                edge = (229, 163, 83)
                edge_width = max(2, width)
            elif region.id == self.selected_province_id:
                fill = self._lighten(country.color, 13)
                edge = GOLD
                edge_width = max(2, width)
            elif region.owner == self.selected_id:
                fill = self._lighten(country.color, 13)
                edge = self._lighten(REGION_EDGE, 28)
                edge_width = width
            else:
                fill = country.color
                edge = REGION_EDGE
                edge_width = width

            for polygon in region.render_polygons:
                points = [self._screen_point(point) for point in polygon]
                if len(points) < 3:
                    continue
                pygame.draw.polygon(surface, fill, points)
                pygame.draw.polygon(surface, edge, points, edge_width)

            if region.occupied and region.label_point:
                center = self._screen_point(region.label_point)
                local_rect = self.rect.move(-self._drawing_offset[0], -self._drawing_offset[1])
                if local_rect.collidepoint(center):
                    pygame.draw.circle(surface, (245, 198, 112), center, max(2, min(4, round(scale * 0.13))))

    def _draw_hovered_admin_region(self, surface, world):
        if self.is_dragging or self.zoom < self.province_zoom:
            return
        region = world.provinces_by_id.get(self.hovered_province_id)
        country = world.countries.get(region.owner) if region else None
        if not region or not country:
            return
        for polygon in region.render_polygons:
            points = [self._screen_point(point) for point in polygon]
            if len(points) >= 3:
                pygame.draw.polygon(surface, self._lighten(country.color, 12), points)
                pygame.draw.polygon(surface, GOLD, points, 2)

    def _draw_country_edges(self, surface, regions, visible_bounds, scale):
        width = max(1, min(2, round(scale * 0.06)))
        for region in regions:
            if not self._bounds_visible(region.bounds, visible_bounds):
                continue
            edge = GOLD if region.owner == self.selected_id else COUNTRY_EDGE
            points = region.render_points if self.zoom < 10 else region.points
            pygame.draw.polygon(surface, edge, [self._screen_point(point) for point in points], width)

    def _draw_graticule(self, surface, scale):
        if self.zoom > 1.15:
            return
        left = self.rect.left - self._drawing_offset[0]
        top = self.rect.top - self._drawing_offset[1]
        right = self.rect.right - self._drawing_offset[0]
        bottom = self.rect.bottom - self._drawing_offset[1]
        for longitude in range(-150, 180, 30):
            x, _ = self.map_point((self._longitude_to_x(longitude), 360))
            x -= self._drawing_offset[0]
            pygame.draw.line(
                surface, OCEAN_GRID, (round(x), top),
                (round(x), bottom), 1,
            )
        for latitude in range(-60, 90, 30):
            _, y = self.map_point((640, self._latitude_to_y(latitude)))
            y -= self._drawing_offset[1]
            pygame.draw.line(
                surface, OCEAN_GRID, (left, round(y)),
                (right, round(y)), 1,
            )

    def _cache_country_areas(self, world):
        if self.country_areas:
            return
        for region in world.regions:
            area = abs(sum(
                region.points[index][0] * region.points[(index + 1) % len(region.points)][1]
                - region.points[(index + 1) % len(region.points)][0] * region.points[index][1]
                for index in range(len(region.points))
            )) / 2
            self.country_areas[region.owner] = self.country_areas.get(region.owner, 0) + area

    def _draw_country_labels(self, surface, world, scale):
        self.country_label_rects = []
        labels = []
        for country_id, label in world.map_labels.items():
            if country_id not in world.countries:
                continue
            area = self.country_areas.get(country_id, 0) * scale * scale
            priority = 0 if country_id == self.selected_id else 1
            labels.append((priority, -area, country_id, label))
        labels.sort()

        minimum_area = max(420, 1800 / max(0.7, self.zoom))
        font_size = max(11, min(20, round(11 + self.zoom * 0.35)))
        font = ui_font(font_size, True)
        offset_x, offset_y = self._drawing_offset
        local_rect = self.rect.move(-offset_x, -offset_y)
        for _, negative_area, country_id, label in labels:
            if -negative_area < minimum_area and country_id != self.selected_id:
                continue
            x, y = self.map_point(label["point"])
            x -= offset_x
            y -= offset_y
            name = label["name"].upper()
            if len(name) > 22:
                name = name[:20] + "…"
            text = font.render(name, True, (239, 239, 226))
            text_rect = text.get_rect(center=(round(x), round(y)))
            padded = text_rect.inflate(12, 8)
            if not local_rect.contains(padded):
                continue
            if any(padded.colliderect(existing) for existing in self.country_label_rects):
                continue
            self.country_label_rects.append(padded)
            background = (26, 35, 42, 220)
            label_surface = pygame.Surface(padded.size, pygame.SRCALPHA)
            pygame.draw.rect(label_surface, background, label_surface.get_rect(), border_radius=4)
            border = GOLD if country_id == self.selected_id else (115, 132, 139, 180)
            pygame.draw.rect(label_surface, border, label_surface.get_rect(), 1, border_radius=4)
            surface.blit(label_surface, padded)
            surface.blit(text, text_rect)

    def _draw_map_controls(self, surface):
        zoom_label = self._small_font.render(f"{self.zoom:.1f}×", True, TEXT)
        zoom_rect = pygame.Rect(self.rect.right - 120, self.rect.y + 12, 44, 28)
        self._draw_control(surface, zoom_rect)
        surface.blit(zoom_label, zoom_label.get_rect(center=zoom_rect.center))
        for offset, label in ((70, "+"), (38, "−")):
            rect = pygame.Rect(self.rect.right - offset, self.rect.y + 12, 28, 28)
            self._draw_control(surface, rect)
            text = self._map_font.render(label, True, TEXT)
            surface.blit(text, text.get_rect(center=rect.center))

        hint = self._small_font.render(
            "КОЛЁСО: МАСШТАБ   •   ЛКМ/СКМ: ПЕРЕМЕЩЕНИЕ",
            True, (218, 223, 215),
        )
        pill = pygame.Rect(self.rect.x + 12, self.rect.bottom - 34, hint.get_width() + 22, 24)
        self._draw_control(surface, pill)
        surface.blit(hint, (pill.x + 11, pill.y + 5))

    def _draw_hover_card(self, surface, world):
        if not self.hovered_id or self.hovered_id not in world.countries:
            return
        country = world.countries[self.hovered_id]
        region = world.provinces_by_id.get(self.hovered_province_id)
        title = region.name if region else country.name
        owner = country.name if region else "Государство"
        suffix = "  •  ОККУПИРОВАНО" if region and region.occupied else ""
        font = ui_font(14, True)
        title_surface = font.render(title, True, TEXT)
        detail_surface = self._small_font.render(f"{owner}{suffix}", True, (188, 201, 202))
        width = min(max(title_surface.get_width(), detail_surface.get_width()) + 24, self.rect.width - 24)
        card = pygame.Rect(self.rect.right - width - 12, self.rect.y + 50, width, 48)
        self._draw_control(surface, card)
        surface.blit(title_surface, (card.x + 12, card.y + 7))
        surface.blit(detail_surface, (card.x + 12, card.y + 27))

    def _draw_control(self, surface, rect):
        pygame.draw.rect(surface, (23, 34, 43), rect, border_radius=5)
        pygame.draw.rect(surface, (94, 115, 124), rect, 1, border_radius=5)

    def handle_event(self, event, world):
        if event.type == pygame.MOUSEWHEEL:
            position = getattr(event, "pos", pygame.mouse.get_pos())
            if self.rect.collidepoint(position):
                self.zoom_at(position, 1.16 ** event.y)
                return None

        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            plus = pygame.Rect(self.rect.right - 70, self.rect.y + 12, 28, 28)
            minus = pygame.Rect(self.rect.right - 38, self.rect.y + 12, 28, 28)
            if event.button == 1 and plus.collidepoint(event.pos):
                self.zoom_at(plus.center, 1.25)
                return None
            if event.button == 1 and minus.collidepoint(event.pos):
                self.zoom_at(minus.center, 1 / 1.25)
                return None
            if event.button in (1, 2, 3):
                self.drag_button = event.button
                self.drag_start = event.pos
                self.drag_position = event.pos
                self.drag_moved = False
                return None

        if event.type == pygame.MOUSEMOTION:
            if self.drag_button is not None and self.drag_start:
                distance = math.hypot(
                    event.pos[0] - self.drag_start[0],
                    event.pos[1] - self.drag_start[1],
                )
                if distance > 5:
                    self.drag_moved = True
                    self.is_dragging = True
                if self.drag_moved and self.drag_position:
                    dx = event.pos[0] - self.drag_position[0]
                    dy = event.pos[1] - self.drag_position[1]
                    scale = max(0.001, self._base_scale() * self.zoom)
                    self.camera_x -= dx / scale
                    self.camera_y -= dy / scale
                    self.drag_position = event.pos
                return None
            if self.rect.collidepoint(event.pos):
                point = self.unmap_point(event.pos)
                inspect_province = (
                    self.zoom >= self.province_zoom
                    or world.scenario_id == "zombie"
                )
                region = world.get_province(point) if inspect_province else None
                if (
                    region and world.scenario_id == "zombie"
                    and self.zoom < self.province_zoom
                    and region.owner != "zombies"
                ):
                    region = None
                self.hovered_province_id = region.id if region else None
                if region:
                    self.hovered_id = region.owner
                else:
                    country_region = world.get_region(point, detailed=self.zoom >= 1.8)
                    self.hovered_id = country_region.owner if country_region else None
            else:
                self.hovered_id = None
                self.hovered_province_id = None

        if event.type == pygame.MOUSEBUTTONUP and event.button == self.drag_button:
            clicked = None
            if event.button == 1 and not self.drag_moved and self.rect.collidepoint(event.pos):
                point = self.unmap_point(event.pos)
                inspect_province = (
                    self.zoom >= self.province_zoom
                    or world.scenario_id == "zombie"
                )
                region = world.get_province(point) if inspect_province else None
                if (
                    region and world.scenario_id == "zombie"
                    and self.zoom < self.province_zoom
                    and region.owner != "zombies"
                ):
                    region = None
                self.selected_province_id = region.id if region else None
                if region:
                    clicked = region.owner
                else:
                    country_region = world.get_region(point, detailed=self.zoom >= 1.8)
                    clicked = country_region.owner if country_region else None
                if clicked:
                    self.selected_id = clicked
            self.drag_button = None
            self.drag_start = None
            self.drag_position = None
            self.drag_moved = False
            self.is_dragging = False
            return clicked
        return None

    def _screen_point(self, point):
        return (
            round(self.rect.centerx + (point[0] - self.camera_x) * self._frame_scale
                  - self._drawing_offset[0]),
            round(self.rect.centery + (point[1] - self.camera_y) * self._frame_scale
                  - self._drawing_offset[1]),
        )

    @staticmethod
    def _bounds_visible(bounds, view):
        left, top, right, bottom = bounds
        return not (right < view[0] or left > view[2] or bottom < view[1] or top > view[3])

    @staticmethod
    def _lighten(color, amount):
        return tuple(min(255, component + amount) for component in color)

    @staticmethod
    def _longitude_to_x(longitude):
        return (longitude + 180) * 1280 / 360

    @staticmethod
    def _latitude_to_y(latitude):
        return 40 + (90 - latitude) * 640 / 180
