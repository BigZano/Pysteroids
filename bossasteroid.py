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
    sounds = {}
    
    def __init__(self, boss_number):
        # Calculate HP with cumulative square root growth
        # Boss 0: 100
        # Boss 1: 100 + sqrt(100) = 110
        # Boss 2: 110 + sqrt(110) = ~120.5
        # Boss 3: 120.5 + sqrt(120.5) = ~131.5, etc.
        
        hp = BOSS_STARTING_HP
        for i in range(boss_number):
            hp = hp + math.sqrt(hp)
        hp = int(hp)  # Convert to integer
        
        # Random edge spawn
        edge = random.choice([0, 1, 2, 3])  # left, right, top, bottom
        if edge == 0:  # left
            x, y = -BOSS_RADIUS, random.uniform(0, SCREEN_HEIGHT)
            velocity = pygame.Vector2(1, 0)
        elif edge == 1:  # right
            x, y = SCREEN_WIDTH + BOSS_RADIUS, random.uniform(0, SCREEN_HEIGHT)
            velocity = pygame.Vector2(-1, 0)
        elif edge == 2:  # top
            x, y = random.uniform(0, SCREEN_WIDTH), -BOSS_RADIUS
            velocity = pygame.Vector2(0, 1)
        else:  # bottom
            x, y = random.uniform(0, SCREEN_WIDTH), SCREEN_HEIGHT + BOSS_RADIUS
            velocity = pygame.Vector2(0, -1)
            
        super().__init__(x, y, BOSS_RADIUS)
        self.hp = hp
        self.max_hp = hp
        self.velocity = velocity.rotate(random.uniform(-15, 15)) * BOSS_SPEED
        self.trail_timer = 0.0
        self.trail_interval = 0.3  # Leave trail every 0.3 seconds
        self.boss_number = boss_number
        
    def take_damage(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            self.split()
            
    def update(self, dt):
        self.position += self.velocity * dt
        
        # Screen wrap - change direction on edge to ensure boss moves toward screen
        margin = BOSS_RADIUS + 10
        if self.position.x < -margin or self.position.x > SCREEN_WIDTH + margin:
            # Re-enter from opposite side with new direction pointing toward screen center
            if self.position.x < -margin:
                self.position.x = SCREEN_WIDTH + margin
                # Point generally toward left side of screen (270 to 90 degrees, excluding extreme angles)
                angle = random.uniform(-60, 60)  # -60 to 60 from straight left
                direction = pygame.Vector2(-1, 0).rotate(angle)
            else:
                self.position.x = -margin
                # Point generally toward right side of screen
                angle = random.uniform(-60, 60)  # -60 to 60 from straight right
                direction = pygame.Vector2(1, 0).rotate(angle)
            self.velocity = direction * BOSS_SPEED
            
        if self.position.y < -margin or self.position.y > SCREEN_HEIGHT + margin:
            if self.position.y < -margin:
                self.position.y = SCREEN_HEIGHT + margin
                # Point generally toward top of screen
                angle = random.uniform(-60, 60)  # -60 to 60 from straight down
                direction = pygame.Vector2(0, 1).rotate(angle)
            else:
                self.position.y = -margin
                # Point generally toward bottom of screen
                angle = random.uniform(-60, 60)  # -60 to 60 from straight up
                direction = pygame.Vector2(0, -1).rotate(angle)
            self.velocity = direction * BOSS_SPEED
            
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
        # Play boss asteroid sound
        if self.sounds:
            sound = self.sounds.get("bossteroid")
            if sound:
                sound.play()
                
        # Drop power-ups (bosses drop more ring charges)
        for _ in range(3):  # Drop 3 power-ups
            kind = random.choice(["rapid_fire", "spread", "ring_charge", "ring_charge"])  # Higher chance for ring charges
            angle = random.uniform(0, 360)
            dir_vec = pygame.Vector2(1, 0).rotate(angle)
            speed = random.uniform(60, 120)
            vel = dir_vec * speed
            
            # Spawn appropriate powerup type
            if kind == "ring_charge":
                RingChargePowerUp(self.position.x, self.position.y, vel)
            else:
                PowerUp(self.position.x, self.position.y, kind, vel)
            
        self.kill()