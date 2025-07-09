import pygame
from config import WIDTH, HEIGHT, RED, FONT_PATH
import os

def load_image(name, scale=1.0):
    try:
        image = pygame.image.load(f"images/{name}.png").convert_alpha()
        if scale != 1.0:
            new_size = (int(image.get_width() * scale), int(image.get_height() * scale))
            image = pygame.transform.scale(image, new_size)
        return image
    except:
        print(f"Не удалось загрузить изображение: {name}")
        # Заглушка
        surf = pygame.Surface((50, 50), pygame.SRCALPHA)
        pygame.draw.circle(surf, RED, (25, 25), 25)
        return surf

def load_background():
    try:
        bg = pygame.image.load("images/background.jpg").convert()
        return pygame.transform.scale(bg, (WIDTH, HEIGHT))
    except:
        # Синий градиент
        bg = pygame.Surface((WIDTH, HEIGHT))
        for y in range(HEIGHT):
            color = (0, 0, 100 + int(155 * y / HEIGHT))
            pygame.draw.line(bg, color, (0, y), (WIDTH, y))
        return bg

def load_sounds():
    sounds = {}
    try:
        pygame.mixer.init()
        sounds['menu_music'] = pygame.mixer.Sound("music/start_menu.mp3")
        sounds['game_music'] = pygame.mixer.Sound("music/game1.mp3")
        sounds['slice'] = pygame.mixer.Sound("music/knife.mp3")
        sounds['explosion'] = pygame.mixer.Sound("music/explosion.wav")
        sounds['game_over'] = pygame.mixer.Sound("music/game_over.mp3")

        # Настройка громкости
        sounds['menu_music'].set_volume(0.5)
        sounds['game_music'].set_volume(0.4)
        sounds['slice'].set_volume(0.7)
        sounds['explosion'].set_volume(0.6)
        sounds['game_over'].set_volume(0.8)

        sounds['enabled'] = True
    except:
        print("Не удалось загрузить звуки.")
        sounds['enabled'] = False

    return sounds

def load_fonts():
    try:
        font = pygame.font.Font(FONT_PATH, 32)
        font_large = pygame.font.Font(FONT_PATH, 48)
    except:
        print("Не удалось загрузить шрифт. Используется стандартный.")
        font = pygame.font.SysFont("Arial", 32)
        font_large = pygame.font.SysFont("Arial", 48)
    return font, font_large

def load_all_images():
    names = [
        "item_1", "item_2", "item_3", "item_4",
        "bomb", "explosion",
        "half_item_1", "half_item_2", "half_item_3", "half_item_4",
        "red_lives", "white_lives", "knife"
    ]
    return {name: load_image(name) for name in names}
