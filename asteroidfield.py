import pygame
import random
from asteroid import Asteroid
from constants import *


class AsteroidField(pygame.sprite.Sprite):
    edges = [
        [pygame.Vector2(1, 0), lambda y: pygame.Vector2(-ASTEROID_MAX_RADIUS, y * SCREEN_HEIGHT)],
        [pygame.Vector2(-1, 0), lambda y: pygame.Vector2(SCREEN_WIDTH + ASTEROID_MAX_RADIUS, y * SCREEN_HEIGHT)],
        [pygame.Vector2(0, 1), lambda x: pygame.Vector2(x * SCREEN_WIDTH, -ASTEROID_MAX_RADIUS)],
        [pygame.Vector2(0, -1), lambda x: pygame.Vector2(x * SCREEN_WIDTH, SCREEN_HEIGHT + ASTEROID_MAX_RADIUS)],
    ]

    def __init__(self):
        super().__init__(self.containers)
        self.spawn_timer = 0.0
        self.spawn_rate = ASTEROID_SPAWN_RATE

    def spawn(self, radius, position, velocity):
        """Create a new asteroid with given parameters"""
        try:
            # Validate parameters before creating asteroid
            if radius <= 0 or radius > ASTEROID_MAX_RADIUS * 2:
                radius = max(ASTEROID_MIN_RADIUS, min(radius, ASTEROID_MAX_RADIUS))
            
            if not position or not hasattr(position, 'x') or not hasattr(position, 'y'):
                position = pygame.Vector2(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            
            # Ensure position is within reasonable bounds (allowing off-screen spawning)
            margin = ASTEROID_MAX_RADIUS * 3
            if (position.x < -margin or position.x > SCREEN_WIDTH + margin or 
                position.y < -margin or position.y > SCREEN_HEIGHT + margin):
                # Don't spawn if position is unreasonable
                return
            
            asteroid = Asteroid(position.x, position.y, radius)
            if velocity and hasattr(velocity, 'x') and hasattr(velocity, 'y'):
                # Ensure velocity is reasonable (prevent super-fast asteroids)
                max_speed = 150  # Reasonable maximum
                if velocity.length_squared() > max_speed * max_speed:
                    velocity = velocity.normalize() * max_speed
                asteroid.velocity = velocity
            else:
                asteroid.velocity = pygame.Vector2(50, 0).rotate(random.uniform(0, 360))
                
        except Exception as e:
            raise

    def update(self, dt):
        try:
            # Validate delta time to prevent issues with large time jumps
            if dt <= 0 or dt > 1.0:  # Cap at 1 second max
                return
                
            self.spawn_timer += dt
            if self.spawn_timer > self.spawn_rate and self.spawn_rate > 0:
                self.spawn_timer = 0
                
                # Validate constants before using them
                if ASTEROID_KINDS <= 0 or ASTEROID_MIN_RADIUS <= 0:
                    return
                
                # Spawn asteroid at random edge with better error handling
                if not self.edges:
                    return
                    
                try:
                    edge = random.choice(self.edges)
                    if not edge or len(edge) < 2:
                        return
                    
                    # Generate spawn parameters with validation
                    speed = random.randint(max(20, 40), min(150, 100))  # Ensure valid range
                    angle_variation = random.randint(-45, 45)  # Slightly wider spread
                    velocity = (edge[0] * speed).rotate(angle_variation)
                    
                    # Generate position with bounds checking
                    spawn_param = random.uniform(0.1, 0.9)  # Avoid exact edges (0,1)
                    position = edge[1](spawn_param)
                    
                    # Validate generated position
                    if not position or not hasattr(position, 'x') or not hasattr(position, 'y'):
                        return
                    
                    kind = random.randint(1, max(1, ASTEROID_KINDS))  # Ensure at least 1
                    radius = ASTEROID_MIN_RADIUS * kind
                    
                    self.spawn(radius, position, velocity)
                    
                except Exception as e:
                    raise
                    
        except Exception as e:
            raise