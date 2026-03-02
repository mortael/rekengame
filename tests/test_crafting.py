"""Tests for the crafting system."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from src.crafting import CraftingSystem
from src.config import CRAFTING_RECIPES, ITEMS


@pytest.fixture
def crafting():
    return CraftingSystem()


@pytest.fixture
def full_inventory():
    return {
        "herb": 10,
        "water": 10,
        "wood": 10,
        "metal": 10,
        "crystal": 10,
        "scroll": 10,
        "ink": 10,
        "gold": 10,
    }


class TestAvailableRecipes:
    def test_all_available_with_full_inventory(self, crafting, full_inventory):
        available = crafting.available_recipes(full_inventory)
        assert len(available) == len(CRAFTING_RECIPES)

    def test_none_available_with_empty_inventory(self, crafting):
        available = crafting.available_recipes({})
        assert len(available) == 0

    def test_partial_inventory(self, crafting):
        inventory = {"herb": 2, "water": 1}
        available = crafting.available_recipes(inventory)
        # Only health_potion (herb×2, water×1) should be craftable
        assert len(available) >= 1
        assert any(r["result"] == "health_potion" for r in available)


class TestCraft:
    def test_craft_health_potion(self, crafting, full_inventory):
        recipe = next(r for r in CRAFTING_RECIPES if r["result"] == "health_potion")
        success, msg = crafting.craft(recipe, full_inventory)
        assert success
        assert "Levensdrankje" in msg

    def test_craft_deducts_materials(self, crafting, full_inventory):
        recipe = next(r for r in CRAFTING_RECIPES if r["result"] == "health_potion")
        crafting.craft(recipe, full_inventory)
        assert full_inventory["herb"] == 8  # deducted 2
        assert full_inventory["water"] == 9  # deducted 1

    def test_craft_fails_without_materials(self, crafting):
        recipe = next(r for r in CRAFTING_RECIPES if r["result"] == "health_potion")
        success, msg = crafting.craft(recipe, {})
        assert not success
        assert "Niet genoeg" in msg

    def test_craft_all_recipes(self, crafting, full_inventory):
        for recipe in CRAFTING_RECIPES:
            success, _ = crafting.craft(recipe, full_inventory)
            assert success


class TestRecipeDisplay:
    def test_display_contains_result_name(self, crafting):
        recipe = next(r for r in CRAFTING_RECIPES if r["result"] == "health_potion")
        display = crafting.get_recipe_display(recipe)
        assert "Levensdrankje" in display

    def test_display_contains_ingredients(self, crafting):
        recipe = next(r for r in CRAFTING_RECIPES if r["result"] == "health_potion")
        display = crafting.get_recipe_display(recipe)
        assert "herb" in display
        assert "water" in display

    def test_all_recipes_have_display(self, crafting):
        for recipe in CRAFTING_RECIPES:
            display = crafting.get_recipe_display(recipe)
            assert isinstance(display, str) and len(display) > 0


class TestAllRecipes:
    def test_get_all_recipes_returns_all(self, crafting):
        all_r = crafting.get_all_recipes()
        assert len(all_r) == len(CRAFTING_RECIPES)

    def test_each_recipe_has_math_type(self, crafting):
        for recipe in crafting.get_all_recipes():
            assert "math_type" in recipe
            assert recipe["math_type"] in (
                "addition", "subtraction", "multiplication", "division",
                "word_problem", "money", "square_root",
            )

    def test_each_result_item_is_in_items_config(self, crafting):
        for recipe in crafting.get_all_recipes():
            assert recipe["result"] in ITEMS
