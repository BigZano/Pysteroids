from circleshape import *
from constants import *


class Shot(CircleShape):
    def __init__(self, x, y):
        super().__init__(x, y, SHOT_RADIUS)

    def draw(self, screen):
        pygame.draw.circle(screen, (255, 0, 0), (int(self.position.x), int(self.position.y)), self.radius)

    def update(self, dt):
        self.position += self.velocity * dt


class WeirdShot(CircleShape):
    """Nova ring shot that travels across screen - exclusive to weird boy ship"""
    def __init__(self, x, y, direction):
        super().__init__(x, y, WEIRD_SHOT_RADIUS)
        self.direction = direction  # Direction vector for travel
        self.current_radius = WEIRD_SHOT_RADIUS
        self.max_radius = WEIRD_SHOT_MAX_RADIUS
        self.expansion_speed = WEIRD_SHOT_EXPANSION_SPEED
        self.travel_speed = WEIRD_SHOT_SPEED
        self.alpha = 200  # Transparency
        
    def draw(self, screen):
        # Draw expanding ring with gradient effect
        color = (255, 150, 255)  # Purple/magenta
        
        # Outer ring
        pygame.draw.circle(screen, color, 
                         (int(self.position.x), int(self.position.y)), 
                         int(self.current_radius), 3)
        
        # Inner ring for effect
        if self.current_radius > 10:
            inner_radius = int(self.current_radius * 0.7)
            inner_color = (200, 100, 200)
            pygame.draw.circle(screen, inner_color,
                             (int(self.position.x), int(self.position.y)),
                             inner_radius, 2)
    
    def update(self, dt):
        # Move in direction
        self.position += self.direction * self.travel_speed * dt
        
        # Expand ring
        if self.current_radius < self.max_radius:
            self.current_radius += self.expansion_speed * dt
            self.radius = self.current_radius
        
        # Kill if off screen
        margin = self.max_radius + 50
        if (self.position.x < -margin or self.position.x > SCREEN_WIDTH + margin or
            self.position.y < -margin or self.position.y > SCREEN_HEIGHT + margin):
            self.kill()