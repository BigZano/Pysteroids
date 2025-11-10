SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
STARTING_SCORE = 0

def set_resolution(width, height):
    """Update screen resolution and dependent constants"""
    global SCREEN_WIDTH, SCREEN_HEIGHT
    global RING_CHARGE_1_RADIUS, RING_CHARGE_2_RADIUS, RING_CHARGE_3_RADIUS
    
    SCREEN_WIDTH = width
    SCREEN_HEIGHT = height
    
    # Update resolution-dependent constants
    RING_CHARGE_1_RADIUS = SCREEN_WIDTH / 8 * 2  # 1/4th screen (2x)
    RING_CHARGE_2_RADIUS = SCREEN_WIDTH / 6 * 2  # 1/3rd screen (2x)
    RING_CHARGE_3_RADIUS = SCREEN_WIDTH / 4 * 2  # 1/2 screen (2x)

PLAYER_RADIUS = 20
PLAYER_TURN_SPEED = 300
PLAYER_ACCELERATION = 200
PLAYER_MAX_SPEED = 300
PLAYER_LIVES = 3
BONUS_PLAYER_LIFE_SCORE = 10000

ASTEROID_MIN_RADIUS = 20
ASTEROID_KINDS = 3
ASTEROID_SPAWN_RATE = 1  # seconds
ASTEROID_MAX_RADIUS = ASTEROID_MIN_RADIUS * ASTEROID_KINDS
ASTEROID_KILL_SCORE = 100
SMALL_ASTEROID_SCORE = 500


SHOT_RADIUS = 5
PLAYER_SHOT_SPEED = 500
PLAYER_SHOT_COOLDOWN = 0.2
PLAYER_SHOT_COOLDOWN_DEFAULT = PLAYER_SHOT_COOLDOWN
RAPID_FIRE_COOLDOWN = 0.1
POWERUP_DURATION = 10.0
POWERUP_DRIFT_DURATION = 3.0  # Time powerup drifts across screen before disappearing
SPREAD_BULLETS = 5
SPREAD_ANGLE_DEG = 15
POWER_UP_DROP_CHANCE = 0.07
POWERUP_RADIUS = 15 

SCORE_FONT_SIZE = 24

# Boss asteroid settings
BOSS_SPAWN_SCORE = 25000
BOSS_RADIUS = ASTEROID_MAX_RADIUS * 1.5 * 1.5  # 1.5x larger again (2.25x total)
BOSS_STARTING_HP = 100
BOSS_SPEED = 56  # 80% of asteroid speed (70 * 0.8 = 56, asteroids are 40-100 speed)
BOSS_ASTEROID_SPAWN_MODIFIER = 0.75  # 75% spawn rate while boss alive
BOSS_LIVES_REWARD = 2
ICE_TRAIL_DURATION = 4.0
ICE_TRAIL_DAMAGE_COOLDOWN = 0.5  # Damage player every 0.5s while touching

# Dash settings
DASH_SPEED = 800
DASH_DURATION = 0.15
DASH_COOLDOWN = 10.0
DASH_INVINCIBILITY = True  # Player is invincible during dash

# Ring blast settings
RING_CHARGE_SCORE = 15000
RING_BLAST_COOLDOWN = 3.0  # Cooldown between ring blasts
RING_CHARGE_1_RADIUS = SCREEN_WIDTH / 8 * 2  # 1/4th screen (2x)
RING_CHARGE_2_RADIUS = SCREEN_WIDTH / 6 * 2  # 1/3rd screen (2x)
RING_CHARGE_3_RADIUS = SCREEN_WIDTH / 4 * 2  # 1/2 screen (2x)
RING_CHARGE_1_BOSS_DAMAGE = 20
RING_CHARGE_2_BOSS_DAMAGE = 60
RING_CHARGE_3_BOSS_DAMAGE = 100
RING_EXPANSION_SPEED = 1500  # pixels per second

# Shield settings
SHIELD_MAX_HITS = 3
SHIELD_COOLDOWN = 30.0  # 30 second recharge
SHIELD_DURATION = 999999  # Effectively infinite until hits depleted

# Stealth settings
STEALTH_DURATION = 5.0  # 5 seconds of invisibility
STEALTH_COOLDOWN = 20.0  # 20 second recharge

# Weird shot settings
WEIRD_SHOT_RADIUS = 30  # Smaller than full ring blast
WEIRD_SHOT_SPEED = 300  # Speed it travels across screen
WEIRD_SHOT_EXPANSION_SPEED = 200  # How fast it expands
WEIRD_SHOT_MAX_RADIUS = 60  # Maximum size
WEIRD_SHOT_COOLDOWN = 2.0  # 2 second cooldown



# Ship unlocks
SHIP_UNLOCKS = {
    "default": 0,
    "fast git": 50000,
    "big git": 100000,
    "sneaky git": 200000,
    "weird boy": 300000
}


# ship stats
SHIP_STATS = {
    "default": {
        "turn_speed": PLAYER_TURN_SPEED,
        "acceleration": PLAYER_ACCELERATION,
        "max_speed": PLAYER_MAX_SPEED,
        "shot_speed": PLAYER_SHOT_SPEED,
        "color": (255, 255, 255),
        "shape": "triangle"
    },
    "fast git": {
        "turn_speed": PLAYER_TURN_SPEED * 1.3,
        "acceleration": PLAYER_ACCELERATION * 1.5,
        "max_speed": PLAYER_MAX_SPEED * 1.4,
        "shot_speed": PLAYER_SHOT_SPEED,
        "color": (255, 100, 100),
        "shape": "arrow"
    },
    "big git": {
        "acceleration": PLAYER_ACCELERATION * 0.8,
        "max_speed": PLAYER_MAX_SPEED * 0.9,
        "turn_speed": PLAYER_TURN_SPEED * 0.9,
        "shot_speed": PLAYER_SHOT_SPEED * 1.2,
        "fire_rate": PLAYER_SHOT_COOLDOWN * 1.2,
        "color": (100, 200, 255),
        "shape": "diamond",
        "special_ability": "shield"  # F key activates shield
    },
    "sneaky git": {
        "acceleration": PLAYER_ACCELERATION * 1.2,
        "max_speed": PLAYER_MAX_SPEED * 1.3,
        "turn_speed": PLAYER_TURN_SPEED * 1.1,
        "shot_speed": PLAYER_SHOT_SPEED,
        "fire_rate": PLAYER_SHOT_COOLDOWN,
        "color": (150, 150, 255),
        "shape": "needle",
        "special_ability": "stealth"  # F key activates stealth
    },
    "weird boy": {
        "acceleration": PLAYER_ACCELERATION,
        "max_speed": PLAYER_MAX_SPEED,
        "turn_speed": PLAYER_TURN_SPEED,
        "shot_speed": PLAYER_SHOT_SPEED * 0.8,
        "fire_rate": PLAYER_SHOT_COOLDOWN,
        "color": (255, 150, 255),
        "shape": "star",
        "special_ability": "weird_shot",  # Uses weird nova shots
        "shot_type": "weird"  # Custom shot type
    }
}