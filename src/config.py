"""Game configuration constants."""
from enum import Enum


class GameState(Enum):
    MENU = "menu"
    DIFFICULTY = "difficulty"
    PLAYING = "playing"
    COMBAT = "combat"
    CRAFTING = "crafting"
    BOSS_INTRO = "boss_intro"
    LEVEL_COMPLETE = "level_complete"
    GAME_OVER = "game_over"
    WIN = "win"


class Difficulty(Enum):
    EASY = 1
    MEDIUM = 2
    HARD = 3
    EXPERT = 4
    CUSTOM = 5


DIFFICULTY_SETTINGS = {
    Difficulty.EASY: {
        "name": "Makkelijk",
        "number_range": (1, 20),
        "operations": ["addition", "subtraction"],
        "time_limit": None,
        "tables": list(range(2, 6)),
        "money_range": (1, 10),
        "sqrt_numbers": [4, 9, 16, 25],
    },
    Difficulty.MEDIUM: {
        "name": "Normaal",
        "number_range": (1, 100),
        "operations": ["addition", "subtraction", "multiplication", "money"],
        "time_limit": 45,
        "tables": list(range(2, 11)),
        "money_range": (1, 100),
        "sqrt_numbers": [4, 9, 16, 25, 36, 49],
    },
    Difficulty.HARD: {
        "name": "Moeilijk",
        "number_range": (1, 1000),
        "operations": [
            "addition", "subtraction", "multiplication", "division",
            "word_problem", "money",
        ],
        "time_limit": 30,
        "tables": list(range(2, 13)),
        "money_range": (1, 500),
        "sqrt_numbers": [4, 9, 16, 25, 36, 49, 64, 81, 100],
    },
    Difficulty.EXPERT: {
        "name": "Expert",
        "number_range": (1, 10000),
        "operations": [
            "addition", "subtraction", "multiplication", "division",
            "word_problem", "money", "square_root",
        ],
        "time_limit": 20,
        "tables": list(range(2, 13)),
        "money_range": (1, 1000),
        "sqrt_numbers": [4, 9, 16, 25, 36, 49, 64, 81, 100, 121, 144],
    },
}

# Number of levels in the game
NUM_LEVELS = 4

LEVEL_CONFIGS = [
    {
        "number": 1,
        "name": "Het Groene Woud",
        "theme": "forest",
        "floor_texture": "grass",
        "wall_color": (0.4, 0.6, 0.2),
        "enemy_color": (0.8, 0.2, 0.2),
        "boss_color": (0.6, 0.0, 0.0),
        "num_regular_enemies": 6,
        "num_bosses": 3,
        "difficulty_scale": 1.0,
        "world_size": 24,
    },
    {
        "number": 2,
        "name": "De Stenen Vesting",
        "theme": "castle",
        "floor_texture": "brick",
        "wall_color": (0.5, 0.5, 0.6),
        "enemy_color": (0.8, 0.4, 0.0),
        "boss_color": (0.5, 0.0, 0.5),
        "num_regular_enemies": 8,
        "num_bosses": 3,
        "difficulty_scale": 1.5,
        "world_size": 28,
    },
    {
        "number": 3,
        "name": "De IJsvlakte",
        "theme": "ice",
        "floor_texture": "white_cube",
        "wall_color": (0.7, 0.85, 1.0),
        "enemy_color": (0.0, 0.4, 0.9),
        "boss_color": (0.0, 0.0, 0.7),
        "num_regular_enemies": 10,
        "num_bosses": 3,
        "difficulty_scale": 2.0,
        "world_size": 32,
    },
    {
        "number": 4,
        "name": "De Vulkaanberg",
        "theme": "volcano",
        "floor_texture": "white_cube",
        "wall_color": (0.4, 0.1, 0.0),
        "enemy_color": (1.0, 0.3, 0.0),
        "boss_color": (0.8, 0.0, 0.0),
        "num_regular_enemies": 12,
        "num_bosses": 3,
        "difficulty_scale": 2.5,
        "world_size": 36,
    },
]

# Player defaults
PLAYER_MAX_HEALTH = 5
PLAYER_START_HEALTH = 5

# Power-up item definitions
ITEMS = {
    "health_potion": {
        "name": "Levensdrankje",
        "description": "Herstelt 1 levenspunt",
        "effect": "heal",
        "value": 1,
        "emoji": "❤️",
    },
    "shield": {
        "name": "Schild",
        "description": "Blokkeert de volgende fout",
        "effect": "shield",
        "value": 1,
        "emoji": "🛡️",
    },
    "time_freeze": {
        "name": "Tijdstop",
        "description": "Stopt de timer voor 1 vraag",
        "effect": "time_freeze",
        "value": 1,
        "emoji": "⏳",
    },
    "hint": {
        "name": "Hint-kaart",
        "description": "Laat een hint zien bij de volgende vraag",
        "effect": "hint",
        "value": 1,
        "emoji": "💡",
    },
    "double_score": {
        "name": "Dubbel Punten",
        "description": "Verdubbelt punten voor de volgende som",
        "effect": "double_score",
        "value": 1,
        "emoji": "⭐",
    },
}

# Crafting recipes: {result_item: [(ingredient, count), ...], math_type}
CRAFTING_RECIPES = [
    {
        "result": "health_potion",
        "ingredients": [("herb", 2), ("water", 1)],
        "math_type": "addition",
        "description": "Maak een Levensdrankje",
    },
    {
        "result": "shield",
        "ingredients": [("wood", 3), ("metal", 1)],
        "math_type": "multiplication",
        "description": "Maak een Schild",
    },
    {
        "result": "time_freeze",
        "ingredients": [("crystal", 2), ("herb", 1)],
        "math_type": "division",
        "description": "Maak een Tijdstop",
    },
    {
        "result": "hint",
        "ingredients": [("scroll", 1), ("ink", 1)],
        "math_type": "subtraction",
        "description": "Maak een Hint-kaart",
    },
    {
        "result": "double_score",
        "ingredients": [("gold", 2), ("crystal", 1)],
        "math_type": "multiplication",
        "description": "Maak Dubbel Punten",
    },
]

# Item drops from enemies
ENEMY_DROPS = {
    "regular": ["herb", "wood", "water", "scroll"],
    "boss": ["metal", "crystal", "gold", "ink"],
}

# Window settings
WINDOW_TITLE = "RekengameAventuur"
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
