import pygame
import random
import math
from constants import SCREEN_WIDTH, SCREEN_HEIGHT


class Star:
    def __init__(self, layer):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.layer = layer

        # set up "further back stars", make them smaller

        self.size = 1 + (2 - layer) * 0.5
        self.brightness = 100 + (2 - layer) * 50
        self.speed = 0.1 + (2 - layer) * 0.15  # parallax effect

    def update(self, dt):
        self.y += self.speed * dt * 10

        # wrap around
        if self.y > SCREEN_HEIGHT:
            self.y = 0
            self.x = random.randint(0, SCREEN_WIDTH)
    
    def draw(self, screen):
        color = (self.brightness, self.brightness, self.brightness)
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), int(self.size))

class NebulaCloud:
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.size = random.randint(100, 300)
        self.drift_x = random.uniform(-5, 5)
        self.drift_y = random.uniform(-5, 5)

        # tuples for purples
        purple_variants = [
            (40, 20, 60),
            (50, 30, 70), 
            (60, 40, 80),
            (40, 15, 50),
        ]
        self.color = random.choice(purple_variants)
        self.alpha = random.randint(30, 45) # transparency

        self.surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self._generate_cloud()

    def _generate_cloud(self):
        center = self.size // 2
        num_blobs = random.randint(3, 6)

        for _ in range(num_blobs):
            offset_x = random.randint(-center // 2, center // 2)
            offset_y = random.randint(-center // 2, center // 2)
            radius = random.randint(self.size // 4, self.size // 2)

            color_with_alpha = (*self.color, self.alpha)
            pygame.draw.circle(self.surface, color_with_alpha, (center + offset_x, center + offset_y), radius)

    def update(self, dt):
        self.x += self.drift_x * dt
        self.y += self.drift_y * dt

        # wrap around
        if self.x < -self.size:
            self.x = SCREEN_WIDTH + self.size
        elif self.x > SCREEN_WIDTH + self.size:
            self.x = -self.size


    def draw(self, screen):
        screen.blit(self.surface, (self.x - self.size // 2, self.y - self.size // 2))

class Background:
    def __init__(self):
        self.stars = []
        self.clouds = []

        for layer in range(3):
            count = 30 - layer * 5
            for _ in range(count):
                self.stars.append(Star(layer))

        for _ in range(3):
            self.clouds.append(NebulaCloud())

    def update(self, dt):
        for star in self.stars:
            star.update(dt)
        for cloud in self.clouds:
            cloud.update(dt)

    def draw(self, screen):
        for cloud in self.clouds:
            cloud.draw(screen)
        for star in self.stars:
            star.draw(screen)
