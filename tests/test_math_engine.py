"""Tests for the math engine problem generation."""
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from src.math_engine import MathEngine, MathProblem
from src.config import Difficulty


@pytest.fixture
def easy_engine():
    return MathEngine(Difficulty.EASY)


@pytest.fixture
def medium_engine():
    return MathEngine(Difficulty.MEDIUM)


@pytest.fixture
def hard_engine():
    return MathEngine(Difficulty.HARD)


@pytest.fixture
def expert_engine():
    return MathEngine(Difficulty.EXPERT)


# ------------------------------------------------------------------ #
#  MathProblem.check_answer                                            #
# ------------------------------------------------------------------ #

class TestMathProblemCheckAnswer:
    def test_correct_integer(self):
        p = MathProblem("3 + 4 = ?", 7, "addition", None)
        assert p.check_answer("7")

    def test_correct_with_spaces(self):
        p = MathProblem("3 + 4 = ?", 7, "addition", None)
        assert p.check_answer("  7  ")

    def test_wrong_answer(self):
        p = MathProblem("3 + 4 = ?", 7, "addition", None)
        assert not p.check_answer("8")

    def test_non_numeric_input(self):
        p = MathProblem("3 + 4 = ?", 7, "addition", None)
        assert not p.check_answer("abc")

    def test_empty_string(self):
        p = MathProblem("3 + 4 = ?", 7, "addition", None)
        assert not p.check_answer("")

    def test_comma_as_decimal_separator(self):
        p = MathProblem("test", 3.5, "division", None)
        assert p.check_answer("3,5")

    def test_float_answer(self):
        p = MathProblem("test", 3.5, "division", None)
        assert p.check_answer("3.5")

    def test_negative_answer(self):
        p = MathProblem("2 - 5 = ?", -3, "subtraction", None)
        assert p.check_answer("-3")


# ------------------------------------------------------------------ #
#  Addition                                                            #
# ------------------------------------------------------------------ #

class TestAddition:
    def test_generates_problem(self, easy_engine):
        p = easy_engine.generate("addition")
        assert "+" in p.question
        assert p.operation == "addition"

    def test_answer_is_correct(self, easy_engine):
        for _ in range(20):
            p = easy_engine.generate("addition")
            nums = [int(x) for x in p.question.replace(" = ?", "").split("+")]
            assert sum(nums) == p.answer

    def test_numbers_in_range(self, easy_engine):
        for _ in range(20):
            p = easy_engine.generate("addition")
            nums = [int(x.strip()) for x in p.question.replace(" = ?", "").split("+")]
            for n in nums:
                assert 1 <= n <= 20

    def test_medium_range(self, medium_engine):
        for _ in range(20):
            p = medium_engine.generate("addition")
            nums = [int(x.strip()) for x in p.question.replace(" = ?", "").split("+")]
            for n in nums:
                assert 1 <= n <= 100


# ------------------------------------------------------------------ #
#  Subtraction                                                         #
# ------------------------------------------------------------------ #

class TestSubtraction:
    def test_generates_problem(self, easy_engine):
        p = easy_engine.generate("subtraction")
        assert "-" in p.question
        assert p.operation == "subtraction"

    def test_answer_non_negative(self, easy_engine):
        for _ in range(50):
            p = easy_engine.generate("subtraction")
            assert p.answer >= 0

    def test_answer_correct(self, easy_engine):
        for _ in range(20):
            p = easy_engine.generate("subtraction")
            parts = p.question.replace(" = ?", "").split("-")
            a, b = int(parts[0].strip()), int(parts[1].strip())
            assert a - b == p.answer


# ------------------------------------------------------------------ #
#  Multiplication                                                      #
# ------------------------------------------------------------------ #

class TestMultiplication:
    def test_generates_problem(self, medium_engine):
        p = medium_engine.generate("multiplication")
        assert "×" in p.question
        assert p.operation == "multiplication"

    def test_answer_correct(self, medium_engine):
        for _ in range(20):
            p = medium_engine.generate("multiplication")
            parts = p.question.replace(" = ?", "").split("×")
            a, b = int(parts[0].strip()), int(parts[1].strip())
            assert a * b == p.answer

    def test_tables_in_range(self, medium_engine):
        tables = set()
        for _ in range(100):
            p = medium_engine.generate("multiplication")
            parts = p.question.replace(" = ?", "").split("×")
            tables.add(int(parts[0].strip()))
        # Should use tables 2–10 for medium difficulty
        assert tables.issubset(set(range(2, 11)))


