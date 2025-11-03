from circleshape import *
import random
import pygame
from constants import *
from powerup import PowerUp

class Asteroid(CircleShape):
    def __init__(self, x, y, radius):
        super().__init__(x, y, radius)
    
    def draw(self, screen):
        pygame.draw.circle(screen,(255, 255, 255),  self.position, self.radius, 2)

    def update(self, dt):
        self.position += self.velocity * dt

    def split(self):
        if random.random() < POWER_UP_DROP_CHANCE:
            kind = random.choice(["rapid_fire", "spread"])
            if self.velocity.length_squared() > 0:
                dir_vec = self.velocity.normalize()
            else:
                dir_vec = pygame.Vector2(1, 0).rotate(random.uniform(0, 360))
            speed = 80.0
            vel = dir_vec * speed
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



    