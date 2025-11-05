import pygame
import random
import math
from circleshape import CircleShape
from constants import *
from powerup import PowerUp
from ringblast import RingChargePowerUp

class IceTrail(pygame.sprite.Sprite):
    """Ice trail left by boss that damages player"""
    containers = ()
    
    def __init__(self, x, y, radius):
        super().__init__(*self.containers)
        self.position = pygame.Vector2(x, y)
        self.radius = radius
        self.lifetime = ICE_TRAIL_DURATION
        self.damage_cooldown = 0.0
        
    def update(self, dt):
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.kill()
        
        # Update damage cooldown
        self.damage_cooldown += dt
    
    def can_damage(self):
        """Returns True if enough time has passed to damage again"""
        if self.damage_cooldown >= ICE_TRAIL_DAMAGE_COOLDOWN:
            self.damage_cooldown = 0.0
            return True
        return False
    
    def crash_check(self, other):
        """Check collision with another object"""
        distance = self.position.distance_to(other.position)
        return distance < self.radius + getattr(other, 'radius', 0)
        
    def draw(self, screen):
        # Fade out ice trail as it expires
        alpha = int(255 * (self.lifetime / ICE_TRAIL_DURATION))
        alpha = max(0, min(255, alpha))
        
        # Draw icy blue trail with glow
        surf = pygame.Surface((int(self.radius * 2), int(self.radius * 2)), pygame.SRCALPHA)
        center = int(self.radius)
        pygame.draw.circle(surf, (100, 200, 255, alpha // 2), (center, center), int(self.radius))
        pygame.draw.circle(surf, (150, 220, 255, alpha), (center, center), int(self.radius * 0.7))
        pygame.draw.circle(surf, (200, 240, 255, alpha), (center, center), int(self.radius * 0.4), 2)
        screen.blit(surf, (int(self.position.x - self.radius), int(self.position.y - self.radius)))

class BossAsteroid(CircleShape):
    """Large boss asteroid with ice trail and scaling HP"""
    sounds = {}
    
    def __init__(self, boss_number):
        # Calculate HP with cumulative square root growth
        hp = BOSS_STARTING_HP
        for _ in range(boss_number):
            hp = int(hp + math.sqrt(hp))
        
        # Spawn from random edge
        edges = [
            (-BOSS_RADIUS, random.uniform(0, SCREEN_HEIGHT), pygame.Vector2(1, 0)),  # Left
            (SCREEN_WIDTH + BOSS_RADIUS, random.uniform(0, SCREEN_HEIGHT), pygame.Vector2(-1, 0)),  # Right
            (random.uniform(0, SCREEN_WIDTH), -BOSS_RADIUS, pygame.Vector2(0, 1)),  # Top
            (random.uniform(0, SCREEN_WIDTH), SCREEN_HEIGHT + BOSS_RADIUS, pygame.Vector2(0, -1))  # Bottom
        ]
        x, y, direction = random.choice(edges)
            
        super().__init__(x, y, BOSS_RADIUS)
        self.hp = hp
        self.max_hp = hp
        self.velocity = direction.rotate(random.uniform(-15, 15)) * BOSS_SPEED
        self.trail_timer = 0.0
        self.trail_interval = 0.3
        self.boss_number = boss_number
        
    def take_damage(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            self.split()
            
    def update(self, dt):
        self.position += self.velocity * dt
        
        # Screen wrap with direction change
        margin = BOSS_RADIUS + 10
        
        # Horizontal wrapping
        if self.position.x < -margin or self.position.x > SCREEN_WIDTH + margin:
            self.position.x = SCREEN_WIDTH + margin if self.position.x < -margin else -margin
            direction = pygame.Vector2(-1, 0) if self.position.x > SCREEN_WIDTH else pygame.Vector2(1, 0)
            self.velocity = direction.rotate(random.uniform(-60, 60)) * BOSS_SPEED
        
        # Vertical wrapping
        if self.position.y < -margin or self.position.y > SCREEN_HEIGHT + margin:
            self.position.y = SCREEN_HEIGHT + margin if self.position.y < -margin else -margin
            direction = pygame.Vector2(0, 1) if self.position.y > SCREEN_HEIGHT else pygame.Vector2(0, -1)
            self.velocity = direction.rotate(random.uniform(-60, 60)) * BOSS_SPEED
        
        # Leave ice trail
        self.trail_timer += dt
        if self.trail_timer >= self.trail_interval:
            IceTrail(self.position.x, self.position.y, self.radius * 0.8)
            self.trail_timer = 0.0
            
    def draw(self, screen):
        # Draw boss with special appearance
        # Outer glow
        surf = pygame.Surface((int(self.radius * 2.5), int(self.radius * 2.5)), pygame.SRCALPHA)
        center = int(self.radius * 1.25)
        pygame.draw.circle(surf, (100, 255, 255, 40), (center, center), int(self.radius * 1.2))
        pygame.draw.circle(surf, (150, 255, 255, 80), (center, center), int(self.radius))
        # Main body
        pygame.draw.circle(surf, (200, 255, 255, 200), (center, center), int(self.radius * 0.9))
        # Core
        pygame.draw.circle(surf, (255, 255, 255), (center, center), int(self.radius * 0.3))
        # Outline
        pygame.draw.circle(surf, (255, 255, 255), (center, center), int(self.radius), 3)
        
        screen.blit(surf, (int(self.position.x - self.radius * 1.25), int(self.position.y - self.radius * 1.25)))
        
    def split(self):
        """Destroy boss and drop powerups"""
        # Play boss destruction sound
        if self.sounds:
            sound = self.sounds.get("bossteroid")
            if sound:
                sound.play()
        
        # Drop 3 powerups with higher ring charge chance
        for _ in range(3):
            kind = random.choice(["rapid_fire", "spread", "ring_charge", "ring_charge"])
            direction = pygame.Vector2(1, 0).rotate(random.uniform(0, 360))
            vel = direction * random.uniform(60, 120)
            
            if kind == "ring_charge":
                RingChargePowerUp(self.position.x, self.position.y, vel)
            else:
                PowerUp(self.position.x, self.position.y, kind, vel)
        
        self.kill()