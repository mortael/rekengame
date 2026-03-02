"""Crafting system: craft power-ups from collected materials by solving math."""
from src.config import CRAFTING_RECIPES, ITEMS


class CraftingSystem:
    """Manages crafting recipes and the crafting process."""

    def __init__(self):
        self.recipes = CRAFTING_RECIPES

    def available_recipes(self, inventory: dict[str, int]) -> list[dict]:
        """Return recipes for which the player has enough materials."""
        available = []
        for recipe in self.recipes:
            if self._can_craft(recipe, inventory):
                available.append(recipe)
        return available

    def _can_craft(self, recipe: dict, inventory: dict[str, int]) -> bool:
        for material, qty in recipe["ingredients"]:
            if inventory.get(material, 0) < qty:
                return False
        return True

    def craft(self, recipe: dict, inventory: dict[str, int]) -> tuple[bool, str]:
        """
        Attempt to craft the item.
        Returns (success, message).
        Deducts materials from inventory dict in-place on success.
        """
        if not self._can_craft(recipe, inventory):
            ingredients_str = ", ".join(
                f"{qty}× {mat}" for mat, qty in recipe["ingredients"]
            )
            return False, f"Niet genoeg materialen. Nodig: {ingredients_str}"

        for material, qty in recipe["ingredients"]:
            inventory[material] -= qty

        result_key = recipe["result"]
        item_name = ITEMS[result_key]["name"]
        return True, f"Je hebt {item_name} gecraftd! ✨"

    def get_recipe_display(self, recipe: dict) -> str:
        """Human-readable recipe string."""
        ingredients_str = " + ".join(
            f"{qty}× {mat}" for mat, qty in recipe["ingredients"]
        )
        result_name = ITEMS[recipe["result"]]["name"]
        emoji = ITEMS[recipe["result"]]["emoji"]
        return f"{ingredients_str} → {emoji} {result_name}"

    def get_all_recipes(self) -> list[dict]:
        return self.recipes
