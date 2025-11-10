# PYSTEROIDS

A modern take on the classic Asteroids arcade game, built with Python and Pygame!

## 🌟 Features

- **Dynamic Boss Battles**: Face increasingly powerful boss asteroids with escalating health
- **Power-up System**: Collect rapid-fire, spread shot, and ring charge power-ups
- **Dash Mechanics**: Execute invincible dashes to dodge danger
- **Ring Blast**: Unleash devastating area attacks with ice, fire, and lightning effects
- **Procedural Backgrounds**: Beautiful scrolling space nebulae and twinkling stars
- **Progressive Difficulty**: Asteroids spawn faster as you progress
- **Multiple Resolutions**: Play in 720p or 1080p

## How to Play

### Controls
- **WASD**: Move your ship
- **Mouse/Click** or **Space**: Aim and fire
- **Left Shift**: Dash (10s cooldown, grants brief invincibility)
- **R**: Ring Blast (requires charges)
- **ESC**: Pause game

### Tips
- Collect power-ups for rapid fire and shotgun modes
- Ring charges drop at score milestones
- Dash through asteroids and ice trails when in danger
- Boss asteroids reward you with extra lives when defeated
- Small asteroids are worth more points!

## Scoring

- **Small Asteroid**: 500 points
- **Medium/Large Asteroid**: 100 points
- **Bonus Life**: Every 10,000 points
- **Boss Defeated**: 2 extra lives + powerups

## Power-ups

- **Rapid Fire** (Red): Faster shot cooldown for 3 seconds
- **Spread Shot** (Blue): Fire 5 bullets in a spread pattern for 3 seconds
- **Ring Charge** (Gold): Adds a ring blast charge (max 3)

## Audio

- Dynamic background music
- Sound effects for shots, asteroid destruction, and boss battles
- Volume controls in settings menu

## System Requirements

### Minimum
- *My brother it will run on a potato if it has python*

### Recommended
- *It is recommended that you play with a monitor and computer*

## Running from Source

### Easy Setup (Recommended)

***You will need Python installed to run from source. Please visit https://www.python.org/downloads/ to download the correct version for your system.***

**Windows:**
- Double-click `setup_and_run.bat`
- OR run `setup_and_run.ps1` in PowerShell

**Linux/macOS:**
```bash
./setup_and_run.sh
```

These scripts will automatically:
1. Create a virtual environment
2. Install all dependencies
3. Run the game

### Manual Setup

If you want to run from source code manually:

1. Clone the repository
```bash
git clone https://github.com/BigZano/Pysteroids.git
cd Pysteroids
```

2. Create virtual environment (optional but recommended)
```bash
python -m venv env
source env/bin/activate  # Linux/macOS
env\Scripts\activate     # Windows
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Run the game
```
python main.py
```

## Credits

**Development**: bigzano
**Engine**: Python + Pygame
**Music/SFX**: (f"Music found on free Sound library, links to profiles are in assets/Attributions.txt")

## 📄 License

Just play and enjoy. Tell folks where you got it, and if you feel super strongly you can support me on itch.io :)

## 🐛 Bug Reports

Found a bug? Please report it on [https://github.com/bigzano] and submit a pull request

## 🎮 Version History

### v1.0.0 (Current)
- Initial release
- Boss asteroid system
- Ring blast mechanics
- Power-up collection
- Dash system
- Dynamic backgrounds
- Multiple resolution support

---

**Enjoy the game! May your aim be true and your dashes timely! 🚀**
