import pygame
import sys
import random
import math
import os
import json


def load_high_score():
    try:
        if os.path.exists("highscore.json"):
            with open("highscore.json", "r") as file:
                data = json.load(file)
                return data.get("high_score", 0)
        return 0
    except:
        return 0

def save_high_score(score):
    try:
        with open("highscore.json", "w") as file:
            json.dump({"high_score": score}, file)
    except:
        print("Не удалось сохранить рекорд")

# Загружаем рекорд при старте игры
high_score = load_high_score()
new_record_achieved = False

# Initialize pygame
pygame.mixer.init()
pygame.mixer.fadeout(500)
pygame.init()

try:
    # Музыка
    menu_music = pygame.mixer.Sound("music/start_menu.mp3")  # Замените на ваш файл
    game_music = pygame.mixer.Sound("music/game1.mp3")  # Замените на ваш файл
    
    # Звуковые эффекты
    slice_sound = pygame.mixer.Sound("music/knife.mp3")  # Звук разрезания
    bomb_explosion = pygame.mixer.Sound("music/explosion.wav")  # Звук взрыва бомбы
    game_over_sound = pygame.mixer.Sound("music/game_over.mp3")  # Звук проигрыша
    
    # Настройка громкости
    menu_music.set_volume(0.5)
    game_music.set_volume(0.4)
    slice_sound.set_volume(0.7)
    bomb_explosion.set_volume(0.6)
    game_over_sound.set_volume(0.8)
    
    sound_enabled = True
except:
    print("Не удалось загрузить звуки. Игра продолжит работу без звука.")
    sound_enabled = False

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fruit Ninja")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
DARK_GRAY = (50, 50, 50)

# Game states
MENU = 0
PLAYING = 1
GAME_OVER = 2

# Game variables
game_state = MENU
score = 0
lives = 3
font = pygame.font.SysFont('Arial', 32)
clock = pygame.time.Clock()

# Objects
fruits = []
bombs = []
fruit_colors = [RED, GREEN, BLUE, YELLOW, ORANGE]
fruit_radius = 30
spawn_rate = 60  # frames
spawn_timer = 0
bomb_probability = 0.2  # 20% chance to spawn bomb

# Physics
GRAVITY = 0.2

