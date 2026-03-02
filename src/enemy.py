"""Enemy and Boss data models."""
import random
from dataclasses import dataclass, field
from typing import Optional

from src.config import ENEMY_DROPS


@dataclass
class Enemy:
    """A regular enemy in the game world."""
    name: str
    health: int
    max_health: int
    position: tuple  # (x, z) in world space
    difficulty_scale: float = 1.0
    is_defeated: bool = False
    drops: list[str] = field(default_factory=list)
    score_value: int = 50

    def take_damage(self, amount: int = 1) -> None:
        self.health = max(0, self.health - amount)
        if self.health <= 0:
            self.is_defeated = True

    def is_alive(self) -> bool:
        return not self.is_defeated

    def get_drops(self) -> list[str]:
        """Return a random selection of drops."""
        count = random.randint(1, 2)
        return random.choices(ENEMY_DROPS["regular"], k=count)

    @classmethod
    def create(cls, position: tuple, difficulty_scale: float = 1.0, level: int = 1):
        names = [
            "Rokul de Rekenridder",
            "Somilla de Sloerie",
            "Teller-Troll",
            "Breuk-Boef",
            "Aftrek-Aap",
        ]
        health = max(1, int(difficulty_scale * level))
        return cls(
            name=random.choice(names),
            health=health,
            max_health=health,
            position=position,
            difficulty_scale=difficulty_scale,
            score_value=50 * level,
        )


@dataclass
class Boss:
    """A boss enemy requiring multiple math problems."""
    name: str
    health: int
    max_health: int
    position: tuple
    phase: int = 0               # current phase (0-indexed)
    num_phases: int = 3          # number of math questions to defeat
    is_defeated: bool = False
    drops: list[str] = field(default_factory=list)
    score_value: int = 300
    special_title: str = ""      # displayed in boss intro
    difficulty_scale: float = 1.0

    def take_damage(self, amount: int = 1) -> None:
        self.health = max(0, self.health - amount)
        if self.health <= 0:
            self.is_defeated = True
        else:
            self.phase = min(self.phase + amount, self.num_phases - 1)

    def is_alive(self) -> bool:
        return not self.is_defeated

    def get_drops(self) -> list[str]:
        count = random.randint(2, 4)
        return random.choices(ENEMY_DROPS["boss"], k=count)

    @classmethod
    def create(cls, position: tuple, boss_index: int, level: int, difficulty_scale: float):
        boss_data = [
            {
                "name": "Groot Hoofd Rekenes",
                "title": "De Heerser der Sommen",
                "num_phases": 3,
            },
            {
                "name": "De IJzeren Telraam",
                "title": "Meester van de Tafel",
                "num_phases": 4,
            },
            {
                "name": "Eindbaas Minuska",
                "title": "Koningin van het Aftrekken",
                "num_phases": 5,
            },
        ]
        data = boss_data[boss_index % len(boss_data)]
        health = data["num_phases"]
        return cls(
            name=data["name"],
            health=health,
            max_health=health,
            position=position,
            num_phases=data["num_phases"],
            score_value=300 * level,
            special_title=data["title"],
            difficulty_scale=difficulty_scale,
        )
