import pygame
from constants import *
from player import Player
from asteroid import Asteroid
from asteroidfield import AsteroidField
from circleshape import *
from shot import Shot
from background import Background
from menu import Menu


pygame.init()


asteroids = pygame.sprite.Group()
updatable = pygame.sprite.Group()
drawable = pygame.sprite.Group()
Player.containers = updatable, drawable
Asteroid.containers = (asteroids, updatable, drawable)
AsteroidField.containers = (updatable)
bullets = pygame.sprite.Group()
Shot.containers = (bullets, updatable, drawable)



def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Asteroids")

    menu = Menu(screen)
    menu.show_main_menu()

    print(f"""Starting Asteroids!
          Screen width: {SCREEN_WIDTH}
          Screen height: {SCREEN_HEIGHT}""")

    # Create game objects
    asteroid_field = AsteroidField()
    player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    player.lives = PLAYER_LIVES
    background = Background()

    # HUD
    font = pygame.font.Font(None, SCORE_FONT_SIZE)
    score = STARTING_SCORE
    next_bonus = BONUS_PLAYER_LIFE_SCORE

    clock = pygame.time.Clock()
    dt = 0.0
    invincible_timer = 0.0  

    running = True
    while running:                          # main game loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False


            keys = pygame.key.get_pressed()
            if keys[pygame.K_ESCAPE]:
                menu.show_main_menu()

        updatable.update(dt)
        background.update(dt)

        # respawn invincibility timer
        invincible_timer = max(0.0, invincible_timer - dt)

        # player vs asteroid collisions if not invincible
        if invincible_timer <= 0.0:
            for asteroid in asteroids:
                if player.crash_check(asteroid):
                    lives_left = player.lives - 1
                    if lives_left < 0:
                        menu.show_game_over_menu()
                        break                        
                    else:
                        # Respawn in center with remaining lives and 2s invincibility
                        player.kill()
                        player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
                        player.lives = lives_left
                        invincible_timer = 1.5 # seconds
                    break
        if not running:
            break

        # Bullet hits -> score and split asteroid; award bonus lives at thresholds
        for bullet in list(bullets):
            hit = False
            for asteroid in list(asteroids):
                if bullet.crash_check(asteroid):
                    bullet.kill()
                    radius = getattr(asteroid, "radius", ASTEROID_MIN_RADIUS)
                    if radius <= ASTEROID_MIN_RADIUS:
                        score += SMALL_ASTEROID_SCORE
                    else:
                        score += ASTEROID_KILL_SCORE
                    asteroid.split()
                    hit = True
                    break
            if hit:
                # Bonus lives on score thresholds
                while score >= next_bonus:
                    player.lives += 1
                    next_bonus += BONUS_PLAYER_LIFE_SCORE

        screen.fill((0, 0, 0))
        background.draw(screen)

        # Flicker the player while invincible
        blink_on = True
        if invincible_timer > 0.0:
            blink_period_ms = 120  # ~8 Hz
            blink_on = ((pygame.time.get_ticks() // blink_period_ms) % 2) == 0

        for obj in drawable:
            if obj is player and invincible_timer > 0.0 and not blink_on:
                continue
            obj.draw(screen)

        # halo around player while invincible
        if invincible_timer > 0.0:
            px = py = None
            if hasattr(player, "position"):
                px, py = int(player.position.x), int(player.position.y)
            elif hasattr(player, "x") and hasattr(player, "y"):
                px, py = int(player.x), int(player.y)

            if px is not None:
                r = int(getattr(player, "radius", PLAYER_RADIUS))
                halo_size = r * 4
                halo_surf = pygame.Surface((halo_size, halo_size), pygame.SRCALPHA)
                center = halo_size // 2
                # Soft purple halo to match background palette
                pygame.draw.circle(halo_surf, (180, 140, 255, 60), (center, center), int(r * 1.6), 2)
                pygame.draw.circle(halo_surf, (180, 140, 255, 30), (center, center), int(r * 1.1), 0)
                screen.blit(halo_surf, (px - center, py - center))

        # HUD
        score_surf = font.render(f"Score: {score}", True, (200, 200, 220))
        lives_surf = font.render(f"Lives: {player.lives}", True, (200, 200, 220))
        screen.blit(score_surf, (10, 10))
        screen.blit(lives_surf, (10, 10 + score_surf.get_height() + 4))

        pygame.display.flip()
        dt = clock.tick(60) / 1000.0   # Limit to 60 FPS and get delta time in seconds

if __name__ == "__main__":
    main()