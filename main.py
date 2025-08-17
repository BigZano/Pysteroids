import pygame
from constants import *
from player import Player
from asteroid import Asteroid
from asteroidfield import AsteroidField
from circleshape import *
from shot import Shot

pygame.init()


asteroids = pygame.sprite.Group()
updatable = pygame.sprite.Group()
drawable = pygame.sprite.Group()
Player.containers = updatable, drawable
Asteroid.containers = (asteroids, updatable, drawable)
AsteroidField.containers = (updatable)
asteroid_field = AsteroidField()
bullets = pygame.sprite.Group()
Shot.containers = (bullets, updatable, drawable)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Asteroids")
player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

# Constants


def main():
    print(f"""Starting Asteroids!
          Screen width: {SCREEN_WIDTH}
          Screen height: {SCREEN_HEIGHT}""")
    
    clock = pygame.time.Clock()
    dt = 0
    
    running = True
    while running:                          # main game loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        updatable.update(dt)

        for asteroid in asteroids:
            if player.crash_check(asteroid):
                print("Game Over!")
                running = False


        for bullet in bullets:
            for asteroid in asteroids:
                if bullet.crash_check(asteroid):
                    bullets.remove(bullet)
                    bullet.kill()
                    asteroid.split()
                    break

        screen.fill((0, 0, 0)) # screen background color
        for obj in drawable:
            obj.draw(screen) # draw player
        pygame.display.flip()  #update display  

        dt = clock.tick(60) / 1000   # Limit to 60 FPS and get delta time in seconds

if __name__ == "__main__":
    main()