# ------------------------------------------------------------------ #
#  Division                                                            #
# ------------------------------------------------------------------ #

class TestDivision:
    def test_generates_problem(self, hard_engine):
        p = hard_engine.generate("division")
        assert "÷" in p.question
        assert p.operation == "division"

    def test_answer_exact(self, hard_engine):
        for _ in range(20):
            p = hard_engine.generate("division")
            parts = p.question.replace(" = ?", "").split("÷")
            dividend, divisor = int(parts[0].strip()), int(parts[1].strip())
            assert dividend % divisor == 0
            assert dividend // divisor == int(p.answer)


# ------------------------------------------------------------------ #
#  Word problems                                                       #
# ------------------------------------------------------------------ #

class TestWordProblems:
    def test_generates_problem(self, hard_engine):
        p = hard_engine.generate("word_problem")
        assert p.operation == "word_problem"
        assert "?" in p.question or len(p.question) > 10

    def test_has_hint(self, hard_engine):
        for _ in range(10):
            p = hard_engine.generate("word_problem")
            assert len(p.hint) > 0

    def test_positive_answer(self, hard_engine):
        for _ in range(30):
            p = hard_engine.generate("word_problem")
            assert p.answer >= 0


# ------------------------------------------------------------------ #
#  Money problems                                                      #
# ------------------------------------------------------------------ #

class TestMoneyProblems:
    def test_generates_problem(self, medium_engine):
        p = medium_engine.generate("money")
        assert p.operation == "money"

    def test_positive_answer(self, medium_engine):
        for _ in range(20):
            p = medium_engine.generate("money")
            assert p.answer > 0

    def test_euro_sign_in_question(self, medium_engine):
        for _ in range(20):
            p = medium_engine.generate("money")
            assert "€" in p.question


# ------------------------------------------------------------------ #
#  Square root                                                         #
# ------------------------------------------------------------------ #

class TestSquareRoot:
    def test_generates_problem(self, expert_engine):
        p = expert_engine.generate("square_root")
        assert "√" in p.question
        assert p.operation == "square_root"

    def test_answer_is_integer_root(self, expert_engine):
        for _ in range(20):
            p = expert_engine.generate("square_root")
            assert p.answer == int(p.answer)
            assert int(p.answer) ** 2 == int(p.question.split("√")[1].split("=")[0].strip())


# ------------------------------------------------------------------ #
#  Time limits                                                         #
# ------------------------------------------------------------------ #

class TestTimeLimits:
    def test_easy_no_time_limit(self, easy_engine):
        for _ in range(10):
            p = easy_engine.generate()
            assert p.time_limit is None

    def test_medium_has_time_limit(self, medium_engine):
        for _ in range(10):
            p = medium_engine.generate()
            assert p.time_limit == 45

    def test_hard_has_time_limit(self, hard_engine):
        for _ in range(10):
            p = hard_engine.generate()
            assert p.time_limit == 30

    def test_expert_has_time_limit(self, expert_engine):
        for _ in range(10):
            p = expert_engine.generate()
            assert p.time_limit == 20


# ------------------------------------------------------------------ #
#  Boss problems                                                       #
# ------------------------------------------------------------------ #

class TestBossProblems:
    def test_boss_has_time_limit(self, easy_engine):
        for i in range(3):
            p = easy_engine.generate_boss_problem(i)
            assert p.time_limit is not None
            assert p.time_limit > 0

    def test_boss_problem_types_vary(self, expert_engine):
        ops = set()
        for i in range(7):
            p = expert_engine.generate_boss_problem(i)
            ops.add(p.operation)
        assert len(ops) > 1


# ------------------------------------------------------------------ #
#  Set difficulty                                                      #
# ------------------------------------------------------------------ #

class TestSetDifficulty:
    def test_can_change_difficulty(self):
        engine = MathEngine(Difficulty.EASY)
        engine.set_difficulty(Difficulty.EXPERT)
        assert engine.difficulty == Difficulty.EXPERT

    def test_changed_difficulty_affects_generation(self):
        engine = MathEngine(Difficulty.EASY)
        easy_problems = [engine.generate("addition") for _ in range(20)]
        max_easy = max(p.answer for p in easy_problems)

        engine.set_difficulty(Difficulty.EXPERT)
        expert_problems = [engine.generate("addition") for _ in range(20)]
        max_expert = max(p.answer for p in expert_problems)

        # Expert should generally produce larger numbers
        assert max_expert >= max_easy
