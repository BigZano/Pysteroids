import pygame
import math
from circleshape import *
from constants import *
from shot import Shot

class Player(CircleShape):
    # Class-level sound references
    laser_sound = None
    laser_channel = None
    rapid_fire_sound = None
    shotgun_sound = None

    def __init__(self, x, y):
        super().__init__(x, y, PLAYER_RADIUS)
        self.rotation = 0
        self.shot_timer = 0
        self.powerups = {"rapid_fire": 0.0, "spread": 0.0}
        self.base_fire_delay = PLAYER_SHOT_COOLDOWN_DEFAULT
        
        # Dash mechanics
        self.dash_cooldown = 0.0
        self.dash_active = False
        self.dash_timer = 0.0
        self.dash_direction = pygame.Vector2(0, 0)

    def rotate(self, dt):
        self.rotation = (PLAYER_TURN_SPEED * dt + self.rotation) % 360.0

    def add_powerup(self, kind):
        if kind in self.powerups:
            from constants import POWERUP_DURATION  # Ensure fresh import
            self.powerups[kind] = POWERUP_DURATION
    
    def current_fire_delay(self):
        return RAPID_FIRE_COOLDOWN if self.powerups["rapid_fire"] > 0.0 else self.base_fire_delay

    def update(self, dt):
        keys = pygame.key.get_pressed()
        mouse_buttons = pygame.mouse.get_pressed()
        self.shot_timer += dt

        # Update dash state
        if self.dash_active:
            self.dash_timer -= dt
            if self.dash_timer <= 0:
                self.dash_active = False
            else:
                self.position += self.dash_direction * DASH_SPEED * dt
        
        # Update cooldowns and powerups
        if self.dash_cooldown > 0:
            self.dash_cooldown -= dt
        
        for powerup in self.powerups:
            old_value = self.powerups[powerup]
            self.powerups[powerup] = max(0.0, self.powerups[powerup] - dt)
            # Powerup timer decremented each frame

        # Movement
        if keys[pygame.K_w]:
            self.move(dt)
        if keys[pygame.K_s]:
            self.move(-dt)
        if keys[pygame.K_a]:
            self.rotate(-dt)
        if keys[pygame.K_d]:
            self.rotate(dt)
        
        # Mouse aiming and firing
        if mouse_buttons[0]:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            dx = mouse_x - self.position.x
            dy = mouse_y - self.position.y
            self.rotation = -math.degrees(math.atan2(dx, dy))
            
            if self.shot_timer >= self.current_fire_delay():
                self.shoot()
                self.shot_timer = 0
        # Keyboard firing
        elif keys[pygame.K_SPACE] and self.shot_timer >= self.current_fire_delay():
            self.shoot()
            self.shot_timer = 0

    def move(self, dt):
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        self.position += forward * PLAYER_ACCELERATION * dt

    def triangle(self):
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        right = pygame.Vector2(0, 1).rotate(self.rotation + 90) * self.radius / 1.5
        a = self.position + forward * self.radius
        b = self.position - forward * self.radius - right
        c = self.position - forward * self.radius + right
        return [a, b, c]

    def shoot(self):
        # Determine active powerup and play appropriate sound
        if self.laser_channel:
            rapid_active = self.powerups["rapid_fire"] > 0.0
            spread_active = self.powerups["spread"] > 0.0
            
            # Select sound based on active powerup (most recent if both active)
            if rapid_active and spread_active:
                sound = self.rapid_fire_sound if self.powerups["rapid_fire"] >= self.powerups["spread"] else self.shotgun_sound
            elif rapid_active:
                sound = self.rapid_fire_sound
            elif spread_active:
                sound = self.shotgun_sound
            else:
                sound = self.laser_sound
            
            if sound:
                self.laser_channel.stop()
                self.laser_channel.play(sound)

        # Calculate shot angles
        center_angle = self.rotation
        angles = [center_angle]

        if self.powerups["spread"] > 0.0 and SPREAD_BULLETS >= 3:
            half = (SPREAD_BULLETS - 1) // 2
            angles = [center_angle + (i * SPREAD_ANGLE_DEG) for i in range(-half, half + 1)]

        # Create shots
        for angle in angles:
            forward = pygame.Vector2(0, 1).rotate(angle)
            shot = Shot(*(self.position + forward * self.radius))
            shot.velocity = forward * PLAYER_SHOT_SPEED

    def is_invincible_dash(self):
        """Returns True if player is invincible due to dash"""
        return DASH_INVINCIBILITY and self.dash_active
    
    def draw(self, screen):
        # Draw dash trail if active
        if self.dash_active:
            trail_color = (100, 200, 255)
            for i in range(3):
                alpha = int(100 / (i + 1))
                trail_pos = self.position - self.dash_direction * 30 * (i + 1)
                
                # Create trail surface with alpha
                surf = pygame.Surface((self.radius * 4, self.radius * 4), pygame.SRCALPHA)
                center_offset = pygame.Vector2(self.radius * 2, self.radius * 2)
                
                # Calculate triangle points relative to trail surface
                forward = pygame.Vector2(0, 1).rotate(self.rotation)
                right = pygame.Vector2(0, 1).rotate(self.rotation + 90) * self.radius / 1.5
                
                a = center_offset + forward * self.radius
                b = center_offset - forward * self.radius - right
                c = center_offset - forward * self.radius + right
                
                pygame.draw.polygon(surf, (*trail_color, alpha), [a, b, c], 2)
                screen.blit(surf, (trail_pos.x - self.radius * 2, trail_pos.y - self.radius * 2))
        
        # Draw main ship
        pygame.draw.polygon(screen, (255, 255, 255), self.triangle(), 2)