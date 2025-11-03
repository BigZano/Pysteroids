import pygame
import random
import math
from constants import SCREEN_WIDTH, SCREEN_HEIGHT


class Star:
    def __init__(self, layer):
        self.x = random.uniform(0, SCREEN_WIDTH)
        self.y = random.uniform(0, SCREEN_HEIGHT)
        self.layer = layer
        self.size = layer * 0.8
        self.alpha = int(50 + layer * 50)
        self.twinkle_offset = random.uniform(0, 2 * 3.14159)
        self.twinkle_speed = random.uniform(1.5, 3.0)

    def update(self, dt, scroll_direction):
        # Scroll based on direction (0=left, 1=down, 2=right, 3=up)
        scroll_speed = 15 * self.layer  # Faster for closer stars (parallax)
        
        if scroll_direction == 0:  # Left
            self.x -= scroll_speed * dt
            if self.x < 0:
                self.x = SCREEN_WIDTH
                self.y = random.uniform(0, SCREEN_HEIGHT)
        elif scroll_direction == 1:  # Down
            self.y += scroll_speed * dt
            if self.y > SCREEN_HEIGHT:
                self.y = 0
                self.x = random.uniform(0, SCREEN_WIDTH)
        elif scroll_direction == 2:  # Right
            self.x += scroll_speed * dt
            if self.x > SCREEN_WIDTH:
                self.x = 0
                self.y = random.uniform(0, SCREEN_HEIGHT)
        elif scroll_direction == 3:  # Up
            self.y -= scroll_speed * dt
            if self.y < 0:
                self.y = SCREEN_HEIGHT
                self.x = random.uniform(0, SCREEN_WIDTH)


class NebulaCloud:
    def __init__(self):
        self.x = random.uniform(0, SCREEN_WIDTH)
        self.y = random.uniform(0, SCREEN_HEIGHT)
        self.size = random.uniform(80, 200)
        self.color = random.choice([
            (40, 20, 60),   # Purple
            (20, 40, 60),   # Blue
            (60, 20, 40),   # Magenta
        ])
        self.alpha = random.randint(15, 35)
        self.drift_speed = random.uniform(2, 5)

    def update(self, dt, scroll_direction):
        # Drift slower than stars
        drift = self.drift_speed * dt
        
        if scroll_direction == 0:  # Left
            self.x -= drift
            if self.x < -self.size:
                self.x = SCREEN_WIDTH + self.size
                self.y = random.uniform(0, SCREEN_HEIGHT)
        elif scroll_direction == 1:  # Down
            self.y += drift
            if self.y > SCREEN_HEIGHT + self.size:
                self.y = -self.size
                self.x = random.uniform(0, SCREEN_WIDTH)
        elif scroll_direction == 2:  # Right
            self.x += drift
            if self.x > SCREEN_WIDTH + self.size:
                self.x = -self.size
                self.y = random.uniform(0, SCREEN_HEIGHT)
        elif scroll_direction == 3:  # Up
            self.y -= drift
            if self.y < -self.size:
                self.y = SCREEN_HEIGHT + self.size
                self.x = random.uniform(0, SCREEN_WIDTH)


class Background:
    def __init__(self):
        self.stars = []
        for _ in range(100):
            self.stars.append(Star(1))
        for _ in range(50):
            self.stars.append(Star(2))
        for _ in range(25):
            self.stars.append(Star(3))
        
        self.nebulae = [NebulaCloud() for _ in range(5)]
        self.time = 0
        self.scroll_direction = 0  # 0=left, 1=down, 2=right, 3=up

    def set_scroll_direction(self, lives_gained):
        """Update scroll direction based on lives gained (cycles through 4 directions)"""
        self.scroll_direction = lives_gained % 4

    def update(self, dt):
        self.time += dt
        for star in self.stars:
            star.update(dt, self.scroll_direction)
        for nebula in self.nebulae:
            nebula.update(dt, self.scroll_direction)

    def draw(self, screen):
        for nebula in self.nebulae:
            surf = pygame.Surface((int(nebula.size * 2), int(nebula.size * 2)), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*nebula.color, nebula.alpha), 
                             (int(nebula.size), int(nebula.size)), int(nebula.size))
            screen.blit(surf, (int(nebula.x - nebula.size), int(nebula.y - nebula.size)))

        for star in self.stars:
            twinkle = abs(math.sin(self.time * star.twinkle_speed + star.twinkle_offset))
            alpha = int(star.alpha * (0.3 + 0.7 * twinkle))
            color = (255, 255, 255, alpha)
            
            surf = pygame.Surface((int(star.size * 2), int(star.size * 2)), pygame.SRCALPHA)
            pygame.draw.circle(surf, color, (int(star.size), int(star.size)), star.size)
            screen.blit(surf, (int(star.x - star.size), int(star.y - star.size)))
