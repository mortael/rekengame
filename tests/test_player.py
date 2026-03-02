"""Tests for the Player model."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from src.player import Player
from src.config import PLAYER_MAX_HEALTH


@pytest.fixture
def player():
    return Player()


class TestPlayerHealth:
    def test_starts_at_max_health(self, player):
        assert player.health == PLAYER_MAX_HEALTH
        assert player.is_alive()

    def test_take_damage(self, player):
        player.take_damage(1)
        assert player.health == PLAYER_MAX_HEALTH - 1

    def test_die_when_health_zero(self, player):
        player.health = 1
        alive = player.take_damage(1)
        assert not alive
        assert not player.is_alive()

    def test_heal_restores_health(self, player):
        player.health = 2
        player.heal(2)
        assert player.health == 4

    def test_heal_does_not_exceed_max(self, player):
        player.heal(100)
        assert player.health == PLAYER_MAX_HEALTH

    def test_shield_blocks_damage(self, player):
        player.active_effects.append("shield")
        original = player.health
        player.take_damage(1)
        assert player.health == original
        assert "shield" not in player.active_effects


class TestPlayerScore:
    def test_initial_score_zero(self, player):
        assert player.score == 0

    def test_add_score(self, player):
        player.add_score(100)
        assert player.score == 100

    def test_double_score_effect(self, player):
        player.active_effects.append("double_score")
        added = player.add_score(100)
        assert added == 200
        assert player.score == 200
        assert "double_score" not in player.active_effects


class TestPlayerInventory:
    def test_add_material(self, player):
        player.add_material("herb", 3)
        assert player.inventory["herb"] == 3

    def test_has_materials(self, player):
        player.add_material("herb", 2)
        assert player.has_materials([("herb", 2)])
        assert not player.has_materials([("herb", 3)])

    def test_consume_materials(self, player):
        player.add_material("herb", 3)
        player.add_material("water", 2)
        result = player.consume_materials([("herb", 2), ("water", 1)])
        assert result
        assert player.inventory["herb"] == 1
        assert player.inventory["water"] == 1

    def test_consume_fails_insufficient(self, player):
        player.add_material("herb", 1)
        result = player.consume_materials([("herb", 2)])
        assert not result
        assert player.inventory["herb"] == 1


class TestPlayerPowerUps:
    def test_add_power_up(self, player):
        player.add_power_up("health_potion")
        assert player.power_ups["health_potion"] == 1

    def test_use_health_potion(self, player):
        player.health = 3
        player.add_power_up("health_potion")
        assert player.use_power_up("health_potion")
        assert player.health == 4

    def test_use_shield(self, player):
        player.add_power_up("shield")
        player.use_power_up("shield")
        assert "shield" in player.active_effects

    def test_use_nonexistent_item(self, player):
        assert not player.use_power_up("health_potion")


class TestPlayerStats:
    def test_accuracy_100_at_start(self, player):
        assert player.accuracy_percent() == 100.0

    def test_accuracy_after_answers(self, player):
        player.record_answer(True)
        player.record_answer(True)
        player.record_answer(False)
        assert player.accuracy_percent() == pytest.approx(66.7, abs=0.1)

    def test_correct_streak(self, player):
        player.record_answer(True)
        player.record_answer(True)
        assert player.correct_streak == 2
        player.record_answer(False)
        assert player.correct_streak == 0

    def test_operation_accuracy_tracking(self, player):
        player.record_answer(True, "addition")
        player.record_answer(False, "addition")
        player.record_answer(True, "division")
        assert player.operation_accuracy("addition") == 50.0
        assert player.operation_accuracy("division") == 100.0

    def test_weakest_operations(self, player):
        player.record_answer(False, "division")
        player.record_answer(True, "division")
        player.record_answer(False, "money")
        player.record_answer(False, "money")
        player.record_answer(True, "addition")
        weakest = player.weakest_operations()
        assert weakest[0] == "money"

    def test_performance_summary_contains_operations(self, player):
        player.record_answer(True, "addition")
        player.record_answer(False, "addition")
        summary = player.performance_summary()
        assert summary["total_correct"] == 1
        assert summary["total_wrong"] == 1
        assert "addition" in summary["operations"]
        assert summary["operations"]["addition"]["accuracy"] == 50.0
