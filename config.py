import pygame

# Размер окна
WIDTH, HEIGHT = 800, 600

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED   = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE  = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
DARK_GRAY = (50, 50, 50)

# Гравитация
GRAVITY = 0.2

# Радиус фрукта
FRUIT_RADIUS = 30

# Вероятность появления бомбы
BOMB_PROBABILITY = 0.2

# Начальный интервал появления
SPAWN_RATE_INITIAL = 60

# Путь к ресурсам
FONT_PATH = "resources/Monoton-Regular.ttf"
HIGHSCORE_FILE = "resources/highscore.json"

# Состояния игры
MENU = 0
PLAYING = 1
GAME_OVER = 2

# Максимальное количество жизней
MAX_LIVES = 3

# FPS
FPS = 60
