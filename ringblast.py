import pygame
import random
import math
from circleshape import CircleShape
from constants import *


class RingBlast(CircleShape):
    """Expanding ring that damages asteroids and boss"""
    containers = None
    
    def __init__(self, x, y, charge_level):
        # Start with radius 0, will expand
        super().__init__(x, y, 0)
        
        self.charge_level = charge_level
        self.current_radius = 0
        
        # Set max radius and damage based on charge level
        if charge_level == 1:
            self.max_radius = RING_CHARGE_1_RADIUS
            self.boss_damage = RING_CHARGE_1_BOSS_DAMAGE
            self.color = (100, 150, 255)  # Blue
        elif charge_level == 2:
            self.max_radius = RING_CHARGE_2_RADIUS
            self.boss_damage = RING_CHARGE_2_BOSS_DAMAGE
            self.color = (255, 100, 100)  # Red
        else:  # charge_level == 3
            self.max_radius = RING_CHARGE_3_RADIUS
            self.boss_damage = RING_CHARGE_3_BOSS_DAMAGE
            self.color = (255, 255, 100)  # Yellow
        
        # Track which objects we've already hit
        self.hit_objects = set()
        
        # Add to containers
        if RingBlast.containers:
            for container in RingBlast.containers:
                container.add(self)
    
    def update(self, dt):
        # Expand the ring
        self.current_radius += RING_EXPANSION_SPEED * dt
        self.radius = self.current_radius
        
        # Kill when fully expanded
        if self.current_radius >= self.max_radius:
            self.kill()
    
    def draw(self, screen):
        # Draw expanding ring with glow effect
        if self.current_radius > 0:
            # Outer glow
            alpha = int(100 * (1 - self.current_radius / self.max_radius))
            if alpha > 0:
                glow_surface = pygame.Surface((int(self.current_radius * 2 + 40), int(self.current_radius * 2 + 40)), pygame.SRCALPHA)
                pygame.draw.circle(glow_surface, (*self.color, alpha), 
                                 (int(self.current_radius + 20), int(self.current_radius + 20)), 
                                 int(self.current_radius + 20))
                screen.blit(glow_surface, 
                          (int(self.position.x - self.current_radius - 20), 
                           int(self.position.y - self.current_radius - 20)))
            
            # Main ring (3 circles for thickness)
            for thickness in range(3):
                radius = int(self.current_radius - thickness * 2)
                if radius > 0:
                    pygame.draw.circle(screen, self.color, 
                                     (int(self.position.x), int(self.position.y)), 
                                     radius, 2)
    
    def has_hit(self, obj):
        """Check if we've already hit this object"""
        return id(obj) in self.hit_objects
    
    def mark_hit(self, obj):
        """Mark an object as hit"""
        self.hit_objects.add(id(obj))


class RingChargeManager:
    """Manager for ring blast charges - tracks and manages ring charge state"""
    def __init__(self):
        self.charges = 0
        self.max_charges = 3
    
    def add_charge(self):
        """Add a ring charge, capped at max_charges"""
        if self.charges < self.max_charges:
            self.charges += 1
            return True
        return False
    
    def use_charges(self):
        """Use all accumulated charges and return the charge level"""
        if self.charges > 0:
            charge_level = min(self.charges, self.max_charges)
            self.charges = 0
            return charge_level
        return 0
    
    def reset(self):
        """Reset charges to 0"""
        self.charges = 0
    
    def get_charges(self):
        """Get current charge count"""
        return self.charges


class RingChargePowerUp(pygame.sprite.Sprite):
    """Ring charge powerup - collectible that adds ring blast charges"""
    containers = ()
    
    def __init__(self, x, y, velocity=None):
        super().__init__(*self.containers)
        self.kind = "ring_charge"
        self.image = self.__build_image()
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        self.position = pygame.Vector2(x, y)
        self.pos = self.position
        self.vel = pygame.Vector2(velocity) if velocity else pygame.Vector2(0, 0)
        self.radius = POWERUP_RADIUS
        self.t = 0.0
    
    def __build_image(self):
        """Build the ring charge powerup sprite (gold colored)"""
        base_color = (255, 215, 0)  # Gold
        glow_outer = 8
        glow_inner = 4
        size = (POWERUP_RADIUS + glow_outer) * 2
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        center = size // 2

        # Outer glow
        pygame.draw.circle(surf, (*base_color, 40), (center, center), POWERUP_RADIUS + glow_outer)
        # Inner glow
        pygame.draw.circle(surf, (*base_color, 100), (center, center), POWERUP_RADIUS + glow_inner)
        # Core
        pygame.draw.circle(surf, (*base_color, 180), (center, center), POWERUP_RADIUS)
        # Ring outline
        pygame.draw.circle(surf, (255, 255, 255, 200), (center, center), POWERUP_RADIUS - 3, 2)

        # Draw "R" icon for ring
        pygame.draw.circle(surf, (255, 255, 255, 230), (center, center), 6, 2)
        pygame.draw.circle(surf, (255, 255, 255, 230), (center, center), 3, 0)
        
        return surf
    
    def update(self, dt):
        """Update powerup position and animation"""
        # Drift
        self.pos += self.vel * dt
        self.position = self.pos

        # Gentle bob animation
        self.t += dt
        bob = math.sin(self.t * 3.0) * 2.0

        # Screen wrap
        margin = POWERUP_RADIUS + 10
        if self.pos.x < -margin:
            self.pos.x = SCREEN_WIDTH + margin
        elif self.pos.x > SCREEN_WIDTH + margin:
            self.pos.x = -margin
        if self.pos.y < -margin:
            self.pos.y = SCREEN_HEIGHT + margin
        elif self.pos.y > SCREEN_HEIGHT + margin:
            self.pos.y = -margin
        
        self.rect.center = (int(self.pos.x), int(self.pos.y + bob))
    
    def draw(self, screen):
        """Draw the ring charge powerup on screen"""
        screen.blit(self.image, self.rect)
