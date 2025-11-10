import json
import os

SAVE_FILE = 'pysteroids_save.json'

def load_game_data():
    """Load game state from a JSON file."""
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, 'r') as f:
                data = json.load(f)
                # Ensure all required keys exist
                if 'unlocked_ships' not in data:
                    data['unlocked_ships'] = ["default"]
                if 'current_ship' not in data:
                    data['current_ship'] = "default"
                if 'highest_score' not in data:
                    data['highest_score'] = 0
                return data
        except Exception as e:
            print(f"Error loading save file: {e}")
            pass
    
    # Default save data
    return {
        "highest_score": 0,
        "unlocked_ships": ["default"],
        "current_ship": "default",
    }


def save_game_data(data):
    """Save game state to JSON file."""
    try:
        with open(SAVE_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving game data: {e}")
        return False
    

def check_unlocks(current_score, save_data):
    """Checks and unlocks ships based on current cumulative score"""
    from constants import SHIP_UNLOCKS

    new_unlocks = []
    for ship, required_score in SHIP_UNLOCKS.items():
        if current_score >= required_score and ship not in save_data['unlocked_ships']:
            save_data['unlocked_ships'].append(ship)
            new_unlocks.append(ship)
    
    # Save immediately after unlocking
    if new_unlocks:
        save_game_data(save_data)
    
    return new_unlocks