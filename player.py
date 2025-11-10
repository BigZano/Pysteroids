import pygame
import math
from circleshape import *
from constants import *
from shot import Shot, WeirdShot

class Player(CircleShape):
    # Class-level sound references
    laser_sound = None
    laser_channel = None
    rapid_fire_sound = None
    shotgun_sound = None

    def __init__(self, x, y, ship_type="default"):
        super().__init__(x, y, PLAYER_RADIUS)
        self.rotation = 0
        self.shot_timer = 0
        self.powerups = {"rapid_fire": 0.0, "spread": 0.0}
        
        # Ship-specific configuration
        self.ship_type = ship_type
        self.ship_stats = SHIP_STATS.get(ship_type, SHIP_STATS["default"])
        self.base_fire_delay = self.ship_stats.get("fire_rate", PLAYER_SHOT_COOLDOWN_DEFAULT)
        self.color = self.ship_stats.get("color", (255, 255, 255))
        self.shape = self.ship_stats.get("shape", "triangle")
        self.special_ability = self.ship_stats.get("special_ability", None)
        self.shot_type = self.ship_stats.get("shot_type", "normal")
        
        # Dash mechanics
        self.dash_cooldown = 0.0
        self.dash_active = False
        self.dash_timer = 0.0
        self.dash_direction = pygame.Vector2(0, 0)
        
        # Shield mechanics (for big git)
        self.shield_active = False
        self.shield_hits = 0
        self.shield_cooldown = 0.0
        
        # Stealth mechanics (for sneaky git)
        self.stealth_active = False
        self.stealth_timer = 0.0
        self.stealth_cooldown = 0.0
        
        # Weird shot mechanics (for weird boy)
        self.weird_shot_cooldown = 0.0

    def rotate(self, dt):
        turn_speed = self.ship_stats.get("turn_speed", PLAYER_TURN_SPEED)
        self.rotation = (turn_speed * dt + self.rotation) % 360.0

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
        
        # Update shield cooldown
        if self.shield_cooldown > 0:
            self.shield_cooldown -= dt
        
        # Update stealth
        if self.stealth_active:
            self.stealth_timer -= dt
            if self.stealth_timer <= 0:
                self.stealth_active = False
        if self.stealth_cooldown > 0:
            self.stealth_cooldown -= dt
        
        # Update weird shot cooldown
        if self.weird_shot_cooldown > 0:
            self.weird_shot_cooldown -= dt
        
        for powerup in self.powerups:
            old_value = self.powerups[powerup]
            self.powerups[powerup] = max(0.0, self.powerups[powerup] - dt)
            # Powerup timer decremented each frame
        
        # Special ability activation (F key)
        if keys[pygame.K_f]:
            self.activate_special_ability()

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
        acceleration = self.ship_stats.get("acceleration", PLAYER_ACCELERATION)
        self.position += forward * acceleration * dt

    def triangle(self):
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        right = pygame.Vector2(0, 1).rotate(self.rotation + 90) * self.radius / 1.5
        a = self.position + forward * self.radius
        b = self.position - forward * self.radius - right
        c = self.position - forward * self.radius + right
        return [a, b, c]

    def shoot(self):
        # Weird boy uses WeirdShot instead of normal shots
        if self.shot_type == "weird":
            if self.weird_shot_cooldown <= 0:
                forward = pygame.Vector2(0, 1).rotate(self.rotation)
                weird_shot = WeirdShot(self.position.x, self.position.y, forward)
                self.weird_shot_cooldown = WEIRD_SHOT_COOLDOWN
                
                # Play sound if available
                if self.laser_channel and self.laser_sound:
                    self.laser_channel.stop()
                    self.laser_channel.play(self.laser_sound)
            return
        
        # Normal shooting for other ships
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

        # Create shots using ship's shot speed
        shot_speed = self.ship_stats.get("shot_speed", PLAYER_SHOT_SPEED)
        for angle in angles:
            forward = pygame.Vector2(0, 1).rotate(angle)
            shot = Shot(*(self.position + forward * self.radius))
            shot.velocity = forward * shot_speed

    def activate_special_ability(self):
        """Activate ship-specific special ability with F key"""
        if self.special_ability == "shield":
            self.activate_shield()
        elif self.special_ability == "stealth":
            self.activate_stealth()
    
    def activate_shield(self):
        """Activate shield for big git - absorbs 3 hits, 30s cooldown"""
        if self.shield_cooldown <= 0 and not self.shield_active:
            self.shield_active = True
            self.shield_hits = SHIELD_MAX_HITS
    
    def activate_stealth(self):
        """Activate stealth for sneaky git - 5s duration, 20s cooldown"""
        if self.stealth_cooldown <= 0 and not self.stealth_active:
            self.stealth_active = True
            self.stealth_timer = STEALTH_DURATION
            self.stealth_cooldown = STEALTH_COOLDOWN
    
    def take_damage(self):
        """Handle taking damage - returns True if damage was taken, False if blocked"""
        if self.shield_active:
            self.shield_hits -= 1
            if self.shield_hits <= 0:
                self.shield_active = False
                self.shield_cooldown = SHIELD_COOLDOWN
            return False  # Damage blocked
        return True  # Damage taken
    
    def is_invincible_dash(self):
        """Returns True if player is invincible due to dash"""
        return DASH_INVINCIBILITY and self.dash_active
    
    def is_invisible(self):
        """Returns True if player is invisible due to stealth"""
        return self.stealth_active
    
    def draw(self, screen):
        # Don't draw if stealthed
        if self.stealth_active:
            # Draw faint outline when stealthed
            pygame.draw.polygon(screen, (50, 50, 100, 50), self.get_shape_points(), 1)
            return
        
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
        
        # Draw shield if active
        if self.shield_active:
            shield_color = (100, 200, 255)
            # Pulsing effect based on hits remaining
            pulse = 1.0 + (0.2 * math.sin(pygame.time.get_ticks() / 200))
            shield_radius = self.radius * 1.5 * pulse
            
            # Draw multiple shield rings for visual effect
            for i in range(3):
                alpha = int(100 - (i * 30))
                pygame.draw.circle(screen, (*shield_color, alpha), 
                                 (int(self.position.x), int(self.position.y)), 
                                 int(shield_radius + i * 3), 2)
        
        # Draw main ship with color
        pygame.draw.polygon(screen, self.color, self.get_shape_points(), 2)
    
    def get_shape_points(self):
        """Get the points for the ship shape based on ship type"""
        if self.shape == "triangle":
            return self.triangle()
        elif self.shape == "arrow":
            return self.arrow_shape()
        elif self.shape == "diamond":
            return self.diamond_shape()
        elif self.shape == "needle":
            return self.needle_shape()
        elif self.shape == "star":
            return self.star_shape()
        return self.triangle()
    
    def arrow_shape(self):
        """Sleek arrow shape for fast git"""
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        right = pygame.Vector2(0, 1).rotate(self.rotation + 90)
        
        tip = self.position + forward * self.radius * 1.3
        left_wing = self.position - forward * self.radius * 0.3 - right * self.radius * 0.8
        tail = self.position - forward * self.radius
        right_wing = self.position - forward * self.radius * 0.3 + right * self.radius * 0.8
        
        return [tip, left_wing, tail, right_wing]
    
    def diamond_shape(self):
        """Wider diamond for big git"""
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        right = pygame.Vector2(0, 1).rotate(self.rotation + 90)
        
        front = self.position + forward * self.radius
        left = self.position - right * self.radius * 1.2
        back = self.position - forward * self.radius
        right_p = self.position + right * self.radius * 1.2
        
        return [front, left, back, right_p]
    
    def needle_shape(self):
        """Long thin shape for sneaky git"""
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        right = pygame.Vector2(0, 1).rotate(self.rotation + 90)
        
        tip = self.position + forward * self.radius * 1.5
        left = self.position - forward * self.radius * 0.5 - right * self.radius * 0.4
        back = self.position - forward * self.radius
        right_p = self.position - forward * self.radius * 0.5 + right * self.radius * 0.4
        
        return [tip, left, back, right_p]
    
    def star_shape(self):
        """5-pointed star for weird boy ship"""
        points = []
        for i in range(5):
            # Outer point
            angle = self.rotation + (i * 72)
            outer = pygame.Vector2(0, 1).rotate(angle) * self.radius
            points.append(self.position + outer)
            
            # Inner point
            angle = self.rotation + (i * 72 + 36)
            inner = pygame.Vector2(0, 1).rotate(angle) * (self.radius * 0.5)
            points.append(self.position + inner)
        
        return points