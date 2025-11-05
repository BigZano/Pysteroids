import pygame
import math
import random
from constants import *
import constants as const
from player import Player
from asteroid import Asteroid
from asteroidfield import AsteroidField
from circleshape import *
from shot import Shot
from background import Background
from menu import Menu
from pygame import mixer
from powerup import PowerUp
from bossasteroid import BossAsteroid, IceTrail
from ringblast import RingBlast, RingChargeManager, RingChargePowerUp

pygame.init()
mixer.init()
# Set 32 channels and reserve specific ones for priority sounds
pygame.mixer.set_num_channels(32)

# Reserve dedicated channels for continuous/priority sounds
laser_channel = pygame.mixer.Channel(0)      # Laser - highest priority
music_channel = pygame.mixer.Channel(1)      # Reserved (not used, but kept free)
# Channels 2-31 available for sound effects (asteroids, power-ups, etc.)

asteroid_sounds = {}
try:
    asteroid_sounds["asteroid_large"] = pygame.mixer.Sound("assets/ogg/asteroid_large.ogg")
    asteroid_sounds["asteroid_small"] = pygame.mixer.Sound("assets/ogg/asteroid_small.ogg")
    asteroid_sounds["asteroid_medium"] = pygame.mixer.Sound("assets/ogg/asteroid_medium.ogg")
    asteroid_sounds["bossteroid"] = pygame.mixer.Sound("assets/ogg/bossteroid.ogg")
    # Set volumes
    asteroid_sounds["bossteroid"].set_volume(1.0)
    asteroid_sounds["asteroid_large"].set_volume(0.4)
    asteroid_sounds["asteroid_medium"].set_volume(0.25)
    asteroid_sounds["asteroid_small"].set_volume(0.15)
except pygame.error as e:
    print(f"Warning: unable to load asteroid sounds: {e}")

try:
    laser_sound_1 = pygame.mixer.Sound("assets/ogg/laser.ogg")
    laser_sound_1.set_volume(0.20)  # Slightly quieter so it doesn't drown out asteroids
    rapid_fire_sound = pygame.mixer.Sound("assets/ogg/rapid_fire.ogg")
    rapid_fire_sound.set_volume(0.20)
    laser_sound = laser_sound_1
    shotgun_sound = pygame.mixer.Sound("assets/ogg/shotgun.ogg")
    shotgun_sound.set_volume(0.70)
    print(f"Laser sound loaded successfully. Channel: {laser_channel}")
except pygame.error as e:
    laser_sound = None
    laser_channel = None
    print(f"Warning: unable to load laser sound: {e}")

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
            print("Refilled playlist")
        else:
            print("Playlist empty, not looping")
            return
    next_track = background_playlist.pop(0)
    print(f"Loading track: {next_track}")
    try:
        pygame.mixer.music.load(next_track)
        pygame.mixer.music.play(0, 0.0, 500) # play with fade in
        pygame.mixer.music.set_volume(0.5)  # Lower music volume so SFX are audible
        print(f"Playing: {next_track}")
    except pygame.error as e:
        print(f"Warning: unable to load music '{next_track}': {e}")

play_next(loop=True) # starts music loop with assets

asteroids = pygame.sprite.Group()
updatable = pygame.sprite.Group()
drawable = pygame.sprite.Group()
powerups = pygame.sprite.Group()
ring_charge_powerups = pygame.sprite.Group()
ice_trails = pygame.sprite.Group()
ring_blasts = pygame.sprite.Group()
boss_asteroids = pygame.sprite.Group()

Player.containers = updatable, drawable
Asteroid.containers = (asteroids, updatable, drawable)
AsteroidField.containers = (updatable)
bullets = pygame.sprite.Group()
Shot.containers = (bullets, updatable, drawable)
PowerUp.containers = (powerups, updatable, drawable)
RingChargePowerUp.containers = (ring_charge_powerups, updatable, drawable)
IceTrail.containers = (ice_trails, updatable, drawable)
RingBlast.containers = (ring_blasts, updatable, drawable)
BossAsteroid.containers = (boss_asteroids, asteroids, updatable, drawable)