class SwordTrail:
    def __init__(self):
        self.points = []
        self.max_length = 7 # Количество точек в следе
        self.max_width = 7   # Максимальная толщина у курсора
        
    def add_point(self, pos):
        self.points.append(pos)
        if len(self.points) > self.max_length:
            self.points.pop(0)
            
    def draw(self, surface):
        if len(self.points) < 2:
            return
            
        # Рисуем след, который утолщается к курсору
        for i in range(len(self.points)-1):
            # Процент завершенности следа (0 = начало, 1 = конец у курсора)
            progress = i / (len(self.points)-1)
            
            # Толщина увеличивается к курсору
            width = int(self.max_width * progress)
            if width < 1:
                width = 1
                
            start_pos = self.points[i]
            end_pos = self.points[i+1]
            
            # Вычисляем перпендикуляр к направлению линии
            dx = end_pos[0] - start_pos[0]
            dy = end_pos[1] - start_pos[1]
            length = math.hypot(dx, dy)
            
            if length == 0:
                continue
                
            # Нормализуем вектор направления
            dx /= length
            dy /= length
            
            # Перпендикулярный вектор для толщины
            perp_x = -dy * width/2
            perp_y = dx * width/2
            
            # Создаем полигон для сегмента линии
            polygon = [
                (start_pos[0] - perp_x, start_pos[1] - perp_y),
                (start_pos[0] + perp_x, start_pos[1] + perp_y),
                (end_pos[0] + perp_x, end_pos[1] + perp_y),
                (end_pos[0] - perp_x, end_pos[1] - perp_y)
            ]
            
            pygame.draw.polygon(surface, WHITE, polygon)
        
        # Рисуем яркое пятно под курсором
        if len(self.points) > 0:
            pygame.draw.circle(surface, WHITE, (int(self.points[-1][0]), int(self.points[-1][1])), self.max_width//2)

sword_trail = SwordTrail()

def load_image(name, scale=1.0):
    try:
        image = pygame.image.load(f"images/{name}.png").convert_alpha()
        if scale != 1.0:
            new_size = (int(image.get_width() * scale), int(image.get_height() * scale))
            image = pygame.transform.scale(image, new_size)
        return image
    except:
        print(f"Не удалось загрузить изображение: {name}")
        # Создаем заглушку если изображение не найдено
        surf = pygame.Surface((50, 50), pygame.SRCALPHA)
        pygame.draw.circle(surf, RED, (25, 25), 25)
        return surf


# Загрузка всех изображений
images = {
    "guava": load_image("guava"),
    "melon": load_image("melon"),
    "orange": load_image("orange"),
    "pomegranate": load_image("pomegranate"),
    "bomb": load_image("bomb"),
    "explosion": load_image("explosion"),
    "half_guava": load_image("half_guava"),
    "half_melon": load_image("half_melon"),
    "half_orange": load_image("half_orange"),
    "half_pomegranate": load_image("half_pomegranate"),
    "red_lives": load_image("red_lives"),
    "white_lives": load_image("white_lives")
}

class Fruit:
    def __init__(self):
        self.x = random.randint(50, WIDTH - 50)
        self.y = HEIGHT + 50
        self.type = random.choice(["guava", "melon", "pomegranate"])
        self.image = images[self.type]
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.speed_y = random.uniform(-15, -10)
        self.speed_x = random.uniform(-3, 3)
        self.sliced = False
        self.slice_time = 0
        self.sliced_image = images[f"half_{self.type}"]
        self.left_half = None
        self.right_half = None
        self.sliced_pieces = []  # Храним половинки фруктов
        
    def update(self):
        if not self.sliced:
            # Обычное движение целого фрукта
            self.speed_y += GRAVITY
            self.y += self.speed_y
            self.x += self.speed_x
            self.rect.center = (self.x, self.y)
            
            if self.x < 50:
                self.x = 50
                self.speed_x *= -0.8
            elif self.x > WIDTH - 50:
                self.x = WIDTH - 50
                self.speed_x *= -0.8
        else:
            # Обновляем положение половинок
            for piece in self.sliced_pieces[:]:  # Используем копию списка для безопасного удаления
                piece['speed_y'] += GRAVITY
                piece['x'] += piece['speed_x']
                piece['y'] += piece['speed_y']
                piece['rotation'] += piece['rotation_speed']
                
                # Удаляем половинки, которые ушли за нижнюю границу
                if piece['y'] > HEIGHT + 100:
                    self.sliced_pieces.remove(piece)
    def slice(self):
        self.sliced = True
        self.slice_time = pygame.time.get_ticks()
        
        # Создаем две половинки с разной физикой
        self.sliced_pieces = [
            {
                'x': self.x,
                'y': self.y,
                'speed_x': random.uniform(-5, -2),  # Левая половинка летит влево
                'speed_y': random.uniform(-2, 1),  # Немного вверх
                'image': self.sliced_image,
                'rotation': 0,
                'rotation_speed': random.uniform(-5, 5)
            },
            {
                'x': self.x,
                'y': self.y,
                'speed_x': random.uniform(2, 5),  # Левая половинка летит влево
                'speed_y': random.uniform(-2, 1),  # Немного вверх
                'image': pygame.transform.flip(self.sliced_image, True, False),
                'rotation': 0,
                'rotation_speed': random.uniform(-5, 5)
            }
        ]
            
    def draw(self):
        if not self.sliced:
            screen.blit(self.image, self.rect)
        else:
            # Рисуем все половинки
            for piece in self.sliced_pieces:
                rotated_img = pygame.transform.rotate(piece['image'], piece['rotation'])
                new_rect = rotated_img.get_rect(center=(piece['x'], piece['y']))
                screen.blit(rotated_img, new_rect)
            
    def is_off_screen(self):
        if not self.sliced:
            return self.y > HEIGHT + 100
        else:
            # Фрукт считается ушедшим, когда все половинки провалились за экран
            return len(self.sliced_pieces) == 0
        
    def is_sliced(self, pos1, pos2):
        if self.sliced:
            return False
            
        # Проверяем расстояние до центра фрукта
        fruit_pos = pygame.math.Vector2(self.x, self.y)
        line_start = pygame.math.Vector2(pos1)
        line_end = pygame.math.Vector2(pos2)
        
        # Максимальное расстояние для разрезания (чуть больше радиуса)
        max_cut_distance = max(self.rect.width, self.rect.height) * 0.7
        
        # Проверяем расстояние от центра до линии
        line_vec = line_end - line_start
        line_length = line_vec.length()
        if line_length == 0:
            return False
            
        line_unit = line_vec.normalize()
        to_center = fruit_pos - line_start
        projection = to_center.dot(line_unit)
        projection = max(0, min(line_length, projection))
        closest_point = line_start + line_unit * projection
        distance = (fruit_pos - closest_point).length()
        
        # Дополнительная проверка - точка должна быть между началом и концом линии
        is_between = (0 <= projection <= line_length)
        
        return distance < max_cut_distance and is_between

class Bomb:
    def __init__(self):
        self.x = random.randint(50, WIDTH - 50)
        self.y = HEIGHT + 50
        self.image = images["bomb"]
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.speed_y = random.uniform(-12, -8)
        self.speed_x = random.uniform(-2, 2)
        self.sliced = False
        self.slice_time = 0
        
    def update(self):
        self.speed_y += GRAVITY
        self.y += self.speed_y
        self.x += self.speed_x
        self.rect.center = (self.x, self.y)
        
        if self.x < 50:
            self.x = 50
            self.speed_x *= -0.7
        elif self.x > WIDTH - 50:
            self.x = WIDTH - 50
            self.speed_x *= -0.7
            
    def draw(self):
        if not self.sliced:
            screen.blit(self.image, self.rect)
        else:
            # Анимация взрыва
            explosion_img = images["explosion"]
            screen.blit(explosion_img, 
                       (self.x - explosion_img.get_width()//2, 
                        self.y - explosion_img.get_height()//2))
            
    def is_off_screen(self):
        return self.y > HEIGHT + 100
        
    def is_sliced(self, pos1, pos2):
        if self.sliced:
            return False
            
        # Аналогичная проверка как для фруктов
        bomb_pos = pygame.math.Vector2(self.x, self.y)
        line_start = pygame.math.Vector2(pos1)
        line_end = pygame.math.Vector2(pos2)
        
        max_cut_distance = max(self.rect.width, self.rect.height) * 0.7
        
        line_vec = line_end - line_start
        line_length = line_vec.length()
        if line_length == 0:
            return False
            
        line_unit = line_vec.normalize()
        to_center = bomb_pos - line_start
        projection = to_center.dot(line_unit)
        projection = max(0, min(line_length, projection))
        closest_point = line_start + line_unit * projection
        distance = (bomb_pos - closest_point).length()
        
        is_between = (0 <= projection <= line_length)
        
        return distance < max_cut_distance and is_between

def draw_main_menu():
    screen.fill(BLACK)
    title = font.render("FRUIT NINJA", True, WHITE)
    start_text = font.render("Press SPACE to Start", True, WHITE)
    high_score_text = font.render(f"High Score: {high_score}", True, (200, 200, 0))
    
    screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//3))
    screen.blit(start_text, (WIDTH//2 - start_text.get_width()//2, HEIGHT//2))
    screen.blit(high_score_text, (WIDTH//2 - high_score_text.get_width()//2, HEIGHT//2 + 50))

    
def draw_game():
    screen.fill(BLACK)
    score_text = font.render(f"Score: {score}", True, WHITE)
    lives_text = font.render(f"Lives: {lives}", True, WHITE)
    high_score_text = font.render(f"High Score: {high_score}", True, (200, 200, 0))
    
    screen.blit(score_text, (20, 20))
    screen.blit(lives_text, (WIDTH - lives_text.get_width() - 20, 20))
    screen.blit(high_score_text, (WIDTH//2 - high_score_text.get_width()//2, 20))
    
    for fruit in fruits:
        fruit.draw()
    for bomb in bombs:
        bomb.draw()
    sword_trail.draw(screen)
    
def draw_game_over():
    screen.fill(BLACK)
    game_over_text = font.render("GAME OVER", True, RED)
    score_text = font.render(f"Your Score: {score}", True, WHITE)
    high_score_text = font.render(f"High Score: {high_score}", True, (200, 200, 0))
    restart_text = font.render("Press SPACE to Play Again", True, WHITE)
    
    screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//3))
    screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2))
    screen.blit(high_score_text, (WIDTH//2 - high_score_text.get_width()//2, HEIGHT//2 + 50))
    screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT*2//3))
    
    if new_record_achieved:
        record_text = font_large.render("NEW RECORD!", True, (0, 255, 0))
        screen.blit(record_text, (WIDTH//2 - record_text.get_width()//2, HEIGHT//2 + 100))

def reset_game():
    global score, lives, fruits, bombs, new_record_achieved
    score = 0
    lives = 3
    fruits = []
    bombs = []
    new_record_achieved = False
    if sound_enabled:
        pygame.mixer.stop()


font_large = pygame.font.SysFont('Arial', 48)  # Для надписи NEW RECORD!
# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if game_state == MENU:
                    game_state = PLAYING
                    reset_game()
                    if sound_enabled:
                        menu_music.stop()
                        game_music.play(-1)  # -1 означает зацикливание
                elif game_state == GAME_OVER:
                    game_state = PLAYING
                    reset_game()
                    if sound_enabled:
                        game_music.play(-1)
    
    if game_state == PLAYING:
        current_pos = pygame.mouse.get_pos()
        if len(sword_trail.points) > 0:
            last_pos = sword_trail.points[-1]
            if math.sqrt((current_pos[0]-last_pos[0])**2 + (current_pos[1]-last_pos[1])**2) > 5:
                sword_trail.add_point(current_pos)
                
                # Check fruit slices
                for fruit in fruits[:]:
                    if fruit.is_sliced(last_pos, current_pos) and not fruit.sliced:
                        fruit.slice()  # Вместо fruit.sliced = True
                        score += 1
                        if sound_enabled:
                            slice_sound.play()
                
                # Check bomb slices
                for bomb in bombs[:]:
                    if bomb.is_sliced(last_pos, current_pos) and not bomb.sliced:
                        bomb.sliced = True
                        bomb.slice_time = pygame.time.get_ticks()
                        lives -= 1
                        if sound_enabled:
                            bomb_explosion.play()
                        if lives <= 0:
                            game_state = GAME_OVER
                            if score > high_score:
                                high_score = score
                                new_record_achieved = True
                                save_high_score(high_score)
                            if sound_enabled:
                                game_music.stop()
                                game_over_sound.play()
        else:
            sword_trail.add_point(current_pos)

    if game_state == PLAYING:
        spawn_timer += 1
        if spawn_timer >= spawn_rate:
            if random.random() < bomb_probability:
                bombs.append(Bomb())
            else:
                fruits.append(Fruit())
            spawn_timer = 0
            spawn_rate = max(20, spawn_rate - 1)
        
        # Update fruits
        for fruit in fruits[:]:
            fruit.update()
            if fruit.is_off_screen():
                if not fruit.sliced:  # Если целый фрукт ушел за экран
                    lives -= 1
                    if lives <= 0:
                        game_state = GAME_OVER
                        if score > high_score:
                            high_score = score
                            new_record_achieved = True
                            save_high_score(high_score)
                        if sound_enabled:
                            game_music.stop()
                            game_over_sound.play()
                fruits.remove(fruit)
        
        # Update bombs
        for bomb in bombs[:]:
            bomb.update()
            if bomb.is_off_screen():
                bombs.remove(bomb)
            elif bomb.sliced and pygame.time.get_ticks() - bomb.slice_time > 500:
                bombs.remove(bomb)
    
    if game_state == MENU:
        draw_main_menu()
    elif game_state == PLAYING:
        draw_game()
    elif game_state == GAME_OVER:
        draw_game_over()
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()