import pygame
from constants import *
from player import Player
from asteroid import Asteroid
from asteroidfield import AsteroidField
from circleshape import *
from shot import Shot
from background import Background
from menu import Menu
from pygame import mixer
from powerup import PowerUp

pygame.init()
mixer.init()

background_music = [
    "assets/ogg/Sci-Fi 1 Loop.ogg",
    "assets/ogg/Sci-Fi 2 Loop.ogg",
    "assets/ogg/Sci-Fi 3 Loop.ogg",
    "assets/ogg/Sci-Fi 4 Loop.ogg",
    "assets/ogg/Sci-Fi 5 Loop.ogg",
    "assets/ogg/Sci-Fi 6 Loop.ogg",
    "assets/ogg/Sci-Fi 7 Loop.ogg",
    "assets/ogg/Sci-Fi 8 Loop.ogg",
]
background_playlist = list(background_music)

MUSIC_END = pygame.USEREVENT + 1
pygame.mixer.music.set_endevent(MUSIC_END)

def play_next(loop=False):
    global background_playlist
    if not background_playlist:
        if loop:
            background_playlist = list(background_music)
        else:
            return
    next_track = background_playlist.pop(0)
    try:
        pygame.mixer.music.load(next_track)
        pygame.mixer.music.play(0, 0.0, 500) # play with fade in, set loop with play next func
        pygame.mixer.music.set_volume(0.7) # volume
    except pygame.error as e:
        print(f"Warning: unable to load music '{next_track}': {e}")

play_next(loop=True) # starts music loop with assets

asteroids = pygame.sprite.Group()
updatable = pygame.sprite.Group()
drawable = pygame.sprite.Group()
powerups = pygame.sprite.Group()
Player.containers = updatable, drawable
Asteroid.containers = (asteroids, updatable, drawable)
AsteroidField.containers = (updatable)
bullets = pygame.sprite.Group()
Shot.containers = (bullets, updatable, drawable)
PowerUp.containers = (powerups, updatable, drawable)


def reset_game():
    """reset game state"""
    asteroids.empty()
    updatable.empty()
    drawable.empty()
    bullets.empty()
    powerups.empty()

try:
    click_sound = pygame.mixer.Sound("assets/game_start.mp3")
except pygame.error as e:
    click_sound = None
    print(f"Warning: unable to load click sound: {e}")

def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Asteroids")

    menu = Menu(screen, click_sound)
    clock = pygame.time.Clock()

    # Main game loop - restarts when returning from menu
    game_running = True
    while game_running:
        # Show initial menu
        menu.show_initial_menu()

        # Reset everything for new game
        reset_game()

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

        dt = 0.0
        invincible_timer = 0.0

        playing = True
        while playing:  # Gameplay loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    playing = False
                    game_running = False
                elif event.type == MUSIC_END:
                    play_next(loop=True)

            keys = pygame.key.get_pressed()
            if keys[pygame.K_ESCAPE]:
                menu.show_pause_menu()

            updatable.update(dt)
            for pu in list(powerups):
                if player.crash_check(pu):
                    player.add_powerup(pu.kind)
                    pu.kill()
            
            background.update(dt)

            # Respawn invincibility timer
            invincible_timer = max(0.0, invincible_timer - dt)

            # Player vs asteroid collisions if not invincible
            if invincible_timer <= 0.0:
                for asteroid in asteroids:
                    if player.crash_check(asteroid):
                        lives_left = player.lives - 1
                        if lives_left < 0:
                            menu.show_game_over_menu()
                            playing = False  # Exit to restart
                            break
                        else:
                            # Respawn in center with remaining lives and invincibility
                            player.kill()
                            player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
                            player.lives = lives_left
                            invincible_timer = 1.5
                        break

            # Bullet hits -> score and split asteroid
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

            # Flicker player while invincible
            blink_on = True
            if invincible_timer > 0.0:
                blink_period_ms = 120
                blink_on = ((pygame.time.get_ticks() // blink_period_ms) % 2) == 0

            for obj in drawable:
                if obj is player and invincible_timer > 0.0 and not blink_on:
                    continue
                obj.draw(screen)

            # Halo around player while invincible
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
                    pygame.draw.circle(halo_surf, (180, 140, 255, 60), (center, center), int(r * 1.6), 2)
                    pygame.draw.circle(halo_surf, (180, 140, 255, 30), (center, center), int(r * 1.1), 0)
                    screen.blit(halo_surf, (px - center, py - center))

            # HUD
            score_surf = font.render(f"Score: {score}", True, (200, 200, 220))
            lives_surf = font.render(f"Lives: {player.lives}", True, (200, 200, 220))
            screen.blit(score_surf, (10, 10))
            screen.blit(lives_surf, (10, 10 + score_surf.get_height() + 4))

            pygame.display.flip()
            dt = clock.tick(60) / 1000.0

    pygame.quit()


if __name__ == "__main__":
    main()