import random
import math
import pygame
from constants import *

class PowerUp(pygame.sprite.Sprite):
    containers = () # set in main.py
    def __init__(self, x, y, kind, velocity=None):
        super().__init__(*self.containers)
        self.kind = kind # power-up type
        self.image = self.__build_image(kind)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        self.position = pygame.Vector2(x, y)  # For crash_check compatibility
        self.pos = self.position  # 
        self.vel = pygame.Vector2(velocity) if velocity else pygame.Vector2(0, 0)
        self.radius = POWERUP_RADIUS  # For crash_check compatibility
        self.t = 0.0
        self.drift_time = 0.0  # Track time drifting across screen

    def __build_image(self, kind):
        # Color scheme based on power-up type
        if kind == "rapid_fire":
            base_color = (220, 60, 60)  # Red
        elif kind == "spread":
            base_color = (60, 120, 240)  # Blue
        else:
            base_color = (150, 150, 150)  # Gray fallback
            
        glow_outer = 8
        glow_inner = 4
        size = (POWERUP_RADIUS + glow_outer) * 2
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        center = size // 2


        # outer glow
        pygame.draw.circle(surf, (*base_color, 40), (center, center), POWERUP_RADIUS + glow_outer)
        # inner glow
        pygame.draw.circle(surf, (*base_color, 100), (center, center), POWERUP_RADIUS + glow_inner)
        # core
        pygame.draw.circle(surf, (*base_color, 180), (center, center), POWERUP_RADIUS)
        # Ring outline
        pygame.draw.circle(surf, (255, 255, 255, 200), (center, center), POWERUP_RADIUS - 3, 2)

        # icons for power ups
        if kind == "rapid_fire":
            pygame.draw.line(surf, (255, 255, 255, 230), (center - 6, center - 5), (center + 7, center - 5), 2)
            pygame.draw.line(surf, (255, 255, 255, 230), (center - 7, center + 1), (center + 5, center + 1), 2)
        elif kind == "spread":
            pygame.draw.line(surf, (255, 255, 255, 230), (center - 8, center + 4), (center, center - 6), 2)
            pygame.draw.line(surf, (255, 255, 255, 230), (center + 8, center + 4), (center, center - 6), 2)
        
        return surf
    
    def update(self, dt):
        # drift 
        self.pos += self.vel * dt
        self.position = self.pos  # Keep position synced for crash_check

        # Track drift time
        self.drift_time += dt
        
        # Kill powerup if drift duration exceeded
        if self.drift_time >= POWERUP_DRIFT_DURATION:
            self.kill()
            return

        # gentle bob
        self.t += dt
        bob = math.sin(self.t * 3.0) * 2.0

        # Kill powerup if it goes off-screen (hits edge)
        margin = POWERUP_RADIUS + 10
        if (self.pos.x < -margin or self.pos.x > SCREEN_WIDTH + margin or
            self.pos.y < -margin or self.pos.y > SCREEN_HEIGHT + margin):
            self.kill()
            return
        
        self.rect.center = (int(self.pos.x), int(self.pos.y + bob))
    
    def draw(self, screen):
        """Draw the power-up sprite on the screen"""
        screen.blit(self.image, self.rect)
