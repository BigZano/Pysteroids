import pygame
from constants import *

class CircleShape(pygame.sprite.Sprite):
    """Base class for circular game objects with collision detection"""
    
    def __init__(self, x, y, radius):
        if hasattr(self, "containers"):
            super().__init__(self.containers)
        else:
            super().__init__()

        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)
        self.radius = radius

    def crash_check(self, other):
        """Check if this object collides with another circular object"""
        return self.position.distance_to(other.position) < self.radius + other.radius

    def draw(self, screen):
        """Override in subclasses to implement drawing"""
        pass

    def update(self, dt):
        """Override in subclasses to implement update logic"""
        pass
