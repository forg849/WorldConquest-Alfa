import pygame

from ui import theme


class Button:
    def __init__(self, rect, text, callback=None, color=None, text_color=None):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.callback = callback
        self.color = color or theme.CARD
        self.text_color = text_color or theme.TEXT
        self.hovered = False
        self.enabled = True

    def handle_event(self, event):
        if not self.enabled:
            return False
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.callback:
                    self.callback()
                return True
        return False

    def draw(self, surface, font):
        self.hovered = self.rect.collidepoint(pygame.mouse.get_pos()) if self.enabled else False
        if self.enabled:
            color = tuple(min(255, channel + (10 if self.hovered else 0)) for channel in self.color)
            border = theme.GOLD if self.hovered else theme.EDGE
            text_color = self.text_color
        else:
            color = (34, 43, 50)
            border = (48, 61, 68)
            text_color = (116, 130, 135)
        pygame.draw.rect(surface, color, self.rect, border_radius=6)
        pygame.draw.rect(surface, border, self.rect, 1, border_radius=6)
        if self.hovered and self.rect.height >= 28:
            pygame.draw.line(
                surface, (231, 207, 151),
                (self.rect.x + 8, self.rect.y + 2),
                (self.rect.right - 8, self.rect.y + 2), 1,
            )
        label = font.render(self.text, True, text_color)
        if label.get_width() > self.rect.width - 12:
            label = theme.fit_text(
                surface, self.text, self.rect.width - 12,
                font.get_height(), text_color,
            )
        surface.blit(label, label.get_rect(center=self.rect.center))
