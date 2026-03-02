"""Level manager: tracks current level, progression, and world layout."""
import random
from src.config import LEVEL_CONFIGS, NUM_LEVELS, Difficulty, DIFFICULTY_SETTINGS
from src.enemy import Enemy, Boss


class LevelManager:
    """Manages level progression and difficulty scaling."""

    def __init__(self, difficulty: Difficulty = Difficulty.EASY):
        self.current_level_index = 0
        self.difficulty = difficulty
        self._enemies: list[Enemy] = []
        self._bosses: list[Boss] = []

    @property
    def current_level(self) -> dict:
        return LEVEL_CONFIGS[self.current_level_index]

    @property
    def level_number(self) -> int:
        return self.current_level["number"]

    @property
    def level_name(self) -> str:
        return self.current_level["name"]

    @property
    def is_last_level(self) -> bool:
        return self.current_level_index >= NUM_LEVELS - 1

    def advance_level(self) -> bool:
        """Move to next level. Returns False if already on last level."""
        if self.is_last_level:
            return False
        self.current_level_index += 1
        return True

    def get_difficulty_scale(self) -> float:
        """Effective difficulty multiplier combining player choice and level."""
        base = {
            Difficulty.EASY: 0.7,
            Difficulty.MEDIUM: 1.0,
            Difficulty.HARD: 1.4,
            Difficulty.EXPERT: 2.0,
            Difficulty.CUSTOM: 1.0,
        }[self.difficulty]
        return base * self.current_level["difficulty_scale"]

    def spawn_enemies(self, positions: list[tuple]) -> list[Enemy]:
        """Create regular enemies at the given positions."""
        cfg = self.current_level
        scale = self.get_difficulty_scale()
        self._enemies = []
        count = min(len(positions), cfg["num_regular_enemies"])
        for pos in positions[:count]:
            enemy = Enemy.create(pos, difficulty_scale=scale, level=self.level_number)
            self._enemies.append(enemy)
        return self._enemies

    def spawn_bosses(self, positions: list[tuple]) -> list[Boss]:
        """Create boss enemies at the given positions."""
        cfg = self.current_level
        scale = self.get_difficulty_scale()
        self._bosses = []
        for i, pos in enumerate(positions[: cfg["num_bosses"]]):
            boss = Boss.create(
                pos,
                boss_index=i,
                level=self.level_number,
                difficulty_scale=scale,
            )
            self._bosses.append(boss)
        return self._bosses

    def all_bosses_defeated(self) -> bool:
        return all(b.is_defeated for b in self._bosses)

    def all_enemies_defeated(self) -> bool:
        return all(e.is_defeated for e in self._enemies) and self.all_bosses_defeated()

    def get_operations_for_level(self) -> list[str]:
        """Return allowed math operations for the current difficulty."""
        return DIFFICULTY_SETTINGS[self.difficulty]["operations"]

    # ------------------------------------------------------------------ #
    #  World layout helper                                                 #
    # ------------------------------------------------------------------ #

    @staticmethod
    def generate_positions(
        world_size: int,
        count: int,
        exclude_center: bool = True,
        min_dist: float = 4.0,
    ) -> list[tuple]:
        """Generate non-overlapping positions inside the world grid."""
        positions = []
        attempts = 0
        center = world_size // 2
        while len(positions) < count and attempts < 1000:
            attempts += 1
            x = random.randint(2, world_size - 3)
            z = random.randint(2, world_size - 3)
            if exclude_center and abs(x - center) < 3 and abs(z - center) < 3:
                continue
            if all(
                ((x - px) ** 2 + (z - pz) ** 2) ** 0.5 >= min_dist
                for px, pz in positions
            ):
                positions.append((x, z))
        return positions
