import pygame
import sys
from config import WIDTH, HEIGHT, FPS
from game import FruitNinjaGame

def main():
    pygame.init()
    pygame.display.set_caption("Veggie Slush")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    icon = pygame.image.load("images/icon.ico")  # или "icon.png"
    pygame.display.set_icon(icon)
    
    pygame.mouse.set_visible(False)

    game = FruitNinjaGame(screen)

    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            game.handle_event(event)

        game.update()
        game.draw()

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
