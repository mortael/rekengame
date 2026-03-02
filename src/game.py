"""Main game controller: state machine connecting all subsystems."""
import time
from ursina import (
    Entity, FirstPersonController, camera, mouse,
    application, invoke, color, held_keys, Text, destroy, Vec2,
)

from src.config import (
    GameState, Difficulty, LEVEL_CONFIGS, ITEMS, WINDOW_TITLE,
    WINDOW_WIDTH, WINDOW_HEIGHT,
)
from src.math_engine import MathEngine
from src.player import Player
from src.level_manager import LevelManager
from src.crafting import CraftingSystem
from src.world import World
from src.ui import (
    MainMenu, HUD, MathCombatUI, CraftingUI,
    BossIntroUI, LevelCompleteUI, GameOverUI, PowerUpBar,
)

DIFFICULTY_MAP = {
    "easy": Difficulty.EASY,
    "medium": Difficulty.MEDIUM,
    "hard": Difficulty.HARD,
    "expert": Difficulty.EXPERT,
}


class Game:
    """Central game controller managing state, player, world and UI."""

    def __init__(self):
        self.state = GameState.MENU
        self._difficulty_key = "medium"

        # Core subsystems (initialised per game start)
        self.player: Player | None = None
        self.level_manager: LevelManager | None = None
        self.math_engine: MathEngine | None = None
        self.crafting_system = CraftingSystem()
        self.world: World | None = None
        self.fps_controller: FirstPersonController | None = None

        # Active UI panels
        self._menu: MainMenu | None = None
        self._hud: HUD | None = None
        self._power_up_bar: PowerUpBar | None = None
        self._combat_ui: MathCombatUI | None = None
        self._crafting_ui: CraftingUI | None = None
        self._boss_intro_ui: BossIntroUI | None = None
        self._level_complete_ui: LevelCompleteUI | None = None
        self._game_over_ui: GameOverUI | None = None

        # Combat state
        self._combat_target = None     # EnemyMarker or BossMarker
        self._combat_problem = None
        self._boss_problem_index = 0

        # Interaction cooldown
        self._last_interact_time = 0.0
        self._interact_cooldown = 0.5  # seconds

        # Show main menu
        self._show_menu()

    # ------------------------------------------------------------------ #
    #  Main update loop (called every frame by Ursina)                   #
    # ------------------------------------------------------------------ #

    def update(self) -> None:
        if self.state == GameState.PLAYING:
            self._update_playing()
        elif self.state == GameState.COMBAT:
            self._update_combat()

    def input(self, key: str) -> None:
        if self.state == GameState.PLAYING:
            self._input_playing(key)
        elif self.state == GameState.COMBAT:
            self._input_combat(key)

    # ------------------------------------------------------------------ #
    #  MENU state                                                          #
    # ------------------------------------------------------------------ #

    def _show_menu(self) -> None:
        self.state = GameState.MENU
        mouse.locked = False
        self._menu = MainMenu(
            on_play=self._start_game,
            on_quit=application.quit,
        )

    def _start_game(self) -> None:
        if self._menu:
            self._difficulty_key = self._menu.selected_difficulty or "medium"
            self._menu.destroy()
            self._menu = None
        self._init_level(0)

    # ------------------------------------------------------------------ #
    #  Level initialisation                                                #
    # ------------------------------------------------------------------ #

    def _init_level(self, level_index: int) -> None:
        """Set up a new level from scratch."""
        self._cleanup_level()

        difficulty = DIFFICULTY_MAP.get(self._difficulty_key, Difficulty.MEDIUM)
        self.player = Player()
        self.level_manager = LevelManager(difficulty)
        self.level_manager.current_level_index = level_index
        self.math_engine = MathEngine(difficulty)

        cfg = self.level_manager.current_level
        world_size = cfg["world_size"]

        # Generate spawn positions
        all_positions = LevelManager.generate_positions(world_size, 30, min_dist=3.0)
        enemy_positions = all_positions[: cfg["num_regular_enemies"]]
        boss_positions = all_positions[cfg["num_regular_enemies"]: cfg["num_regular_enemies"] + cfg["num_bosses"]]

        enemies = self.level_manager.spawn_enemies(enemy_positions)
        bosses = self.level_manager.spawn_bosses(boss_positions)

        # Build 3D world
        self.world = World(cfg)
        self.world.build(enemies, bosses)

        # Set up first-person controller
        spawn = self.world.get_player_spawn()
        self.fps_controller = FirstPersonController(
            position=spawn,
            gravity=0,
            speed=5,
        )
        try:
            self.fps_controller.cursor.visible = False
        except AttributeError:
            pass

        # UI
        self._hud = HUD()
        self._power_up_bar = PowerUpBar()

        self.state = GameState.PLAYING
        mouse.locked = True

    def _cleanup_level(self) -> None:
        if self.world:
            self.world.destroy_all()
            self.world = None
        if self.fps_controller:
            destroy(self.fps_controller)
            self.fps_controller = None
        self._destroy_all_ui()

    def _destroy_all_ui(self) -> None:
        for attr in [
            "_hud", "_power_up_bar", "_combat_ui", "_crafting_ui",
            "_boss_intro_ui", "_level_complete_ui", "_game_over_ui", "_menu",
        ]:
            ui = getattr(self, attr)
            if ui:
                ui.destroy()
                setattr(self, attr, None)

    # ------------------------------------------------------------------ #
    #  PLAYING state                                                       #
    # ------------------------------------------------------------------ #

    def _update_playing(self) -> None:
        if not self.fps_controller or not self.world:
            return

        player_pos = self.fps_controller.position
        hint = ""

        # Check for nearby entities
        enemy_marker = self.world.get_nearby_enemy(player_pos)
        boss_marker = self.world.get_nearby_boss(player_pos)
        craft_station = self.world.get_nearby_crafting_station(player_pos)

        if enemy_marker:
            hint = f"[E] Vecht tegen {enemy_marker.enemy_data.name}"
        elif boss_marker:
            hint = f"[E] Vecht tegen EINDBAAS: {boss_marker.boss_data.name}"
        elif craft_station:
            hint = "[E] Gebruik Crafting Station  |  [C] Crafting"

        if self._hud:
            level_name = f"Level {self.level_manager.level_number}: {self.level_manager.level_name}"
            self._hud.update(self.player, level_name, hint)
        if self._power_up_bar:
            self._power_up_bar.update(self.player.power_ups)

    def _input_playing(self, key: str) -> None:
        now = time.time()
        if now - self._last_interact_time < self._interact_cooldown:
            return

        player_pos = self.fps_controller.position if self.fps_controller else None
        if player_pos is None:
            return

        if key == "e":
            self._last_interact_time = now
            enemy_marker = self.world.get_nearby_enemy(player_pos)
            boss_marker = self.world.get_nearby_boss(player_pos)
            craft_station = self.world.get_nearby_crafting_station(player_pos)

            if boss_marker:
                self._start_boss_intro(boss_marker)
            elif enemy_marker:
                self._start_combat(enemy_marker, is_boss=False)
            elif craft_station:
                self._open_crafting()

        elif key == "c":
            self._last_interact_time = now
            self._open_crafting()

        elif key in ("1", "2", "3", "4", "5"):
            idx = int(key) - 1
            items_list = list(ITEMS.keys())
            if idx < len(items_list):
                item_key = items_list[idx]
                if self.player.use_power_up(item_key):
                    pass  # effect applied silently

        elif key == "escape":
            self._show_menu()

    # ------------------------------------------------------------------ #
    #  COMBAT state                                                        #
    # ------------------------------------------------------------------ #

    def _start_combat(self, marker, is_boss: bool = False) -> None:
        self.state = GameState.COMBAT
        mouse.locked = False

        self._combat_target = marker
        opponent = marker.boss_data if is_boss else marker.enemy_data
        scale = opponent.difficulty_scale

        if is_boss:
            problem = self.math_engine.generate_boss_problem(self._boss_problem_index, scale)
        else:
            problem = self.math_engine.generate(scale=scale)

        self._combat_problem = problem

        self._combat_ui = MathCombatUI(
            problem=problem,
            opponent_name=opponent.name,
            on_submit=self._on_combat_submit,
        )

        # Show hint if player has hint active
        if "hint" in self.player.active_effects:
            self._combat_ui.show_hint()
            self.player.active_effects.remove("hint")

    def _start_boss_intro(self, boss_marker) -> None:
        self.state = GameState.BOSS_INTRO
        mouse.locked = False
        self._combat_target = boss_marker
        self._boss_problem_index = 0
        boss = boss_marker.boss_data
        self._boss_intro_ui = BossIntroUI(
            boss_name=boss.name,
            boss_title=boss.special_title,
            on_continue=self._on_boss_intro_continue,
        )

    def _on_boss_intro_continue(self) -> None:
        if self._boss_intro_ui:
            self._boss_intro_ui.destroy()
            self._boss_intro_ui = None
        self._start_combat(self._combat_target, is_boss=True)

    def _update_combat(self) -> None:
        if self._combat_ui:
            timed_out = self._combat_ui.update()
            if timed_out:
                self._handle_wrong_answer()

    def _input_combat(self, key: str) -> None:
        if key == "enter" and self._combat_ui:
            answer = self._combat_ui.get_answer()
            self._on_combat_submit(answer)

    def _on_combat_submit(self, answer: str) -> None:
        if not self._combat_problem or not self._combat_ui:
            return

        problem = self._combat_problem
        correct = problem.check_answer(answer)
        self.player.record_answer(correct)

        self._combat_ui.show_feedback(correct, problem.answer)

        if correct:
            self._handle_correct_answer()
        else:
            self._handle_wrong_answer()

    def _handle_correct_answer(self) -> None:
        target = self._combat_target
        is_boss = hasattr(target, "boss_data")
        opponent = target.boss_data if is_boss else target.enemy_data

        opponent.take_damage(1)
        score_gained = self.player.add_score(100 if is_boss else 50)

        if opponent.is_defeated:
            # Collect drops
            for drop in opponent.get_drops():
                self.player.add_material(drop)
            self.world.refresh_markers()
            invoke(self._end_combat, delay=0.8)

            # Check win condition after brief delay
            invoke(self._check_level_complete, delay=1.0)
        elif is_boss and not opponent.is_defeated:
            # Boss needs more hits
            self._boss_problem_index += 1
            invoke(self._continue_boss_fight, delay=0.8)
        else:
            invoke(self._end_combat, delay=0.8)

    def _handle_wrong_answer(self) -> None:
        alive = self.player.take_damage(1)
        if self._combat_ui:
            self._combat_ui.show_feedback(False, self._combat_problem.answer)
        invoke(self._end_combat, delay=0.8)
        if not alive:
            invoke(self._trigger_game_over, delay=1.0)

    def _continue_boss_fight(self) -> None:
        if self._combat_ui:
            self._combat_ui.destroy()
            self._combat_ui = None
        self._start_combat(self._combat_target, is_boss=True)

    def _end_combat(self) -> None:
        if self._combat_ui:
            self._combat_ui.destroy()
            self._combat_ui = None
        self._combat_target = None
        self._combat_problem = None
        if self.player.is_alive():
            self.state = GameState.PLAYING
            mouse.locked = True

    # ------------------------------------------------------------------ #
    #  CRAFTING state                                                      #
    # ------------------------------------------------------------------ #

    def _open_crafting(self) -> None:
        self.state = GameState.CRAFTING
        mouse.locked = False

        available = self.crafting_system.available_recipes(self.player.inventory)
        all_recipes = self.crafting_system.get_all_recipes()
        # Show all recipes, but only craftable ones should be clickable
        self._crafting_ui = CraftingUI(
            recipes=available if available else all_recipes,
            inventory=self.player.inventory,
            on_craft=self._on_craft_selected,
            on_close=self._close_crafting,
        )

    def _on_craft_selected(self, recipe: dict) -> None:
        """First show a math problem, then craft on correct answer."""
        if self._crafting_ui:
            self._crafting_ui.destroy()
            self._crafting_ui = None

        op = recipe.get("math_type", "addition")
        problem = self.math_engine.generate(op)
        self._combat_problem = problem
        self._pending_recipe = recipe

        self._combat_ui = MathCombatUI(
            problem=problem,
            opponent_name=f"Crafting: {recipe['description']}",
            on_submit=self._on_crafting_math_submit,
        )
        self.state = GameState.COMBAT

    def _on_crafting_math_submit(self, answer: str) -> None:
        if not self._combat_problem:
            return
        correct = self._combat_problem.check_answer(answer)
        if correct:
            success, msg = self.crafting_system.craft(
                self._pending_recipe, self.player.inventory
            )
            if success:
                result_key = self._pending_recipe["result"]
                self.player.add_power_up(result_key)
            self._combat_ui.show_feedback(True, self._combat_problem.answer)
        else:
            self._combat_ui.show_feedback(False, self._combat_problem.answer)
        self._pending_recipe = None
        invoke(self._end_crafting_combat, delay=0.8)

    def _end_crafting_combat(self) -> None:
        if self._combat_ui:
            self._combat_ui.destroy()
            self._combat_ui = None
        self._combat_problem = None
        self.state = GameState.PLAYING
        mouse.locked = True

    def _close_crafting(self) -> None:
        if self._crafting_ui:
            self._crafting_ui.destroy()
            self._crafting_ui = None
        self.state = GameState.PLAYING
        mouse.locked = True

    # ------------------------------------------------------------------ #
    #  Level complete / Game over                                          #
    # ------------------------------------------------------------------ #

    def _check_level_complete(self) -> None:
        if self.level_manager.all_bosses_defeated():
            self._show_level_complete()

    def _show_level_complete(self) -> None:
        self.state = GameState.LEVEL_COMPLETE
        mouse.locked = False

        # Freeze player
        if self.fps_controller:
            self.fps_controller.enabled = False

        is_final = self.level_manager.is_last_level
        self._level_complete_ui = LevelCompleteUI(
            level_name=self.level_manager.level_name,
            score=self.player.score,
            accuracy=self.player.accuracy_percent(),
            on_next=self._next_level,
            on_quit=self._show_menu,
            is_final=is_final,
        )

    def _next_level(self) -> None:
        if self._level_complete_ui:
            self._level_complete_ui.destroy()
            self._level_complete_ui = None
        next_index = self.level_manager.current_level_index + 1
        # Preserve player score across levels
        old_score = self.player.score if self.player else 0
        self._init_level(next_index)
        if self.player:
            self.player.score = old_score

    def _trigger_game_over(self) -> None:
        self.state = GameState.GAME_OVER
        mouse.locked = False
        if self.fps_controller:
            self.fps_controller.enabled = False
        self._game_over_ui = GameOverUI(
            score=self.player.score if self.player else 0,
            on_retry=self._retry,
            on_quit=self._show_menu,
        )

    def _retry(self) -> None:
        if self._game_over_ui:
            self._game_over_ui.destroy()
            self._game_over_ui = None
        level_index = self.level_manager.current_level_index if self.level_manager else 0
        self._init_level(level_index)
