import pygame
from ui import theme


class Panel:
    def __init__(self, rect, title, accent=None):
        self.rect = pygame.Rect(rect)
        self.title = title
        self.accent = accent or theme.GOLD

    def draw(self, surface, font, title_font):
        theme.rounded_panel(surface, self.rect, theme.PANEL, theme.EDGE, 8)
        pygame.draw.line(
            surface, self.accent,
            (self.rect.x + 12, self.rect.y + 1),
            (self.rect.x + 54, self.rect.y + 1), 2,
        )
        title_surface = title_font.render(self.title, True, theme.TEXT)
        surface.blit(title_surface, (self.rect.x + 14, self.rect.y + 11))
        pygame.draw.line(
            surface, theme.EDGE,
            (self.rect.x + 12, self.rect.y + 38),
            (self.rect.right - 12, self.rect.y + 38), 1,
        )
