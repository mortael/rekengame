"""Tests for LevelManager and level progression."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from src.level_manager import LevelManager
from src.config import Difficulty, LEVEL_CONFIGS, NUM_LEVELS


@pytest.fixture
def easy_manager():
    return LevelManager(Difficulty.EASY)


@pytest.fixture
def expert_manager():
    return LevelManager(Difficulty.EXPERT)


# ------------------------------------------------------------------ #
#  Level properties                                                    #
# ------------------------------------------------------------------ #

class TestLevelProperties:
    def test_starts_at_level_1(self, easy_manager):
        assert easy_manager.level_number == 1

    def test_level_name_not_empty(self, easy_manager):
        assert len(easy_manager.level_name) > 0

    def test_not_last_level_at_start(self, easy_manager):
        assert not easy_manager.is_last_level

    def test_all_level_configs_present(self):
        assert len(LEVEL_CONFIGS) == NUM_LEVELS

    def test_levels_have_required_keys(self):
        required = {
            "number", "name", "num_regular_enemies", "num_bosses",
            "difficulty_scale", "world_size",
        }
        for cfg in LEVEL_CONFIGS:
            assert required.issubset(cfg.keys()), f"Missing keys in {cfg['name']}"

    def test_each_level_has_3_bosses(self):
        for cfg in LEVEL_CONFIGS:
            assert cfg["num_bosses"] == 3


# ------------------------------------------------------------------ #
#  Level progression                                                   #
# ------------------------------------------------------------------ #

class TestLevelProgression:
    def test_advance_returns_true(self, easy_manager):
        assert easy_manager.advance_level()

    def test_advance_increments_index(self, easy_manager):
        easy_manager.advance_level()
        assert easy_manager.level_number == 2

    def test_advance_through_all_levels(self, easy_manager):
        for _ in range(NUM_LEVELS - 1):
            easy_manager.advance_level()
        assert easy_manager.is_last_level

    def test_advance_beyond_last_returns_false(self, easy_manager):
        for _ in range(NUM_LEVELS - 1):
            easy_manager.advance_level()
        assert not easy_manager.advance_level()

    def test_level_index_matches_configs(self, easy_manager):
        for i in range(NUM_LEVELS):
            assert easy_manager.current_level_index == i
            assert easy_manager.level_number == LEVEL_CONFIGS[i]["number"]
            if i < NUM_LEVELS - 1:
                easy_manager.advance_level()


# ------------------------------------------------------------------ #
#  Difficulty scaling                                                  #
# ------------------------------------------------------------------ #

class TestDifficultyScaling:
    def test_easy_scale_less_than_expert(self):
        easy = LevelManager(Difficulty.EASY)
        expert = LevelManager(Difficulty.EXPERT)
        assert easy.get_difficulty_scale() < expert.get_difficulty_scale()

    def test_scale_increases_with_level(self, easy_manager):
        scale_level_1 = easy_manager.get_difficulty_scale()
        easy_manager.advance_level()
        scale_level_2 = easy_manager.get_difficulty_scale()
        assert scale_level_2 > scale_level_1

    def test_scale_is_positive(self, easy_manager):
        for _ in range(NUM_LEVELS):
            assert easy_manager.get_difficulty_scale() > 0
            if not easy_manager.is_last_level:
                easy_manager.advance_level()


# ------------------------------------------------------------------ #
#  Enemy spawning                                                      #
# ------------------------------------------------------------------ #

class TestEnemySpawning:
    def test_spawn_correct_enemy_count(self, easy_manager):
        positions = [(i * 3, i * 3) for i in range(20)]
        enemies = easy_manager.spawn_enemies(positions)
        expected = easy_manager.current_level["num_regular_enemies"]
        assert len(enemies) == expected

    def test_enemies_have_positions(self, easy_manager):
        positions = [(i * 3, i * 3) for i in range(20)]
        enemies = easy_manager.spawn_enemies(positions)
        for e in enemies:
            assert e.position in positions

    def test_enemies_are_alive(self, easy_manager):
        positions = [(i * 3, i * 3) for i in range(20)]
        enemies = easy_manager.spawn_enemies(positions)
        assert all(e.is_alive() for e in enemies)

    def test_all_enemies_defeated_flag(self, easy_manager):
        positions = [(i * 3, i * 3) for i in range(20)]
        enemies = easy_manager.spawn_enemies(positions)
        bosses = easy_manager.spawn_bosses([(50, 50), (60, 60), (70, 70)])
        assert not easy_manager.all_enemies_defeated()

        for e in enemies:
            e.take_damage(e.health)
        for b in bosses:
            b.take_damage(b.health)

        assert easy_manager.all_enemies_defeated()


# ------------------------------------------------------------------ #
#  Boss spawning                                                       #
# ------------------------------------------------------------------ #

class TestBossSpawning:
    def test_spawn_correct_boss_count(self, easy_manager):
        positions = [(i * 10 + 50, i * 10 + 50) for i in range(5)]
        bosses = easy_manager.spawn_bosses(positions)
        expected = easy_manager.current_level["num_bosses"]
        assert len(bosses) == expected

    def test_bosses_have_multiple_phases(self, easy_manager):
        positions = [(50, 50), (60, 60), (70, 70)]
        bosses = easy_manager.spawn_bosses(positions)
        for boss in bosses:
            assert boss.num_phases >= 3

    def test_bosses_alive_at_start(self, easy_manager):
        positions = [(50, 50), (60, 60), (70, 70)]
        bosses = easy_manager.spawn_bosses(positions)
        assert all(b.is_alive() for b in bosses)

    def test_all_bosses_not_defeated_initially(self, easy_manager):
        positions = [(50, 50), (60, 60), (70, 70)]
        easy_manager.spawn_bosses(positions)
        assert not easy_manager.all_bosses_defeated()

    def test_all_bosses_defeated_after_killing(self, easy_manager):
        positions = [(50, 50), (60, 60), (70, 70)]
        bosses = easy_manager.spawn_bosses(positions)
        for b in bosses:
            b.take_damage(b.health)
        assert easy_manager.all_bosses_defeated()


# ------------------------------------------------------------------ #
#  Position generation                                                 #
# ------------------------------------------------------------------ #

class TestPositionGeneration:
    def test_generates_requested_count(self):
        positions = LevelManager.generate_positions(30, 10)
        assert len(positions) == 10

    def test_positions_within_bounds(self):
        size = 30
        positions = LevelManager.generate_positions(size, 10)
        for x, z in positions:
            assert 0 <= x < size
            assert 0 <= z < size

    def test_positions_have_minimum_distance(self):
        min_dist = 3.0
        positions = LevelManager.generate_positions(30, 8, min_dist=min_dist)
        for i, (x1, z1) in enumerate(positions):
            for j, (x2, z2) in enumerate(positions):
                if i != j:
                    dist = ((x1 - x2) ** 2 + (z1 - z2) ** 2) ** 0.5
                    assert dist >= min_dist - 0.01  # small tolerance

    def test_returns_empty_if_impossible(self):
        # Too small a world for many positions
        positions = LevelManager.generate_positions(5, 100)
        assert len(positions) < 100  # Should return fewer than requested


# ------------------------------------------------------------------ #
#  Operations for level                                                #
# ------------------------------------------------------------------ #

class TestOperationsForLevel:
    def test_easy_has_limited_operations(self, easy_manager):
        ops = easy_manager.get_operations_for_level()
        assert "addition" in ops
        assert "square_root" not in ops

    def test_expert_has_all_operations(self, expert_manager):
        ops = expert_manager.get_operations_for_level()
        assert "square_root" in ops
        assert "word_problem" in ops
        assert "money" in ops