def reset_game():
    """reset game state"""
    asteroids.empty()
    updatable.empty()
    drawable.empty()
    bullets.empty()
    powerups.empty()
    ring_charge_powerups.empty()
    ice_trails.empty()
    ring_blasts.empty()
    boss_asteroids.empty()

try:
    click_sound = pygame.mixer.Sound("assets/game_start.mp3")
except pygame.error as e:
    click_sound = None
    print(f"Warning: unable to load click sound: {e}")

def main():
    screen = pygame.display.set_mode((const.SCREEN_WIDTH, const.SCREEN_HEIGHT))
    pygame.display.set_caption("Asteroids")

    menu = Menu(screen, click_sound, MUSIC_END, play_next)
    clock = pygame.time.Clock()

    # Assign sounds
    Asteroid.sounds = asteroid_sounds
    BossAsteroid.sounds = asteroid_sounds
    Player.laser_sound = laser_sound
    Player.laser_channel = laser_channel
    Player.rapid_fire_sound = rapid_fire_sound
    Player.shotgun_sound = shotgun_sound
    
    # Set sound references in menu for live volume updates
    menu.set_sound_references(laser_sound, rapid_fire_sound, shotgun_sound, asteroid_sounds)
    
    # Apply initial volume settings from menu
    menu.apply_volumes(laser_sound, rapid_fire_sound, shotgun_sound, asteroid_sounds, click_sound)

    # Main game loop - restarts when returning from menu
    game_running = True
    while game_running:
        # Create initial background for menu
        initial_background = Background()
        
        # Show initial menu and get selected resolution
        selected_resolution = menu.show_initial_menu(initial_background)
        
        # Apply volume settings after returning from menu (user may have changed them)
        menu.apply_volumes(laser_sound, rapid_fire_sound, shotgun_sound, asteroid_sounds, click_sound)
        
        # Update resolution if changed
        if selected_resolution and selected_resolution != (const.SCREEN_WIDTH, const.SCREEN_HEIGHT):
            const.set_resolution(selected_resolution[0], selected_resolution[1])
            # Create new screen with updated resolution
            screen = pygame.display.set_mode((const.SCREEN_WIDTH, const.SCREEN_HEIGHT))
            menu.screen = screen  # Update menu's screen reference

        # Reset everything for new game
        reset_game()

        print(f"""Starting Asteroids!
              Screen width: {const.SCREEN_WIDTH}
              Screen height: {const.SCREEN_HEIGHT}""")

        # Create game objects
        asteroid_field = AsteroidField()
        player = Player(const.SCREEN_WIDTH // 2, const.SCREEN_HEIGHT // 2)
        player.lives = PLAYER_LIVES
        background = Background()

        # HUD
        font = pygame.font.Font(None, SCORE_FONT_SIZE)
        score = STARTING_SCORE
        next_bonus = BONUS_PLAYER_LIFE_SCORE
        lives_gained = 0  # Track total lives gained for scroll direction

        # Boss tracking
        bosses_defeated = 0
        next_boss_score = BOSS_SPAWN_SCORE
        current_boss = None
        
        # Ring blast tracking - using RingChargeManager
        ring_manager = RingChargeManager()
        next_ring_charge_score = RING_CHARGE_SCORE
        
        # Dash tracking (reset player dash state)
        player.dash_cooldown = 0.0
        player.dash_active = False

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
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        # Pause menu - pass background
                        menu.show_pause_menu(background)
                        # Apply volume settings after returning from pause menu
                        menu.apply_volumes(laser_sound, rapid_fire_sound, shotgun_sound, asteroid_sounds, click_sound)
                        # Update screen reference in case resolution changed
                        screen = menu.screen
                        # Flush the clock after unpausing to prevent time jump
                        clock.tick()  # Discard accumulated time
                        # Skip to next frame with fresh dt
                        continue
                    elif event.key == pygame.K_r:
                        # Fire ring blast if we have charges
                        charge_level = ring_manager.use_charges()
                        if charge_level > 0:
                            RingBlast(player.position.x, player.position.y, charge_level)
                            next_ring_charge_score = score + RING_CHARGE_SCORE
                    elif event.key == pygame.K_LSHIFT:
                        # Activate dash if available
                        if player.dash_cooldown <= 0.0 and not player.dash_active:
                            player.dash_active = True
                            player.dash_timer = DASH_DURATION
                            player.dash_cooldown = DASH_COOLDOWN
                            # Dash in the direction the ship is facing (forward)
                            player.dash_direction = pygame.Vector2(0, 1).rotate(player.rotation)

            keys = pygame.key.get_pressed()
            
            # Boss spawning
            if score >= next_boss_score and len(boss_asteroids) == 0:
                current_boss = BossAsteroid(bosses_defeated)
                next_boss_score += BOSS_SPAWN_SCORE
                # Play boss spawn sound
                if asteroid_sounds.get("bossteroid"):
                    asteroid_sounds["bossteroid"].play()
                # Modify asteroid spawn rate while boss is active
                asteroid_field.spawn_rate = asteroid_field.spawn_rate * BOSS_ASTEROID_SPAWN_MODIFIER
            
            # Check if boss is defeated
            if current_boss is not None and current_boss not in boss_asteroids:
                # Boss was defeated
                bosses_defeated += 1
                player.lives += BOSS_LIVES_REWARD
                lives_gained += BOSS_LIVES_REWARD
                background.set_scroll_direction(lives_gained)
                # Restore normal asteroid spawn rate
                asteroid_field.spawn_rate = asteroid_field.spawn_rate / BOSS_ASTEROID_SPAWN_MODIFIER
                current_boss = None
            
            # Ring charge accumulation - drop ring charge powerups at score thresholds
            while score >= next_ring_charge_score:
                # Drop a ring charge powerup at player position
                angle = random.uniform(0, 360)
                dir_vec = pygame.Vector2(1, 0).rotate(angle)
                speed = 100.0
                vel = dir_vec * speed
                RingChargePowerUp(player.position.x, player.position.y, vel)
                next_ring_charge_score += RING_CHARGE_SCORE
            
            updatable.update(dt)
            
            # Handle regular powerup collection
            for pu in list(powerups):
                if player.crash_check(pu):
                    player.add_powerup(pu.kind)
                    pu.kill()
            
            # Handle ring charge powerup collection
            for rc in list(ring_charge_powerups):
                if player.crash_check(rc):
                    ring_manager.add_charge()
                    rc.kill()
            
            background.update(dt)

            # Respawn invincibility timer
            invincible_timer = max(0.0, invincible_timer - dt)

            # Player vs asteroid collisions if not invincible and not dash-invincible
            is_dash_invincible = player.is_invincible_dash() if hasattr(player, 'is_invincible_dash') else False
            if invincible_timer <= 0.0 and not is_dash_invincible:
                for asteroid in asteroids:
                    if player.crash_check(asteroid):
                        lives_left = player.lives - 1
                        if lives_left < 0:
                            menu.show_game_over_menu(background)
                            # Apply volume settings after game over
                            menu.apply_volumes(laser_sound, rapid_fire_sound, shotgun_sound, asteroid_sounds, click_sound)
                            # Update screen reference in case resolution changed
                            screen = menu.screen
                            playing = False  # Exit to restart
                            break
                        else:
                            # Respawn in center with remaining lives and invincibility
                            player.kill()
                            player = Player(const.SCREEN_WIDTH // 2, const.SCREEN_HEIGHT // 2)
                            player.lives = lives_left
                            # Reassign class-level sound references
                            Player.laser_sound = laser_sound
                            Player.laser_channel = laser_channel
                            Player.rapid_fire_sound = rapid_fire_sound
                            Player.shotgun_sound = shotgun_sound
                            invincible_timer = 1.5
                            # Reset ring charges on death
                            ring_manager.reset()
                            next_ring_charge_score = score + RING_CHARGE_SCORE
                        break
                
                # Ice trail damage
                for trail in ice_trails:
                    if player.crash_check(trail) and trail.can_damage():
                        lives_left = player.lives - 1
                        if lives_left < 0:
                            menu.show_game_over_menu(background)
                            # Apply volume settings after game over
                            menu.apply_volumes(laser_sound, rapid_fire_sound, shotgun_sound, asteroid_sounds, click_sound)
                            # Update screen reference in case resolution changed
                            screen = menu.screen
                            playing = False
                            break
                        else:
                            player.kill()
                            player = Player(const.SCREEN_WIDTH // 2, const.SCREEN_HEIGHT // 2)
                            player.lives = lives_left
                            # Reassign class-level sound references
                            Player.laser_sound = laser_sound
                            Player.laser_channel = laser_channel
                            Player.rapid_fire_sound = rapid_fire_sound
                            Player.shotgun_sound = shotgun_sound
                            invincible_timer = 1.5
                            # Reset ring charges on death
                            ring_manager.reset()
                            next_ring_charge_score = score + RING_CHARGE_SCORE
                        break

            # Bullet hits -> score and split asteroid
            for bullet in list(bullets):
                hit = False
                for asteroid in list(asteroids):
                    if bullet.crash_check(asteroid):
                        bullet.kill()
                        # Check if it's a boss
                        if asteroid in boss_asteroids:
                            asteroid.take_damage(1)
                            hit = True
                            break
                        else:
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
                        lives_gained += 1  # Track lives gained
                        background.set_scroll_direction(lives_gained)  # Update scroll direction
                        next_bonus += BONUS_PLAYER_LIFE_SCORE
            
            # Ring blast collisions
            for ring in ring_blasts:
                # Damage asteroids
                for asteroid in list(asteroids):
                    if ring.crash_check(asteroid) and not ring.has_hit(asteroid):
                        ring.mark_hit(asteroid)
                        # Check if it's a boss
                        if asteroid in boss_asteroids:
                            asteroid.take_damage(ring.boss_damage)
                        else:
                            # Regular asteroids are destroyed instantly
                            radius = getattr(asteroid, "radius", ASTEROID_MIN_RADIUS)
                            if radius <= ASTEROID_MIN_RADIUS:
                                score += SMALL_ASTEROID_SCORE
                            else:
                                score += ASTEROID_KILL_SCORE
                            asteroid.split()
                            
                            # Bonus lives on score thresholds
                            while score >= next_bonus:
                                player.lives += 1
                                lives_gained += 1
                                background.set_scroll_direction(lives_gained)
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
            
            # Dash cooldown indicator
            if player.dash_cooldown > 0:
                dash_text = f"Dash: {player.dash_cooldown:.1f}s"
                dash_color = (150, 150, 150)
            else:
                dash_text = "Dash: READY"
                dash_color = (100, 255, 100)
            dash_surf = font.render(dash_text, True, dash_color)
            screen.blit(dash_surf, (10, 10 + score_surf.get_height() + lives_surf.get_height() + 8))
            
            # Ring charge indicator
            current_charges = ring_manager.get_charges()
            ring_color = (100, 150, 255) if current_charges == 1 else (255, 100, 100) if current_charges == 2 else (255, 255, 100) if current_charges == 3 else (150, 150, 150)
            ring_text = f"Ring: {current_charges}/3"
            ring_surf = font.render(ring_text, True, ring_color)
            screen.blit(ring_surf, (10, 10 + score_surf.get_height() + lives_surf.get_height() + dash_surf.get_height() + 12))
            
            # Boss HP bar at top center
            if current_boss is not None and current_boss in boss_asteroids:
                bar_width = 300
                bar_height = 20
                bar_x = const.SCREEN_WIDTH // 2 - bar_width // 2
                bar_y = 10
                
                # Background
                pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
                
                # HP bar
                hp_percentage = current_boss.hp / current_boss.max_hp
                pygame.draw.rect(screen, (255, 50, 50), (bar_x, bar_y, bar_width * hp_percentage, bar_height))
                
                # Border
                pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 2)
                
                # Text
                boss_text = f"BOSS: {current_boss.hp}/{current_boss.max_hp} HP"
                boss_surf = font.render(boss_text, True, (255, 255, 255))
                text_x = const.SCREEN_WIDTH // 2 - boss_surf.get_width() // 2
                text_y = bar_y + bar_height + 4
                screen.blit(boss_surf, (text_x, text_y))

            pygame.display.flip()
            dt = clock.tick(60) / 1000.0
            # Cap dt to prevent huge jumps after pause or lag
            dt = min(dt, 0.1)  # Max 100ms per frame

    pygame.quit()


if __name__ == "__main__":
    main()