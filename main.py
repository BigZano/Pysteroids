import pygame
from constants import *
from player import Player
pygame.init()

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

        player.update(dt)
        screen.fill((0, 0, 0)) # screen background color
        player.draw(screen) # draw player
        pygame.display.flip()  #update display  

        dt = clock.tick(60) / 1000   # Limit to 60 FPS and get delta time in seconds

if __name__ == "__main__":
    main()