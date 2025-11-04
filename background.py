import pygame
import random
import math
import constants
from noise import pnoise2


class Star:
    def __init__(self, layer):
        self.x = random.uniform(0, constants.SCREEN_WIDTH)
        self.y = random.uniform(0, constants.SCREEN_HEIGHT)
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
                self.x = constants.SCREEN_WIDTH
                self.y = random.uniform(0, constants.SCREEN_HEIGHT)
        elif scroll_direction == 1:  # Down
            self.y += scroll_speed * dt
            if self.y > constants.SCREEN_HEIGHT:
                self.y = 0
                self.x = random.uniform(0, constants.SCREEN_WIDTH)
        elif scroll_direction == 2:  # Right
            self.x += scroll_speed * dt
            if self.x > constants.SCREEN_WIDTH:
                self.x = 0
                self.y = random.uniform(0, constants.SCREEN_HEIGHT)
        elif scroll_direction == 3:  # Up
            self.y -= scroll_speed * dt
            if self.y < 0:
                self.y = constants.SCREEN_HEIGHT
                self.x = random.uniform(0, constants.SCREEN_WIDTH)


class NebulaCloud:
    def __init__(self):
        self.x = random.uniform(0, constants.SCREEN_WIDTH)
        self.y = random.uniform(0, constants.SCREEN_HEIGHT)
        self.size = random.uniform(120, 280)
        
        # Purple/Indigo color scheme
        self.color = random.choice([
            (60, 30, 100),   # Deep purple
            (40, 20, 80),    # Dark purple
            (30, 40, 90),    # Purple-blue
            (50, 20, 70),    # Magenta-purple
            (35, 30, 85),    # Indigo
        ])
        self.secondary_color = random.choice([
            (80, 50, 130),   # Light purple
            (60, 40, 110),   # Medium purple
            (70, 60, 120),   # Purple-blue light
        ])
        self.alpha = random.randint(25, 50)
        self.drift_speed = random.uniform(3, 8)  # Moderate lazy drift
        self.noise_offset_x = random.uniform(0, 1000)
        self.noise_offset_y = random.uniform(0, 1000)
        self.time_offset = random.uniform(0, 100)
        self.pulse_speed = random.uniform(0.2, 0.5)  # Slower pulse
        
        # Pre-generate cloud surface for performance
        self.surface = None
        self.last_generated_time = -999

    def update(self, dt, scroll_direction):
        # Drift slower than stars (lazy drift)
        drift = self.drift_speed * dt
        
        if scroll_direction == 0:  # Left
            self.x -= drift
            if self.x < -self.size * 1.5:
                self.x = constants.SCREEN_WIDTH + self.size * 1.5
                self.y = random.uniform(0, constants.SCREEN_HEIGHT)
        elif scroll_direction == 1:  # Down
            self.y += drift
            if self.y > constants.SCREEN_HEIGHT + self.size * 1.5:
                self.y = -self.size * 1.5
                self.x = random.uniform(0, constants.SCREEN_WIDTH)
        elif scroll_direction == 2:  # Right
            self.x += drift
            if self.x > constants.SCREEN_WIDTH + self.size * 1.5:
                self.x = -self.size * 1.5
                self.y = random.uniform(0, constants.SCREEN_HEIGHT)
        elif scroll_direction == 3:  # Up
            self.y -= drift
            if self.y < -self.size * 1.5:
                self.y = constants.SCREEN_HEIGHT + self.size * 1.5
                self.x = random.uniform(0, constants.SCREEN_WIDTH)
    
    def generate_surface(self, time):
        """Generate nebula surface using noise and overlapping circles"""
        surf_size = int(self.size * 3)
        surf = pygame.Surface((surf_size, surf_size), pygame.SRCALPHA)
        
        scale = 0.03  # Larger, more spread out clouds
        
        # Pulsing effect (subtle)
        pulse = 0.85 + 0.15 * math.sin(time * self.pulse_speed + self.time_offset)
        
        center_x = surf_size // 2
        center_y = surf_size // 2
        
        # Draw base cloud using noise-based circles
        num_blobs = 8  # Number of blob circles to create organic shape
        for blob in range(num_blobs):
            # Use noise to determine blob position and size
            angle = (360 / num_blobs) * blob + time * 10
            noise_x = pnoise2(blob * 0.5 + self.noise_offset_x, time * 0.1, octaves=2) * self.size * 0.4
            noise_y = pnoise2(blob * 0.5 + self.noise_offset_y, time * 0.1 + 100, octaves=2) * self.size * 0.4
            
            blob_x = center_x + noise_x
            blob_y = center_y + noise_y
            blob_radius = self.size * random.uniform(0.4, 0.7) * pulse
            
            # Layer 1: Outer glow (primary color)
            for layer_i in range(3):
                if layer_i == 0:
                    color = self.color
                    layer_alpha = int(self.alpha * 0.3)
                    layer_radius = blob_radius * 1.2
                elif layer_i == 1:
                    color = self.secondary_color
                    layer_alpha = int(self.alpha * 0.5)
                    layer_radius = blob_radius * 0.9
                else:
                    # Mix colors
                    color = tuple((c1 + c2) // 2 for c1, c2 in zip(self.color, self.secondary_color))
                    layer_alpha = int(self.alpha * 0.7)
                    layer_radius = blob_radius * 0.6
                
                pygame.draw.circle(surf, (*color, layer_alpha), 
                                 (int(blob_x), int(blob_y)), int(layer_radius))
        
        return surf


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
        # Draw nebulae with noise-based rendering
        for nebula in self.nebulae:
            # Regenerate surface every 2 seconds for subtle animation
            if nebula.surface is None or (self.time - nebula.last_generated_time) > 2.0:
                nebula.surface = nebula.generate_surface(self.time)
                nebula.last_generated_time = self.time
            
            # Blit the pre-generated surface
            if nebula.surface:
                surf_size = nebula.surface.get_width()
                screen.blit(nebula.surface, (int(nebula.x - surf_size // 2), int(nebula.y - surf_size // 2)))

        # Draw stars
        for star in self.stars:
            twinkle = abs(math.sin(self.time * star.twinkle_speed + star.twinkle_offset))
            alpha = int(star.alpha * (0.3 + 0.7 * twinkle))
            color = (255, 255, 255, alpha)
            
            surf = pygame.Surface((int(star.size * 2), int(star.size * 2)), pygame.SRCALPHA)
            pygame.draw.circle(surf, color, (int(star.size), int(star.size)), star.size)
            screen.blit(surf, (int(star.x - star.size), int(star.y - star.size)))
