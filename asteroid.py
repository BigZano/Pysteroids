from circleshape import *
import random
import pygame
import math
from constants import *
from powerup import PowerUp
from ringblast import RingChargePowerUp

class Asteroid(CircleShape):
    """Jagged asteroid with random shape and rotation"""
    sounds = {}

    def __init__(self, x, y, radius):
        super().__init__(x, y, radius)
        
        # Generate random jagged shape
        self.num_vertices = random.randint(8, 14)
        self.vertices = []
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-30, 30)
        
        # Generate vertices with random distance variations
        for i in range(self.num_vertices):
            angle = (360 / self.num_vertices) * i
            distance = radius * random.uniform(0.7, 1.0)
            rad = math.radians(angle)
            offset = pygame.Vector2(distance * math.cos(rad), distance * math.sin(rad))
            self.vertices.append(offset)
        
        # Add craters for detail
        self.craters = []
        for _ in range(random.randint(0, 3)):
            self.craters.append({
                'angle': random.uniform(0, 360),
                'distance': random.uniform(0.5, 0.8) * radius,
                'size': random.uniform(0.1, 0.2) * radius
            })
    
    def draw(self, screen):
        # Rotate vertices based on current rotation
        rotated_vertices = []
        for vertex in self.vertices:
            rotated = vertex.rotate(self.rotation)
            world_pos = self.position + rotated
            rotated_vertices.append((world_pos.x, world_pos.y))
        
        # Draw the jagged asteroid outline
        if len(rotated_vertices) >= 3:
            pygame.draw.polygon(screen, (255, 255, 255), rotated_vertices, 2)
        
        # Draw craters for detail
        for crater in self.craters:
            rad = math.radians(crater['angle'] + self.rotation)
            crater_x = self.position.x + crater['distance'] * math.cos(rad)
            crater_y = self.position.y + crater['distance'] * math.sin(rad)
            pygame.draw.circle(screen, (200, 200, 200), (int(crater_x), int(crater_y)), 
                             int(crater['size']), 1)

    def update(self, dt):
        self.position += self.velocity * dt
        self.rotation += self.rotation_speed * dt

    def split(self):
        """Split asteroid and potentially drop powerups"""
        # Play size-appropriate sound
        if self.sounds:
            sound_key = "asteroid_small" if self.radius <= ASTEROID_MIN_RADIUS else \
                       "asteroid_medium" if self.radius <= ASTEROID_MIN_RADIUS * 2 else \
                       "asteroid_large"
            sound = self.sounds.get(sound_key)
            if sound:
                sound.play()

        # Drop powerup with configured chance
        if random.random() < POWER_UP_DROP_CHANCE:
            kind = random.choice(["rapid_fire", "spread", "rapid_fire", "spread", "ring_charge"])
            
            # Calculate powerup velocity
            if self.velocity.length_squared() > 0:
                direction = self.velocity.normalize()
            else:
                direction = pygame.Vector2(1, 0).rotate(random.uniform(0, 360))
            vel = direction * 80.0
            
            # Spawn powerup
            if kind == "ring_charge":
                RingChargePowerUp(self.position.x, self.position.y, vel)
            else:
                PowerUp(self.position.x, self.position.y, kind, vel)

        self.kill()

        # Split into smaller asteroids if not minimum size
        if self.radius > ASTEROID_MIN_RADIUS:
            new_radius = self.radius - ASTEROID_MIN_RADIUS
            split_angle = random.uniform(20, 50)
            
            for angle_sign in [1, -1]:
                asteroid = Asteroid(self.position.x, self.position.y, new_radius)
                asteroid.velocity = self.velocity.rotate(split_angle * angle_sign) * 1.2



