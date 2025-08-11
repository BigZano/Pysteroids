import pygame
from constants import *

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Asteroids")

# Constants

running= True
while running:                          # main game loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0, 0, 0)) # screen background color
    player.draw(screen) # draw player
    pygame.display.flip()  #update display

    
def main():
    print(f"""Starting Asteroids!
          Screen width: {SCREEN_WIDTH}
          Screen height: {SCREEN_HEIGHT}""")

player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

if __name__ == "__main__":
    main()