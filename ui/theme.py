import functools
import pygame

from ui.localization import LocalizedFont, translate


BACKGROUND = (14, 21, 29)
TOPBAR = (20, 29, 38)
PANEL = (22, 32, 41)
PANEL_ALT = (28, 40, 50)
CARD = (32, 46, 57)
CARD_HOVER = (42, 59, 69)
EDGE = (62, 81, 91)
TEXT = (231, 234, 227)
MUTED = (154, 171, 177)
GOLD = (218, 180, 103)
GREEN = (111, 164, 129)
RED = (191, 107, 100)
BLUE = (91, 145, 171)


_FONT_SCALE = 1.0


def set_scale(scale):
    global _FONT_SCALE
    value = max(0.85, min(1.4, scale))
    if value != _FONT_SCALE:
        _FONT_SCALE = value
        _cached_font.cache_clear()


@functools.lru_cache(maxsize=48)
def _cached_font(size, bold):
    family = pygame.font.match_font("segoeui") or pygame.font.match_font("arial")
    typeface = pygame.font.Font(family, size) if family else pygame.font.Font(None, size)
    typeface.set_bold(bold)
    return typeface


def font(size, bold=False):
    return LocalizedFont(_cached_font(max(9, round(size * _FONT_SCALE)), bold))


def rounded_panel(surface, rect, fill=PANEL, border=EDGE, radius=8, width=1):
    pygame.draw.rect(surface, fill, rect, border_radius=radius)
    if border:
        pygame.draw.rect(surface, border, rect, width, border_radius=radius)


def draw_flag(surface, rect, country_id, color):
    flag = pygame.Surface(rect.size)
    patterns = {
        "germany": ("h", ((25, 27, 31), (191, 62, 57), (223, 185, 90))),
        "russia": ("h", ((235, 236, 229), (79, 121, 165), (190, 75, 76))),
        "france": ("v", ((73, 111, 166), (239, 234, 215), (194, 75, 73))),
        "italy": ("v", ((82, 147, 103), (239, 234, 215), (190, 75, 76))),
        "netherlands": ("h", ((177, 69, 68), (239, 234, 215), (63, 103, 151))),
        "poland": ("h", ((239, 234, 215), (191, 63, 61), (191, 63, 61))),
        "ukraine": ("h", ((68, 122, 176), (226, 190, 87), (226, 190, 87))),
        "india": ("h", ((224, 153, 72), (239, 234, 215), (78, 134, 93))),
        "austria": ("h", ((188, 63, 65), (239, 234, 215), (188, 63, 65))),
        "hungary": ("h", ((181, 74, 69), (239, 234, 215), (83, 130, 87))),
    }
    if country_id in patterns:
        direction, colors = patterns[country_id]
        for index, stripe in enumerate(colors):
            if direction == "h":
                stripe_rect = pygame.Rect(
                    0, index * rect.height // 3, rect.width,
                    (index + 1) * rect.height // 3 - index * rect.height // 3,
                )
            else:
                stripe_rect = pygame.Rect(
                    index * rect.width // 3, 0,
                    (index + 1) * rect.width // 3 - index * rect.width // 3, rect.height,
                )
            pygame.draw.rect(flag, stripe, stripe_rect)
    else:
        pygame.draw.rect(flag, color, flag.get_rect())
        pygame.draw.rect(
            flag, (239, 234, 215),
            pygame.Rect(0, rect.height * 2 // 3, rect.width, rect.height // 3),
        )
        emblem = country_id[:3].upper()
        text = font(15, True).render(emblem, True, (242, 240, 228))
        flag.blit(text, text.get_rect(center=(rect.width // 2, rect.height // 3)))
    pygame.draw.rect(flag, (225, 228, 219), flag.get_rect(), 1)
    surface.blit(flag, rect)
    pygame.draw.rect(surface, (8, 14, 19), rect, 1)


def section_label(surface, text, position, size=11, color=GOLD):
    label = font(size, True).render(translate(text).upper(), True, color)
    surface.blit(label, position)
    return label.get_rect(topleft=position)


def fit_text(surface, text, max_width, size, color=TEXT, bold=False):
    text = translate(text)
    current_size = size
    typeface = font(current_size, bold)
    while current_size > 9 and typeface.size(text)[0] > max_width:
        current_size -= 1
        typeface = font(current_size, bold)
    return typeface.render(text, True, color)
