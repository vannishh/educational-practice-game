import pygame
import sys
import random
import math

# Initialize pygame
pygame.mixer.init()
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

class Fruit:
    def __init__(self):
        self.x = random.randint(fruit_radius, WIDTH - fruit_radius)
        self.y = HEIGHT + fruit_radius
        self.color = random.choice(fruit_colors)
        self.radius = fruit_radius
        self.speed_y = random.uniform(-15, -10)
        self.speed_x = random.uniform(-3, 3)
        self.sliced = False
        self.slice_time = 0
        
    def update(self):
        self.speed_y += GRAVITY
        self.y += self.speed_y
        self.x += self.speed_x
        
        if self.x - self.radius < 0:
            self.x = self.radius
            self.speed_x *= -0.8
            
        if self.x + self.radius > WIDTH:
            self.x = WIDTH - self.radius
            self.speed_x *= -0.8
            
    def draw(self):
        if not self.sliced:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
            pygame.draw.circle(screen, WHITE, (int(self.x - self.radius/3), int(self.y - self.radius/3)), self.radius//4)
        else:
            pygame.draw.circle(screen, self.color, (int(self.x - 10), int(self.y)), self.radius//2)
            pygame.draw.circle(screen, self.color, (int(self.x + 10), int(self.y)), self.radius//2)
            
    def is_off_screen(self):
        return self.y > HEIGHT + self.radius
        
    def is_sliced(self, pos1, pos2):
        if self.sliced:
            return False
            
        x1, y1 = pos1
        x2, y2 = pos2
        dx = self.x - x1
        dy = self.y - y1
        lx = x2 - x1
        ly = y2 - y1
        dot = dx * lx + dy * ly
        len_sq = lx * lx + ly * ly
        
        if len_sq != 0:
            param = dot / len_sq
        else:
            param = -1
            
        if param < 0:
            xx = x1
            yy = y1
        elif param > 1:
            xx = x2
            yy = y2
        else:
            xx = x1 + param * lx
            yy = y1 + param * ly
            
        dist = math.sqrt((self.x - xx)**2 + (self.y - yy)**2)
        return dist <= self.radius

class Bomb:
    def __init__(self):
        self.x = random.randint(fruit_radius, WIDTH - fruit_radius)
        self.y = HEIGHT + fruit_radius
        self.radius = fruit_radius
        self.speed_y = random.uniform(-15, -10)
        self.speed_x = random.uniform(-3, 3)
        self.sliced = False
        self.slice_time = 0
        
    def update(self):
        self.speed_y += GRAVITY
        self.y += self.speed_y
        self.x += self.speed_x
        
        if self.x - self.radius < 0:
            self.x = self.radius
            self.speed_x *= -0.8
            
        if self.x + self.radius > WIDTH:
            self.x = WIDTH - self.radius
            self.speed_x *= -0.8
            
    def draw(self):
        if not self.sliced:
            pygame.draw.circle(screen, DARK_GRAY, (int(self.x), int(self.y)), self.radius)
            pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), self.radius//2)
            # Фитиль
            pygame.draw.line(screen, ORANGE, (self.x, self.y - self.radius), 
                            (self.x, self.y - self.radius - 10), 2)
        else:
            # Взрыв
            pygame.draw.circle(screen, ORANGE, (int(self.x), int(self.y)), self.radius + 10)
            pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), self.radius + 5)
            
    def is_off_screen(self):
        return self.y > HEIGHT + self.radius
        
    def is_sliced(self, pos1, pos2):
        if self.sliced:
            return False
            
        x1, y1 = pos1
        x2, y2 = pos2
        dx = self.x - x1
        dy = self.y - y1
        lx = x2 - x1
        ly = y2 - y1
        dot = dx * lx + dy * ly
        len_sq = lx * lx + ly * ly
        
        if len_sq != 0:
            param = dot / len_sq
        else:
            param = -1
            
        if param < 0:
            xx = x1
            yy = y1
        elif param > 1:
            xx = x2
            yy = y2
        else:
            xx = x1 + param * lx
            yy = y1 + param * ly
            
        dist = math.sqrt((self.x - xx)**2 + (self.y - yy)**2)
        return dist <= self.radius

def draw_main_menu():
    if sound_enabled and game_state == MENU:
        if not pygame.mixer.get_busy():  # Если музыка не играет
            menu_music.play(-1)
    screen.fill(BLACK)
    title = font.render("FRUIT NINJA", True, WHITE)
    start_text = font.render("Press SPACE to Start", True, WHITE)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//3))
    screen.blit(start_text, (WIDTH//2 - start_text.get_width()//2, HEIGHT//2))
    
def draw_game():
    screen.fill(BLACK)
    score_text = font.render(f"Score: {score}", True, WHITE)
    lives_text = font.render(f"Lives: {lives}", True, WHITE)
    screen.blit(score_text, (20, 20))
    screen.blit(lives_text, (WIDTH - lives_text.get_width() - 20, 20))
    
    for fruit in fruits:
        fruit.draw()
    
    for bomb in bombs:
        bomb.draw()
    
    sword_trail.draw(screen)
    
def draw_game_over():
    screen.fill(BLACK)
    game_over_text = font.render("GAME OVER", True, RED)
    final_score = font.render(f"Final Score: {score}", True, WHITE)
    restart_text = font.render("Press SPACE to Play Again", True, WHITE)
    
    screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//3))
    screen.blit(final_score, (WIDTH//2 - final_score.get_width()//2, HEIGHT//2))
    screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT*2//3))

    pass

def reset_game():
    global score, lives, fruits, bombs
    score = 0
    lives = 3
    fruits = []
    bombs = []
    if sound_enabled:
        pygame.mixer.stop()

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
                    if fruit.is_sliced(last_pos, current_pos):
                        fruit.sliced = True
                        fruit.slice_time = pygame.time.get_ticks()
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
                if not fruit.sliced:
                    lives -= 1
                    if lives <= 0:
                        game_state = GAME_OVER
                fruits.remove(fruit)
            elif fruit.sliced and pygame.time.get_ticks() - fruit.slice_time > 500:
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