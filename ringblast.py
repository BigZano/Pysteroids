import pygame
import random
import math
from circleshape import CircleShape
from constants import *

# Element color constants
ICE_PRIMARY = (150, 220, 255)
ICE_SECONDARY = (200, 240, 255)
ICE_HIGHLIGHT = (200, 240, 255)
FIRE_CORE = (255, 255, 200)
LIGHTNING_PRIMARY = (255, 255, 200)
LIGHTNING_SECONDARY = (200, 180, 255)
LIGHTNING_GLOW = (200, 150, 255)

class NovaParticle:
    """Elemental particle for ring blast visual effects"""
    def __init__(self, x, y, angle, element_type, ring_radius):
        self.pos = pygame.Vector2(x, y)
        self.angle = angle
        self.element = element_type
        self.life = 1.0
        self.age = 0.0
        
        # Element-specific initialization
        if element_type == "ice":
            self._init_ice(angle)
        elif element_type == "fire":
            self._init_fire(angle)
        else:  # lightning
            self._init_lightning(angle)
    
    def _init_ice(self, angle):
        """Initialize ice particle properties"""
        self.color = ICE_PRIMARY
        self.secondary_color = ICE_SECONDARY
        self.decay_rate = random.uniform(3.5, 5.0)
        self.size = random.uniform(2, 5)
        perp_angle = angle + random.uniform(-15, 15)
        speed = random.uniform(80, 150)
        self.velocity = pygame.Vector2.from_polar((speed, perp_angle))
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-300, 300)
        self.shape = "crystal"
    
    def _init_fire(self, angle):
        """Initialize fire particle properties"""
        self.color = (255, random.randint(150, 200), random.randint(0, 50))
        self.secondary_color = (255, random.randint(100, 150), 0)
        self.decay_rate = random.uniform(2.5, 4.0)
        self.size = random.uniform(2, 6)
        drift_angle = angle + random.uniform(-30, 30)
        speed = random.uniform(40, 80)
        self.velocity = pygame.Vector2.from_polar((speed, drift_angle))
        self.velocity.y -= random.uniform(30, 60)
        self.rotation = 0
        self.rotation_speed = 0
        self.shape = "ember"
        self.flicker = random.uniform(0.7, 1.0)
    
    def _init_lightning(self, angle):
        """Initialize lightning particle properties"""
        self.color = (255, 255, random.randint(200, 255))
        self.secondary_color = LIGHTNING_SECONDARY
        self.decay_rate = random.uniform(5.0, 8.0)
        self.size = random.uniform(1, 3)
        speed = random.uniform(100, 200)
        self.velocity = pygame.Vector2.from_polar((speed, angle + random.uniform(-45, 45)))
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-500, 500)
        self.shape = "arc"
        self.flicker = random.random() > 0.4
        self.arc_length = random.uniform(8, 15)
    
    def update(self, dt):
        """Update particle position and life"""
        self.age += dt
        self.life -= self.decay_rate * dt
        self.pos += self.velocity * dt
        self.rotation += self.rotation_speed * dt
        
        # Element-specific updates
        if self.element == "fire":
            # Fire slows down and flickers
            self.velocity *= 0.96
            self.flicker = 0.7 + 0.3 * math.sin(self.age * 15)
        elif self.element == "lightning":
            # Lightning changes direction erratically
            if random.random() < 0.3:
                self.velocity.rotate_ip(random.uniform(-30, 30))
        
        return self.life > 0
    
    def draw(self, screen):
        """Draw particle based on element type"""
        if self.life <= 0:
            return
        
        alpha = int(255 * self.life)
        
        if self.shape == "crystal":
            self._draw_crystal(screen, alpha)
        elif self.shape == "ember":
            self._draw_ember(screen, alpha)
        elif self.shape == "arc":
            self._draw_arc(screen, alpha)
    
    def _draw_crystal(self, screen, alpha):
        """Draw ice crystal shard"""
        crystal_length = self.size * 3
        points = []
        for i in range(3):
            angle_offset = (i * 120) + self.rotation
            rad = math.radians(angle_offset)
            dist = crystal_length if i == 0 else crystal_length * 0.3
            px = self.pos.x + math.cos(rad) * dist
            py = self.pos.y + math.sin(rad) * dist
            points.append((int(px), int(py)))
        
        if len(points) >= 3:
            surf = pygame.Surface((int(crystal_length * 2 + 10), int(crystal_length * 2 + 10)), pygame.SRCALPHA)
            offset = pygame.Vector2(crystal_length + 5, crystal_length + 5)
            local_points = [(p[0] - self.pos.x + offset.x, p[1] - self.pos.y + offset.y) for p in points]
            
            pygame.draw.polygon(surf, (*self.secondary_color, alpha // 2), local_points)
            pygame.draw.polygon(surf, (*self.color, alpha), local_points)
            
            screen.blit(surf, (int(self.pos.x - offset.x), int(self.pos.y - offset.y)))
    
    def _draw_ember(self, screen, alpha):
        """Draw fire ember"""
        surf_size = int(self.size * 4 + 10)
        surf = pygame.Surface((surf_size, surf_size), pygame.SRCALPHA)
        center = surf_size // 2
        
        pygame.draw.circle(surf, (*self.secondary_color, int(alpha * 0.3 * self.flicker)), (center, center), int(self.size * 2))
        pygame.draw.circle(surf, (*self.color, int(alpha * 0.6 * self.flicker)), (center, center), int(self.size * 1.2))
        pygame.draw.circle(surf, (255, 255, 200, int(alpha * self.flicker)), (center, center), int(self.size * 0.6))
        
        screen.blit(surf, (int(self.pos.x - surf_size // 2), int(self.pos.y - surf_size // 2)))
    
    def _draw_arc(self, screen, alpha):
        """Draw lightning arc"""
        if self.flicker or random.random() > 0.3:
            end_rad = math.radians(self.rotation)
            end_pos = self.pos + pygame.Vector2(math.cos(end_rad), math.sin(end_rad)) * self.arc_length
            
            # Create jagged line
            points = [self.pos]
            for i in range(1, 3):
                t = i / 3
                mid = self.pos.lerp(end_pos, t)
                offset = random.uniform(-self.arc_length * 0.3, self.arc_length * 0.3)
                perp = pygame.Vector2(math.cos(end_rad + math.pi/2), math.sin(end_rad + math.pi/2)) * offset
                points.append(mid + perp)
            points.append(end_pos)
            
            # Draw glow and core
            for i in range(len(points) - 1):
                pygame.draw.line(screen, (*self.secondary_color, alpha // 2), 
                               (int(points[i].x), int(points[i].y)),
                               (int(points[i + 1].x), int(points[i + 1].y)), 3)
            for i in range(len(points) - 1):
                pygame.draw.line(screen, (*self.color, alpha), 
                               (int(points[i].x), int(points[i].y)),
                               (int(points[i + 1].x), int(points[i + 1].y)), 1)


class RingBlast(CircleShape):
    """Expanding ring that damages asteroids and boss"""
    containers = None
    
    def __init__(self, x, y, charge_level):
        super().__init__(x, y, 0)
        
        self.charge_level = charge_level
        self.current_radius = 0
        self.age = 0.0
        self.particles = []
        self.particle_spawn_timer = 0.0
        self.particle_spawn_interval = 0.016
        self.hit_objects = set()
        
        # Element configs: (max_radius, boss_damage, color, element, particles_per_spawn)
        configs = {
            1: (RING_CHARGE_1_RADIUS, RING_CHARGE_1_BOSS_DAMAGE, (100, 150, 255), "ice", 16),
            2: (RING_CHARGE_2_RADIUS, RING_CHARGE_2_BOSS_DAMAGE, (255, 100, 100), "fire", 24),
            3: (RING_CHARGE_3_RADIUS, RING_CHARGE_3_BOSS_DAMAGE, (255, 255, 100), "lightning", 12)
        }
        
        config = configs.get(charge_level, configs[1])
        self.max_radius, self.boss_damage, self.color, self.element, self.particles_per_spawn = config
        
        if RingBlast.containers:
            for container in RingBlast.containers:
                container.add(self)
    
    
    def _spawn_particles_at_wavefront(self):
        """Spawn elemental particles at the expanding ring edge"""
        if self.current_radius <= 0:
            return
        
        # Spawn particles around the ring circumference
        for _ in range(self.particles_per_spawn):
            angle = random.uniform(0, 360)
            rad = math.radians(angle)
            
            # Position on ring edge
            px = self.position.x + math.cos(rad) * self.current_radius
            py = self.position.y + math.sin(rad) * self.current_radius
            
            particle = NovaParticle(px, py, angle, self.element, self.current_radius)
            self.particles.append(particle)
    
    def update(self, dt):
        # Expand the ring
        self.current_radius += RING_EXPANSION_SPEED * dt
        self.radius = self.current_radius
        self.age += dt
        
        # Spawn particles at wavefront
        self.particle_spawn_timer += dt
        if self.particle_spawn_timer >= self.particle_spawn_interval:
            self._spawn_particles_at_wavefront()
            self.particle_spawn_timer = 0.0
        
        # Update particles
        self.particles = [p for p in self.particles if p.update(dt)]
        
        # Kill when fully expanded
        if self.current_radius >= self.max_radius:
            self.kill()
    
    
    def draw(self, screen):
        # Draw particles first
        for particle in self.particles:
            particle.draw(screen)
        
        if self.current_radius <= 0:
            return
        
        # Draw glow
        alpha = int(100 * (1 - self.current_radius / self.max_radius))
        if alpha > 0:
            glow_size = int(self.current_radius * 2 + 40)
            glow_surface = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
            glow_center = int(self.current_radius + 20)
            pygame.draw.circle(glow_surface, (*self.color, alpha), (glow_center, glow_center), glow_center)
            screen.blit(glow_surface, (int(self.position.x - self.current_radius - 20), 
                                      int(self.position.y - self.current_radius - 20)))
        
        # Element-specific rendering
        if self.element == "ice":
            self._draw_ice_ring(screen)
        elif self.element == "fire":
            self._draw_fire_ring(screen)
        else:  # lightning
            self._draw_lightning_ring(screen)
    
    def _draw_ice_ring(self, screen):
        """Draw ice ring with frost effect"""
        for thickness in range(4):
            radius = int(self.current_radius - thickness * 2)
            if radius > 0:
                pygame.draw.circle(screen, self.color, (int(self.position.x), int(self.position.y)), radius, 2)
                if thickness == 0:
                    pygame.draw.circle(screen, ICE_HIGHLIGHT, (int(self.position.x), int(self.position.y)), radius, 1)
    
    def _draw_fire_ring(self, screen):
        """Draw flickering fire ring"""
        flicker = 0.9 + 0.1 * math.sin(self.age * 12)
        for thickness in range(5):
            radius = int(self.current_radius - thickness * 3)
            if radius > 0:
                t = thickness / 5.0
                color = (255, int(200 - t * 100), int(50 * (1 - t)))
                line_width = 2 if thickness % 2 == 0 else 1
                offset_x = int(math.sin(self.age * 8 + thickness) * 2)
                offset_y = int(math.cos(self.age * 6 + thickness) * 2)
                pygame.draw.circle(screen, color, 
                                 (int(self.position.x + offset_x), int(self.position.y + offset_y)), 
                                 radius, line_width)
    
    def _draw_lightning_ring(self, screen):
        """Draw electric lightning ring"""
        num_segments = 48
        points = []
        for i in range(num_segments):
            angle = (i / num_segments) * math.pi * 2
            jitter = random.uniform(-5, 5) if random.random() > 0.7 else 0
            radius = self.current_radius + jitter
            px = self.position.x + math.cos(angle) * radius
            py = self.position.y + math.sin(angle) * radius
            points.append((int(px), int(py)))
        
        for i in range(len(points)):
            next_i = (i + 1) % len(points)
            pygame.draw.line(screen, LIGHTNING_GLOW, points[i], points[next_i], 4)
            pygame.draw.line(screen, LIGHTNING_PRIMARY, points[i], points[next_i], 2)
        
        # Random lightning bolts
        if random.random() > 0.7:
            angle1 = random.uniform(0, math.pi * 2)
            angle2 = angle1 + random.uniform(-math.pi / 3, math.pi / 3)
            p1 = self.position + pygame.Vector2(math.cos(angle1), math.sin(angle1)) * self.current_radius
            p2 = self.position + pygame.Vector2(math.cos(angle2), math.sin(angle2)) * self.current_radius
            pygame.draw.line(screen, (255, 255, 255, 200), (int(p1.x), int(p1.y)), (int(p2.x), int(p2.y)), 1)
    
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
        self.cooldown_timer = 0.0
        self.cooldown_duration = RING_BLAST_COOLDOWN
    
    def update(self, dt):
        """Update cooldown timer"""
        if self.cooldown_timer > 0:
            self.cooldown_timer -= dt
    
    def add_charge(self):
        """Add a ring charge, capped at max_charges"""
        if self.charges < self.max_charges:
            self.charges += 1
            return True
        return False
    
    def use_charges(self):
        """Use all accumulated charges and return the charge level (if not on cooldown)"""
        if self.charges > 0 and self.cooldown_timer <= 0:
            charge_level = min(self.charges, self.max_charges)
            self.charges = 0
            self.cooldown_timer = self.cooldown_duration  # Start cooldown
            return charge_level
        return 0
    
    def reset(self):
        """Reset charges to 0"""
        self.charges = 0
        self.cooldown_timer = 0.0
    
    def get_charges(self):
        """Get current charge count"""
        return self.charges
    
    def get_cooldown(self):
        """Get remaining cooldown time"""
        return max(0.0, self.cooldown_timer)
    
    def is_ready(self):
        """Check if ring blast is ready to fire"""
        return self.charges > 0 and self.cooldown_timer <= 0


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
