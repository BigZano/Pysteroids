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
        """Update star position with parallax scrolling"""
        scroll_speed = 15 * self.layer
        
        # Direction-based scrolling with wrapping
        directions = [
            (-scroll_speed, 0, -10, constants.SCREEN_WIDTH + 10, 'x', 'y'),  # Left
            (0, scroll_speed, constants.SCREEN_HEIGHT + 10, -10, 'y', 'x'),  # Down
            (scroll_speed, 0, constants.SCREEN_WIDTH + 10, -10, 'x', 'y'),   # Right
            (0, -scroll_speed, -10, constants.SCREEN_HEIGHT + 10, 'y', 'x')  # Up
        ]
        
        if 0 <= scroll_direction < 4:
            dx, dy, edge_check, wrap_pos, primary_axis, secondary_axis = directions[scroll_direction]
            self.x += dx * dt
            self.y += dy * dt
            
            # Wrap around screen
            if (dx < 0 and self.x < -10) or (dx > 0 and self.x > constants.SCREEN_WIDTH + 10):
                self.x = wrap_pos
                self.y = random.uniform(0, constants.SCREEN_HEIGHT)
            elif (dy < 0 and self.y < -10) or (dy > 0 and self.y > constants.SCREEN_HEIGHT + 10):
                self.y = wrap_pos
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
        """Update nebula position with lazy drift"""
        drift = self.drift_speed * dt
        buffer = self.size
        
        # Direction-based drift with wrapping
        if scroll_direction == 0:  # Left
            self.x -= drift
            if self.x < -buffer:
                self.x = constants.SCREEN_WIDTH + buffer
                self.y = random.uniform(0, constants.SCREEN_HEIGHT)
        elif scroll_direction == 1:  # Down
            self.y += drift
            if self.y > constants.SCREEN_HEIGHT + buffer:
                self.y = -buffer
                self.x = random.uniform(0, constants.SCREEN_WIDTH)
        elif scroll_direction == 2:  # Right
            self.x += drift
            if self.x > constants.SCREEN_WIDTH + buffer:
                self.x = -buffer
                self.y = random.uniform(0, constants.SCREEN_HEIGHT)
        elif scroll_direction == 3:  # Up
            self.y -= drift
            if self.y < -buffer:
                self.y = constants.SCREEN_HEIGHT + buffer
                self.x = random.uniform(0, constants.SCREEN_WIDTH)
    
    def generate_surface(self, time):
        """Generate nebula surface using noise and overlapping circles"""
        surf_size = int(self.size * 3)
        surf = pygame.Surface((surf_size, surf_size), pygame.SRCALPHA)
        pulse = 0.85 + 0.15 * math.sin(time * self.pulse_speed + self.time_offset)
        center = surf_size // 2
        
        # Draw base cloud using noise-based circles
        num_blobs = 8
        for blob in range(num_blobs):
            noise_x = pnoise2(blob * 0.5 + self.noise_offset_x, time * 0.1, octaves=2) * self.size * 0.4
            noise_y = pnoise2(blob * 0.5 + self.noise_offset_y, time * 0.1 + 100, octaves=2) * self.size * 0.4
            
            blob_pos = (center + noise_x, center + noise_y)
            blob_radius = self.size * random.uniform(0.4, 0.7) * pulse
            
            # Layer colors and alphas
            layers = [
                (self.color, int(self.alpha * 0.3), blob_radius * 1.2),
                (self.secondary_color, int(self.alpha * 0.5), blob_radius * 0.9),
                (tuple((c1 + c2) // 2 for c1, c2 in zip(self.color, self.secondary_color)), 
                 int(self.alpha * 0.7), blob_radius * 0.6)
            ]
            
            for color, alpha, radius in layers:
                pygame.draw.circle(surf, (*color, alpha), (int(blob_pos[0]), int(blob_pos[1])), int(radius))
        
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
        
        self.nebulae = [NebulaCloud() for _ in range(12)]  # Increased from 5 to 12
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
