import pygame
from circleshape import *
from constants import *
from shot import Shot

class Player(CircleShape):
    def __init__(self, x, y):
        super().__init__(x, y, PLAYER_RADIUS)
        self.rotation = 0
        self.shot_timer = 0
        self.powerups = {"rapid_fire": 0.0, "spread": 0.0} # initialize timers for powerups
        self.base_fire_delay = PLAYER_SHOT_COOLDOWN_DEFAULT


    def rotate(self, dt):
        self.rotation = (PLAYER_TURN_SPEED * dt) + self.rotation
        self.rotation %= 360.0

    def add_powerup(self, kind):
        if kind in self.powerups:
            self.powerups[kind] = POWERUP_DURATION
    
    def current_fire_delay(self):
        return RAPID_FIRE_COOLDOWN if self.powerups["rapid_fire"] > 0.0 else self.base_fire_delay

    def update(self, dt):
        keys = pygame.key.get_pressed()
        self.shot_timer += dt

        # update power-up timers
        for p in self.powerups:
            self.powerups[p] = max(0.0, self.powerups[p] - dt)

        if keys[pygame.K_w]:
            self.move(dt)
        if keys[pygame.K_s]:
            self.move(dt * -1)
        if keys[pygame.K_a]:
            self.rotate(dt * -1)
        if keys[pygame.K_d]:
            self.rotate(dt)
        if keys[pygame.K_SPACE] and self.shot_timer >= self.current_fire_delay():
            self.shoot()
            self.shot_timer = 0

    def move(self, dt):
        forward = pygame.Vector2(0, 1).rotate(self.rotation)  #Spooky magic bullshit
        self.position += forward * PLAYER_ACCELERATION * dt   # accelerate!


    # in the player class
    def triangle(self):
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        right = pygame.Vector2(0, 1).rotate(self.rotation + 90) * self.radius / 1.5
        a = self.position + forward * self.radius
        b = self.position - forward * self.radius - right
        c = self.position - forward * self.radius + right
        return [a, b, c]
    

    def draw(self, screen):
        pygame.draw.polygon(screen, (255, 255, 255), self.triangle(), 2)

    
    def shoot(self):
        # shoot straight forward by default
        center_angle = self.rotation
        angles = [center_angle]

        # spread 'em
        if self.powerups["spread"] > 0.0 and SPREAD_BULLETS >= 3:
            half = (SPREAD_BULLETS - 1) // 2
            offsets = [i * SPREAD_ANGLE_DEG for i in range(-half, half + 1)]
            angles = [center_angle + off for off in offsets]

        for ang in angles:
            forward = pygame.Vector2(0, 1).rotate(ang)
            position = self.position + forward * self.radius
            velocity = forward * PLAYER_SHOT_SPEED
            shot = Shot(position.x, position.y)
            shot.velocity = velocity
        return None