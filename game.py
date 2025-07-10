import pygame
import math
import random

from config import *
from utils import load_high_score, save_high_score
from assets import (
    load_fonts, load_background, load_sounds, load_all_images
)
from objects import Fruit, Bomb, SwordTrail

class FruitNinjaGame:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.font, self.font_large = load_fonts()
        self.images = load_all_images()
        self.background = load_background()
        self.sounds = load_sounds()
        self.knife_img = self.images.get("knife", pygame.Surface((0, 0)))
        self.knife_img = pygame.transform.scale(self.knife_img, (50, 50))
        self.knife_rect = self.knife_img.get_rect()
        self.reset()

    def reset(self):
        self.state = MENU
        self.score = 0
        self.lives = MAX_LIVES
        self.spawn_rate = SPAWN_RATE_INITIAL
        self.spawn_timer = 0
        self.fruits = []
        self.bombs = []
        self.trail = SwordTrail()
        self.high_score = load_high_score()
        self.new_record = False
        if self.sounds['enabled']:
            pygame.mixer.stop()

    def start_game(self):
        self.state = PLAYING
        self.score = 0
        self.lives = MAX_LIVES
        self.fruits.clear()
        self.bombs.clear()
        self.spawn_timer = 0
        self.spawn_rate = SPAWN_RATE_INITIAL
        self.new_record = False
        if self.sounds['enabled']:
            self.sounds['menu_music'].stop()
            self.sounds['game_music'].play(-1)

    def update(self):
        if self.state == PLAYING:
            self._update_playing()

    def draw(self):
        if self.state == MENU:
            self._draw_menu()
        elif self.state == PLAYING:
            self._draw_game()
        elif self.state == GAME_OVER:
            self._draw_game_over()

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if self.state == MENU:
                self.start_game()
            elif self.state == GAME_OVER:
                self.start_game()

    def _update_playing(self):
        pos = pygame.mouse.get_pos()
        if self.trail.points:
            last_pos = self.trail.points[-1]
            dist = math.hypot(pos[0] - last_pos[0], pos[1] - last_pos[1])
            if dist > 5:
                self.trail.add_point(pos)
                self._check_collisions(last_pos, pos)
        else:
            self.trail.add_point(pos)

        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_rate:
            if random.random() < BOMB_PROBABILITY:
                self.bombs.append(Bomb(self.images))
            else:
                self.fruits.append(Fruit(self.images))
            self.spawn_timer = 0
            self.spawn_rate = max(20, self.spawn_rate - 1)

        for fruit in self.fruits[:]:
            fruit.update()
            if fruit.is_off_screen():
                if not fruit.sliced:
                    self.lives -= 1
                    if self.lives <= 0:
                        self._game_over()
                self.fruits.remove(fruit)

        for bomb in self.bombs[:]:
            bomb.update()
            if bomb.is_off_screen():
                self.bombs.remove(bomb)
            elif bomb.sliced and pygame.time.get_ticks() - bomb.slice_time > 500:
                self.bombs.remove(bomb)

    def _check_collisions(self, last_pos, pos):
        for fruit in self.fruits[:]:
            if fruit.is_sliced(last_pos, pos):
                fruit.slice()
                self.score += 1
                if self.sounds['enabled']:
                    self.sounds['slice'].play()

        for bomb in self.bombs[:]:
            if bomb.is_sliced(last_pos, pos):
                bomb.sliced = True
                bomb.slice_time = pygame.time.get_ticks()
                self.lives -= 1
                if self.sounds['enabled']:
                    self.sounds['explosion'].play()
                if self.lives <= 0:
                    self._game_over()

    def _game_over(self):
        self.state = GAME_OVER
        if self.score > self.high_score:
            self.high_score = self.score
            self.new_record = True
            save_high_score(self.high_score)
        if self.sounds['enabled']:
            self.sounds['game_music'].stop()
            self.sounds['game_over'].play()

    def _draw_menu(self):
        self.screen.blit(self.background, (0, 0))
        logo_img = pygame.image.load("images/title.png").convert_alpha()
        logo_img = pygame.transform.scale(logo_img, (500, 500))
    
        logo_rect = logo_img.get_rect(center=(WIDTH//2, HEIGHT//3))
        self.screen.blit(logo_img, logo_rect)
    
    # Остальные элементы меню
        prompt = self.font.render("Press SPACE to Start", True, WHITE)
        hi_score = self.font.render(f"High Score: {self.high_score}", True, (75, 218, 246))
        self.screen.blit(hi_score, (WIDTH//2 - hi_score.get_width()//2, HEIGHT//2 + 20))
        self.screen.blit(prompt, (WIDTH//2 - prompt.get_width()//2, HEIGHT - 80))
    
        if self.sounds['enabled']:
            self.sounds['menu_music'].play(-1)

    def _draw_game(self):
        self.screen.blit(self.background, (0, 0))
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        hi_text = self.font.render(f"High Score: {self.high_score}", True, (200, 200, 0))
        self.screen.blit(score_text, (20, 20))
        self.screen.blit(hi_text, (WIDTH // 2 - hi_text.get_width() // 2, 20))

        heart_img_w = self.images["red_lives"].get_width()
        for i in range(MAX_LIVES):
            img = self.images["red_lives"] if i < self.lives else self.images["white_lives"]
            self.screen.blit(img, (WIDTH - 30 - (MAX_LIVES - i) * (heart_img_w + 5), 20))

        for fruit in self.fruits:
            fruit.draw(self.screen)
        for bomb in self.bombs:
            bomb.draw(self.screen)
        self.trail.draw(self.screen)

        # Нож
        knife_rect = self.knife_img.get_rect(center=pygame.mouse.get_pos())
        self.screen.blit(self.knife_img, knife_rect)

    def _draw_game_over(self):
        self.screen.blit(self.background, (0, 0))
        game_over = self.font_large.render("GAME OVER", True, RED)
        logo_img = pygame.image.load("images/game_over.png").convert_alpha()
        logo_img = pygame.transform.scale(logo_img, (150, 150))
    
        logo_rect = logo_img.get_rect(center=(WIDTH//2, HEIGHT//4-50))
        self.screen.blit(logo_img, logo_rect)
        score_text = self.font.render(f"Your Score: {self.score}", True, WHITE)
        hi_score = self.font.render(f"High Score: {self.high_score}", True, (200, 200, 0))
        prompt = self.font.render("Press SPACE to Play Again", True, WHITE)

        self.screen.blit(game_over, (WIDTH // 2 - game_over.get_width() // 2, HEIGHT // 3))
        self.screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2))
        self.screen.blit(hi_score, (WIDTH // 2 - hi_score.get_width() // 2, HEIGHT // 2 + 50))
        self.screen.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, HEIGHT-80))
        if self.new_record:
            record = self.font_large.render("NEW RECORD!", True, (0, 255, 0))
            self.screen.blit(record, (WIDTH // 2 - record.get_width() // 2, HEIGHT // 2 + 150))
