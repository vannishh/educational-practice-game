import pygame
import random
import math
from config import WIDTH, HEIGHT, GRAVITY, WHITE

class SwordTrail:
    def __init__(self):
        self.points = []
        self.max_length = 7
        self.max_width = 7

    def add_point(self, pos):
        self.points.append(pos)
        if len(self.points) > self.max_length:
            self.points.pop(0)

    def draw(self, surface):
        if len(self.points) < 2:
            return
        for i in range(len(self.points) - 1):
            progress = i / (len(self.points) - 1)
            width = max(1, int(self.max_width * progress))
            start, end = self.points[i], self.points[i+1]

            dx, dy = end[0] - start[0], end[1] - start[1]
            length = math.hypot(dx, dy)
            if length == 0:
                continue
            dx, dy = dx / length, dy / length
            perp_x, perp_y = -dy * width / 2, dx * width / 2

            polygon = [
                (start[0] - perp_x, start[1] - perp_y),
                (start[0] + perp_x, start[1] + perp_y),
                (end[0] + perp_x, end[1] + perp_y),
                (end[0] - perp_x, end[1] - perp_y),
            ]
            pygame.draw.polygon(surface, WHITE, polygon)
        pygame.draw.circle(surface, WHITE, self.points[-1], self.max_width // 2)

class Fruit:
    def __init__(self, images):
        self.x = random.randint(50, WIDTH - 50)
        self.y = HEIGHT + 50
        self.type = random.choice(["item_1", "item_2", "item_3", "item_4"])
        self.image = images[self.type]
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.speed_y = random.uniform(-15, -10)
        self.speed_x = random.uniform(-3, 3)
        self.sliced = False
        self.slice_time = 0
        self.sliced_image = images[f"half_{self.type}"]
        self.sliced_pieces = []

    def update(self):
        if not self.sliced:
            self.speed_y += GRAVITY
            self.y += self.speed_y
            self.x += self.speed_x
            self.rect.center = (self.x, self.y)
            if self.x < 50 or self.x > WIDTH - 50:
                self.speed_x *= -0.8
        else:
            for piece in self.sliced_pieces[:]:
                piece['speed_y'] += GRAVITY
                piece['x'] += piece['speed_x']
                piece['y'] += piece['speed_y']
                piece['rotation'] += piece['rotation_speed']
                if piece['y'] > HEIGHT + 100:
                    self.sliced_pieces.remove(piece)

    def slice(self):
        self.sliced = True
        self.slice_time = pygame.time.get_ticks()
        self.sliced_pieces = [
            {
                'x': self.x,
                'y': self.y,
                'speed_x': random.uniform(-5, -2),
                'speed_y': random.uniform(-2, 1),
                'image': self.sliced_image,
                'rotation': 0,
                'rotation_speed': random.uniform(-5, 5)
            },
            {
                'x': self.x,
                'y': self.y,
                'speed_x': random.uniform(2, 5),
                'speed_y': random.uniform(-2, 1),
                'image': pygame.transform.flip(self.sliced_image, True, False),
                'rotation': 0,
                'rotation_speed': random.uniform(-5, 5)
            }
        ]

    def draw(self, screen):
        if not self.sliced:
            screen.blit(self.image, self.rect)
        else:
            for piece in self.sliced_pieces:
                rotated = pygame.transform.rotate(piece['image'], piece['rotation'])
                rect = rotated.get_rect(center=(piece['x'], piece['y']))
                screen.blit(rotated, rect)

    def is_off_screen(self):
        return (not self.sliced and self.y > HEIGHT + 100) or (self.sliced and not self.sliced_pieces)

    def is_sliced(self, pos1, pos2):
        if self.sliced:
            return False  # 🍉 Уже разрезан, игнорируем
        return _check_slice(self.x, self.y, self.rect, pos1, pos2)

class Bomb:
    def __init__(self, images):
        self.x = random.randint(50, WIDTH - 50)
        self.y = HEIGHT + 50
        self.image = images["bomb"]
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.speed_y = random.uniform(-12, -8)
        self.speed_x = random.uniform(-2, 2)
        self.sliced = False
        self.slice_time = 0
        self.explosion_image = images["explosion"]

    def update(self):
        self.speed_y += GRAVITY
        self.y += self.speed_y
        self.x += self.speed_x
        self.rect.center = (self.x, self.y)
        if self.x < 50 or self.x > WIDTH - 50:
            self.speed_x *= -0.7

    def draw(self, screen):
        if not self.sliced:
            screen.blit(self.image, self.rect)
        else:
            rect = self.explosion_image.get_rect(center=(self.x, self.y))
            screen.blit(self.explosion_image, rect)

    def is_off_screen(self):
        return self.y > HEIGHT + 100

    def is_sliced(self, pos1, pos2):
        if self.sliced:
            return False  # 🍉 Уже разрезан, игнорируем
        return _check_slice(self.x, self.y, self.rect, pos1, pos2)

def _check_slice(x, y, rect, pos1, pos2):
    center = pygame.math.Vector2(x, y)
    line_start = pygame.math.Vector2(pos1)
    line_end = pygame.math.Vector2(pos2)
    line_vec = line_end - line_start
    line_length = line_vec.length()
    if line_length == 0:
        return False
    line_unit = line_vec.normalize()
    to_center = center - line_start
    projection = max(0, min(line_length, to_center.dot(line_unit)))
    closest = line_start + line_unit * projection
    distance = (center - closest).length()
    max_distance = max(rect.width, rect.height) * 0.7
    return distance < max_distance and (0 <= projection <= line_length)
