import pygame

from config import WIDTH, HEIGHT, FPS, TITLE, SAVE_DIR
from game.world import World
from game.save_system import SaveSystem
from ui.main_menu import MainMenu
from ui.game_screen import GameScreen


def main():
    pygame.init()
    pygame.display.set_caption(TITLE)
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    clock = pygame.time.Clock()
    world = World()
    save_system = SaveSystem(SAVE_DIR)

    state = {"mode": "menu", "game": None}

    def start_game():
        state["mode"] = "game"
        state["game"] = GameScreen(screen, world)

    menu = MainMenu(screen, world, save_system, start_game)
    running = True

    while running:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)
                if state["game"]:
                    state["game"].resize(screen)
                menu.background = None
            elif state["mode"] == "menu":
                menu.handle_event(event)
            else:
                result = state["game"].handle_event(event)
                if result == "menu":
                    state["mode"] = "menu"
                    menu.mode = "menu"

        if state["mode"] == "menu":
            menu.screen = screen
            menu.draw(screen)
        else:
            state["game"].update(dt)
            state["game"].draw(screen)
            pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
