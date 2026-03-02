"""Player data model."""
from src.config import PLAYER_MAX_HEALTH, ITEMS


class Player:
    """Holds the player's state: health, score, inventory, active effects."""

    def __init__(self):
        self.max_health = PLAYER_MAX_HEALTH
        self.health = PLAYER_MAX_HEALTH
        self.score = 0
        self.inventory: dict[str, int] = {}   # raw material counts
        self.power_ups: dict[str, int] = {}   # usable item counts
        self.active_effects: list[str] = []   # currently active effect names
        self.correct_streak = 0
        self.total_correct = 0
        self.total_wrong = 0
        self.operation_stats: dict[str, dict[str, int]] = {}

    # ------------------------------------------------------------------ #
    #  Health                                                              #
    # ------------------------------------------------------------------ #

    def take_damage(self, amount: int = 1) -> bool:
        """Apply damage. Returns True if player is still alive."""
        if "shield" in self.active_effects:
            self.active_effects.remove("shield")
            return True  # blocked
        self.health = max(0, self.health - amount)
        return self.health > 0

    def heal(self, amount: int = 1) -> None:
        self.health = min(self.max_health, self.health + amount)

    def is_alive(self) -> bool:
        return self.health > 0

    # ------------------------------------------------------------------ #
    #  Score                                                               #
    # ------------------------------------------------------------------ #

    def add_score(self, base: int) -> int:
        """Add score, applying double_score effect if active. Returns actual added."""
        multiplier = 2 if "double_score" in self.active_effects else 1
        if "double_score" in self.active_effects:
            self.active_effects.remove("double_score")
        amount = base * multiplier
        self.score += amount
        return amount

    # ------------------------------------------------------------------ #
    #  Inventory (raw materials)                                          #
    # ------------------------------------------------------------------ #

    def add_material(self, material: str, count: int = 1) -> None:
        self.inventory[material] = self.inventory.get(material, 0) + count

    def has_materials(self, requirements: list[tuple[str, int]]) -> bool:
        return all(self.inventory.get(mat, 0) >= qty for mat, qty in requirements)

    def consume_materials(self, requirements: list[tuple[str, int]]) -> bool:
        if not self.has_materials(requirements):
            return False
        for mat, qty in requirements:
            self.inventory[mat] -= qty
        return True

    # ------------------------------------------------------------------ #
    #  Power-ups                                                           #
    # ------------------------------------------------------------------ #

    def add_power_up(self, item_key: str) -> None:
        self.power_ups[item_key] = self.power_ups.get(item_key, 0) + 1

    def use_power_up(self, item_key: str) -> bool:
        """Use a power-up. Returns True if successful."""
        if self.power_ups.get(item_key, 0) <= 0:
            return False
        self.power_ups[item_key] -= 1
        effect = ITEMS[item_key]["effect"]
        value = ITEMS[item_key]["value"]
        if effect == "heal":
            self.heal(value)
        elif effect == "shield":
            if "shield" not in self.active_effects:
                self.active_effects.append("shield")
        elif effect == "time_freeze":
            if "time_freeze" not in self.active_effects:
                self.active_effects.append("time_freeze")
        elif effect == "hint":
            if "hint" not in self.active_effects:
                self.active_effects.append("hint")
        elif effect == "double_score":
            if "double_score" not in self.active_effects:
                self.active_effects.append("double_score")
        return True

    # ------------------------------------------------------------------ #
    #  Stats                                                               #
    # ------------------------------------------------------------------ #

    def record_answer(self, correct: bool, operation: str | None = None) -> None:
        if correct:
            self.total_correct += 1
            self.correct_streak += 1
        else:
            self.total_wrong += 1
            self.correct_streak = 0

        if operation:
            if operation not in self.operation_stats:
                self.operation_stats[operation] = {"correct": 0, "wrong": 0}
            key = "correct" if correct else "wrong"
            self.operation_stats[operation][key] += 1

    def accuracy_percent(self) -> float:
        total = self.total_correct + self.total_wrong
        if total == 0:
            return 100.0
        return round(self.total_correct / total * 100, 1)

    def operation_accuracy(self, operation: str) -> float:
        """Return accuracy percentage for one operation type."""
        stats = self.operation_stats.get(operation)
        if not stats:
            return 100.0
        total = stats["correct"] + stats["wrong"]
        if total == 0:
            return 100.0
        return round(stats["correct"] / total * 100, 1)

    def weakest_operations(self, min_attempts: int = 1, limit: int = 3) -> list[str]:
        """Return operations sorted from weakest to strongest based on accuracy."""
        ranked: list[tuple[float, int, str]] = []
        for op, stats in self.operation_stats.items():
            attempts = stats["correct"] + stats["wrong"]
            if attempts < min_attempts:
                continue
            ranked.append((self.operation_accuracy(op), attempts, op))

        ranked.sort(key=lambda item: (item[0], -item[1], item[2]))
        return [op for _, _, op in ranked[:limit]]

    def performance_summary(self) -> dict:
        """Summarize overall and per-operation performance in one object."""
        operation_breakdown = {
            op: {
                "correct": stats["correct"],
                "wrong": stats["wrong"],
                "accuracy": self.operation_accuracy(op),
            }
            for op, stats in sorted(self.operation_stats.items())
        }
        return {
            "total_correct": self.total_correct,
            "total_wrong": self.total_wrong,
            "accuracy": self.accuracy_percent(),
            "best_streak": self.correct_streak,
            "weakest_operations": self.weakest_operations(),
            "operations": operation_breakdown,
        }
