from circleshape import *
import random
import pygame
import math
from constants import *
from powerup import PowerUp
from ringblast import RingChargePowerUp

class Asteroid(CircleShape):
    sounds = {}

    def __init__(self, x, y, radius):
        super().__init__(x, y, radius)
        
        # Generate random jagged shape
        self.num_vertices = random.randint(8, 14)  # More vertices = more detail
        self.vertices = []
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-30, 30)  # degrees per second
        
        # Generate vertices with random distance variations
        for i in range(self.num_vertices):
            angle = (360 / self.num_vertices) * i
            # Vary the distance from center (70% to 100% of radius)
            distance_variation = random.uniform(0.7, 1.0)
            distance = radius * distance_variation
            
            # Convert polar to cartesian
            rad = math.radians(angle)
            x_offset = distance * math.cos(rad)
            y_offset = distance * math.sin(rad)
            self.vertices.append(pygame.Vector2(x_offset, y_offset))
        
        # Add small craters (indentations) occasionally
        self.craters = []
        num_craters = random.randint(0, 3)
        for _ in range(num_craters):
            crater_angle = random.uniform(0, 360)
            crater_distance = random.uniform(0.5, 0.8) * radius
            crater_size = random.uniform(0.1, 0.2) * radius
            self.craters.append({
                'angle': crater_angle,
                'distance': crater_distance,
                'size': crater_size
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
        # Play sound based on size
        if self.sounds:
            if self.radius <= ASTEROID_MIN_RADIUS:
                sound = self.sounds.get("asteroid_small")
            elif self.radius <= ASTEROID_MIN_RADIUS * 2:
                sound = self.sounds.get("asteroid_medium")
            else:
                sound = self.sounds.get("asteroid_large")
            
            if sound:
                sound.play()

        # Drop power-up chance
        if random.random() < POWER_UP_DROP_CHANCE:
            # Choose powerup type (ring charges are rarer)
            powerup_types = ["rapid_fire", "spread", "rapid_fire", "spread", "ring_charge"]
            kind = random.choice(powerup_types)
            
            if self.velocity.length_squared() > 0:
                dir_vec = self.velocity.normalize()
            else:
                dir_vec = pygame.Vector2(1, 0).rotate(random.uniform(0, 360))
            speed = 80.0
            vel = dir_vec * speed
            
            # Spawn appropriate powerup type
            if kind == "ring_charge":
                RingChargePowerUp(self.position.x, self.position.y, vel)
            else:
                PowerUp(self.position.x, self.position.y, kind, vel)

        self.kill()

        if self.radius <= ASTEROID_MIN_RADIUS:
            return
        
        new_radius = self.radius - ASTEROID_MIN_RADIUS
        random_angle = random.uniform(20, 50)
        velocity1 = self.velocity.rotate(random_angle) * 1.2
        velocity2 = self.velocity.rotate(-random_angle) * 1.2

        asteroid1 = Asteroid(self.position.x, self.position.y, new_radius)
        asteroid2 = Asteroid(self.position.x, self.position.y, new_radius)
        asteroid1.velocity = velocity1
        asteroid2.velocity = velocity2



