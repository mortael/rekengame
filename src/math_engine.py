"""Math problem generation engine for the rekengame."""
import random
import math
from dataclasses import dataclass, field
from typing import Optional

from src.config import Difficulty, DIFFICULTY_SETTINGS


@dataclass
class MathProblem:
    """Represents a single math problem."""
    question: str
    answer: float
    operation: str
    time_limit: Optional[int]  # seconds, None = no limit
    hint: str = ""
    choices: list = field(default_factory=list)  # for multiple choice (future use)

    def check_answer(self, user_answer: str) -> bool:
        """Check if the user's answer is correct."""
        try:
            val = float(user_answer.replace(",", ".").strip())
            # Allow small float rounding differences
            if self.answer == int(self.answer):
                return int(val) == int(self.answer)
            return abs(val - self.answer) < 0.01
        except (ValueError, AttributeError):
            return False


class MathEngine:
    """Generates math problems based on difficulty and operation type."""

    def __init__(self, difficulty: Difficulty = Difficulty.EASY):
        self.difficulty = difficulty
        self.settings = DIFFICULTY_SETTINGS[difficulty]

    def set_difficulty(self, difficulty: Difficulty) -> None:
        self.difficulty = difficulty
        self.settings = DIFFICULTY_SETTINGS[difficulty]

    def _get_range(self, scale: float = 1.0) -> tuple:
        lo, hi = self.settings["number_range"]
        hi = max(lo + 1, int(hi * scale))
        return lo, hi

    def _rand(self, lo: int, hi: int) -> int:
        return random.randint(lo, hi)

    def generate(self, operation: Optional[str] = None, scale: float = 1.0) -> MathProblem:
        """Generate a math problem for the given operation (or random from allowed ops)."""
        ops = self.settings["operations"]
        if operation is None or operation not in ops:
            operation = random.choice(ops)

        time_limit = self.settings.get("time_limit")

        if operation == "addition":
            return self._addition(time_limit, scale)
        elif operation == "subtraction":
            return self._subtraction(time_limit, scale)
        elif operation == "multiplication":
            return self._multiplication(time_limit, scale)
        elif operation == "division":
            return self._division(time_limit, scale)
        elif operation == "word_problem":
            return self._word_problem(time_limit, scale)
        elif operation == "money":
            return self._money(time_limit, scale)
        elif operation == "square_root":
            return self._square_root(time_limit)
        else:
            return self._addition(time_limit, scale)

    # ------------------------------------------------------------------ #
    #  Operation implementations                                           #
    # ------------------------------------------------------------------ #

    def _addition(self, time_limit, scale) -> MathProblem:
        lo, hi = self._get_range(scale)
        a = self._rand(lo, hi)
        b = self._rand(lo, hi)
        return MathProblem(
            question=f"{a} + {b} = ?",
            answer=a + b,
            operation="addition",
            time_limit=time_limit,
            hint=f"Tel {a} en {b} bij elkaar op.",
        )

    def _subtraction(self, time_limit, scale) -> MathProblem:
        lo, hi = self._get_range(scale)
        a = self._rand(lo, hi)
        b = self._rand(lo, a)  # ensure non-negative result
        return MathProblem(
            question=f"{a} - {b} = ?",
            answer=a - b,
            operation="subtraction",
            time_limit=time_limit,
            hint=f"Trek {b} af van {a}.",
        )

    def _multiplication(self, time_limit, scale) -> MathProblem:
        tables = self.settings["tables"]
        table = random.choice(tables)
        lo, hi = self._get_range(scale)
        factor = self._rand(lo, min(hi, 12))
        return MathProblem(
            question=f"{table} × {factor} = ?",
            answer=table * factor,
            operation="multiplication",
            time_limit=time_limit,
            hint=f"Tafel van {table}: {table} × {factor}.",
        )

    def _division(self, time_limit, scale) -> MathProblem:
        tables = self.settings["tables"]
        divisor = random.choice(tables)
        lo, hi = self._get_range(scale)
        quotient = self._rand(1, min(hi, 12))
        dividend = divisor * quotient
        return MathProblem(
            question=f"{dividend} ÷ {divisor} = ?",
            answer=quotient,
            operation="division",
            time_limit=time_limit,
            hint=f"Hoeveel keer past {divisor} in {dividend}?",
        )

    def _word_problem(self, time_limit, scale) -> MathProblem:
        lo, hi = self._get_range(scale)
        templates = [
            self._word_buy_sell,
            self._word_share,
            self._word_distance,
            self._word_age,
            self._word_apples,
        ]
        generator = random.choice(templates)
        return generator(lo, hi, time_limit)

    def _word_buy_sell(self, lo, hi, time_limit) -> MathProblem:
        items = ["appels", "boeken", "pennen", "stickers", "koekjes"]
        item = random.choice(items)
        price = self._rand(1, max(2, hi // 10))
        qty = self._rand(2, max(3, hi // 20))
        total = price * qty
        return MathProblem(
            question=(
                f"Lena koopt {qty} {item} voor €{price} per stuk.\n"
                f"Hoeveel betaalt ze in totaal?"
            ),
            answer=total,
            operation="word_problem",
            time_limit=time_limit,
            hint=f"Vermenigvuldig {qty} × €{price}.",
        )

    def _word_share(self, lo, hi, time_limit) -> MathProblem:
        people = ["kinderen", "vrienden", "klasgenoten"]
        snacks = ["koekjes", "snoepjes", "stickers"]
        group = random.choice(people)
        snack = random.choice(snacks)
        divisor = self._rand(2, min(10, hi // 5))
        quotient = self._rand(2, min(12, hi // divisor))
        total = divisor * quotient
        return MathProblem(
            question=(
                f"Er zijn {total} {snack} voor {divisor} {group}.\n"
                f"Hoeveel krijgt elk kind?"
            ),
            answer=quotient,
            operation="word_problem",
            time_limit=time_limit,
            hint=f"Deel {total} door {divisor}.",
        )

    def _word_distance(self, lo, hi, time_limit) -> MathProblem:
        speed = self._rand(2, max(3, hi // 20))
        time_h = self._rand(2, 6)
        distance = speed * time_h
        return MathProblem(
            question=(
                f"Tim fietst {speed} km per uur.\n"
                f"Hoe ver rijdt hij na {time_h} uur?"
            ),
            answer=distance,
            operation="word_problem",
            time_limit=time_limit,
            hint=f"Vermenigvuldig {speed} × {time_h}.",
        )

    def _word_age(self, lo, hi, time_limit) -> MathProblem:
        age_a = self._rand(10, min(50, hi // 2))
        diff = self._rand(2, min(20, age_a - 1))
        age_b = age_a - diff
        names = [("Tom", "Lisa"), ("Sara", "Bob"), ("Max", "Emma")]
        name_a, name_b = random.choice(names)
        return MathProblem(
            question=(
                f"{name_a} is {age_a} jaar oud.\n"
                f"{name_b} is {diff} jaar jonger.\n"
                f"Hoe oud is {name_b}?"
            ),
            answer=age_b,
            operation="word_problem",
            time_limit=time_limit,
            hint=f"Trek {diff} af van {age_a}.",
        )

    def _word_apples(self, lo, hi, time_limit) -> MathProblem:
        start = self._rand(lo, hi)
        eaten = self._rand(1, max(2, start - 1))
        left = start - eaten
        return MathProblem(
            question=(
                f"Er liggen {start} appels in een mand.\n"
                f"Er worden {eaten} appels gegeten.\n"
                f"Hoeveel appels zijn er nog?"
            ),
            answer=left,
            operation="word_problem",
            time_limit=time_limit,
            hint=f"Trek {eaten} af van {start}.",
        )

    def _money(self, time_limit, scale) -> MathProblem:
        lo_m, hi_m = self.settings["money_range"]
        templates = [
            self._money_change,
            self._money_total,
            self._money_split,
        ]
        return random.choice(templates)(lo_m, hi_m, time_limit)

    def _money_change(self, lo, hi, time_limit) -> MathProblem:
        price = self._rand(lo, hi)
        paid = price + random.choice([1, 5, 10, 20, 50])
        change = paid - price
        return MathProblem(
            question=(
                f"Een artikel kost €{price}.\n"
                f"Je betaalt met €{paid}.\n"
                f"Hoeveel wisselgeld krijg je terug?"
            ),
            answer=change,
            operation="money",
            time_limit=time_limit,
            hint=f"Trek €{price} af van €{paid}.",
        )

    def _money_total(self, lo, hi, time_limit) -> MathProblem:
        items = ["boek", "speelgoed", "pen", "snoep", "schrift"]
        item = random.choice(items)
        price = self._rand(lo, max(lo + 1, hi // 5))
        qty = self._rand(2, 5)
        total = price * qty
        return MathProblem(
            question=(
                f"Een {item} kost €{price}.\n"
                f"Je koopt er {qty}.\n"
                f"Wat is het totaal bedrag?"
            ),
            answer=total,
            operation="money",
            time_limit=time_limit,
            hint=f"Vermenigvuldig €{price} × {qty}.",
        )

    def _money_split(self, lo, hi, time_limit) -> MathProblem:
        people = self._rand(2, 5)
        total = people * self._rand(lo, max(lo + 1, hi // people))
        share = total // people
        return MathProblem(
            question=(
                f"Een groep van {people} vrienden betaalt samen €{total}.\n"
                f"Ze splitsen de rekening gelijk.\n"
                f"Hoeveel betaalt elk persoon?"
            ),
            answer=share,
            operation="money",
            time_limit=time_limit,
            hint=f"Deel €{total} door {people}.",
        )

    def _square_root(self, time_limit) -> MathProblem:
        sqrt_numbers = self.settings["sqrt_numbers"]
        n = random.choice(sqrt_numbers)
        root = int(math.sqrt(n))
        return MathProblem(
            question=f"√{n} = ?",
            answer=root,
            operation="square_root",
            time_limit=time_limit,
            hint=f"Welk getal keer zichzelf is {n}?",
        )

    def generate_boss_problem(self, boss_index: int, scale: float = 1.0) -> MathProblem:
        """Generate a harder problem for boss encounters."""
        # Boss problems cycle through operations in increasing difficulty
        ops = self.settings["operations"]
        op = ops[min(boss_index, len(ops) - 1)]
        problem = self.generate(op, scale=scale * 1.5)
        # Boss problems always have a time limit
        if problem.time_limit is None:
            problem.time_limit = 30
        return problem
