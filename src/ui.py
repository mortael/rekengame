"""All UI panels and overlays for the rekengame."""
import time
from ursina import (
    Entity, Text, Button, InputField, Quad, color, camera,
    Vec2, Vec3, destroy, invoke, mouse, Audio,
)
from src.config import ITEMS, GameState


def _panel(parent=None, **kw):
    defaults = dict(
        model="quad",
        color=color.rgba(20, 20, 40, 220),
        scale=(0.6, 0.5),
        position=(0, 0, -0.1),
    )
    defaults.update(kw)
    if parent:
        defaults["parent"] = parent
    return Entity(**defaults)


# ------------------------------------------------------------------ #
#  MAIN MENU                                                           #
# ------------------------------------------------------------------ #

class MainMenu:
    """Full-screen main menu with difficulty selection."""

    def __init__(self, on_play, on_quit):
        self._entities = []
        self.selected_difficulty = None

        bg = Entity(
            parent=camera.ui,
            model="quad",
            color=color.rgba(10, 10, 30, 255),
            scale=(2, 2),
        )
        self._entities.append(bg)

        title = Text(
            parent=camera.ui,
            text="🧮 Rekengame Avontuur",
            origin=(0, 0),
            scale=3,
            position=(0, 0.38),
            color=color.yellow,
        )
        self._entities.append(title)

        subtitle = Text(
            parent=camera.ui,
            text="Versla vijanden door sommen op te lossen!",
            origin=(0, 0),
            scale=1.4,
            position=(0, 0.28),
            color=color.white,
        )
        self._entities.append(subtitle)

        # Difficulty buttons
        diff_label = Text(
            parent=camera.ui,
            text="Kies je moeilijkheidsgraad:",
            origin=(0, 0),
            scale=1.4,
            position=(0, 0.14),
            color=color.light_gray,
        )
        self._entities.append(diff_label)

        difficulties = [
            ("Makkelijk", "easy"),
            ("Normaal", "medium"),
            ("Moeilijk", "hard"),
            ("Expert", "expert"),
        ]
        for i, (label, key) in enumerate(difficulties):
            btn = Button(
                parent=camera.ui,
                text=label,
                scale=(0.22, 0.06),
                position=(-0.34 + i * 0.23, 0.04),
                color=color.rgba(50, 80, 160, 230),
                highlight_color=color.rgba(80, 120, 220, 255),
                on_click=lambda k=key: self._select_difficulty(k),
            )
            self._entities.append(btn)

        play_btn = Button(
            parent=camera.ui,
            text="▶  Spelen",
            scale=(0.28, 0.07),
            position=(0, -0.1),
            color=color.rgba(30, 150, 60, 240),
            highlight_color=color.rgba(50, 200, 80, 255),
            on_click=on_play,
        )
        self._entities.append(play_btn)

        quit_btn = Button(
            parent=camera.ui,
            text="✖  Stoppen",
            scale=(0.22, 0.06),
            position=(0, -0.22),
            color=color.rgba(150, 30, 30, 220),
            highlight_color=color.rgba(200, 50, 50, 255),
            on_click=on_quit,
        )
        self._entities.append(quit_btn)

        controls_text = Text(
            parent=camera.ui,
            text="Bewegen: WASD  |  Kijken: Muis  |  Actie: E  |  Crafting: C  |  Item: 1-5",
            origin=(0, 0),
            scale=0.9,
            position=(0, -0.36),
            color=color.rgba(180, 180, 180, 200),
        )
        self._entities.append(controls_text)

        self._selected_label = Text(
            parent=camera.ui,
            text="Geselecteerd: Normaal",
            origin=(0, 0),
            scale=1.1,
            position=(0, -0.06),
            color=color.cyan,
        )
        self._entities.append(self._selected_label)
        self.selected_difficulty = "medium"

    def _select_difficulty(self, key: str) -> None:
        names = {"easy": "Makkelijk", "medium": "Normaal", "hard": "Moeilijk", "expert": "Expert"}
        self.selected_difficulty = key
        self._selected_label.text = f"Geselecteerd: {names.get(key, key)}"

    def destroy(self) -> None:
        for e in self._entities:
            destroy(e)
        self._entities.clear()


# ------------------------------------------------------------------ #
#  HUD (in-game heads-up display)                                      #
# ------------------------------------------------------------------ #

class HUD:
    """Displays health, score, level name, and interaction hint."""

    def __init__(self):
        self._entities = []

        # Health bar background
        self._health_bg = Entity(
            parent=camera.ui,
            model="quad",
            color=color.rgba(40, 0, 0, 200),
            scale=(0.24, 0.028),
            position=(-0.78, 0.45),
        )
        self._entities.append(self._health_bg)

        self._health_bar = Entity(
            parent=camera.ui,
            model="quad",
            color=color.rgba(220, 40, 40, 255),
            scale=(0.24, 0.028),
            position=(-0.78, 0.45),
            origin=(-0.5, 0),
        )
        self._entities.append(self._health_bar)

        self._health_text = Text(
            parent=camera.ui,
            text="❤️ 5/5",
            origin=(-0.5, 0),
            scale=1.1,
            position=(-0.88, 0.43),
            color=color.white,
        )
        self._entities.append(self._health_text)

        self._score_text = Text(
            parent=camera.ui,
            text="Punten: 0",
            origin=(0.5, 0),
            scale=1.2,
            position=(0.88, 0.45),
            color=color.yellow,
        )
        self._entities.append(self._score_text)

        self._level_text = Text(
            parent=camera.ui,
            text="Level 1",
            origin=(0, 0),
            scale=1.2,
            position=(0, 0.45),
            color=color.cyan,
        )
        self._entities.append(self._level_text)

        self._hint_text = Text(
            parent=camera.ui,
            text="",
            origin=(0, 0),
            scale=1.1,
            position=(0, -0.43),
            color=color.rgba(255, 255, 100, 220),
        )
        self._entities.append(self._hint_text)

        self._effects_text = Text(
            parent=camera.ui,
            text="",
            origin=(-0.5, 0),
            scale=0.9,
            position=(-0.88, 0.38),
            color=color.rgba(100, 255, 200, 220),
        )
        self._entities.append(self._effects_text)

    def update(self, player, level_name: str, interaction_hint: str = "") -> None:
        hp_ratio = player.health / player.max_health
        self._health_bar.scale_x = 0.24 * hp_ratio
        self._health_text.text = f"❤️ {player.health}/{player.max_health}"
        self._score_text.text = f"Punten: {player.score}"
        self._level_text.text = level_name
        self._hint_text.text = interaction_hint
        if player.active_effects:
            self._effects_text.text = "  ".join(player.active_effects)
        else:
            self._effects_text.text = ""

    def destroy(self) -> None:
        for e in self._entities:
            destroy(e)
        self._entities.clear()


# ------------------------------------------------------------------ #
#  MATH COMBAT UI                                                      #
# ------------------------------------------------------------------ #

class MathCombatUI:
    """
    Overlay panel shown during combat.
    Shows the math problem, optional timer, and an answer input.
    """

    def __init__(self, problem, opponent_name: str, on_submit):
        self._entities = []
        self._problem = problem
        self._on_submit = on_submit
        self._start_time = time.time()
        self._feedback_text = None

        # Dim background
        overlay = Entity(
            parent=camera.ui,
            model="quad",
            color=color.rgba(0, 0, 0, 160),
            scale=(2, 2),
            z=0.01,
        )
        self._entities.append(overlay)

        # Main panel
        panel = Entity(
            parent=camera.ui,
            model="quad",
            color=color.rgba(15, 20, 50, 240),
            scale=(0.72, 0.52),
            position=(0, 0),
            z=0.02,
        )
        self._entities.append(panel)

        # Opponent name header
        name_bg = Entity(
            parent=camera.ui,
            model="quad",
            color=color.rgba(150, 20, 20, 240),
            scale=(0.72, 0.07),
            position=(0, 0.235),
            z=0.03,
        )
        self._entities.append(name_bg)

        opponent_text = Text(
            parent=camera.ui,
            text=f"⚔️  {opponent_name}",
            origin=(0, 0),
            scale=1.5,
            position=(0, 0.232),
            color=color.white,
            z=0.04,
        )
        self._entities.append(opponent_text)

        # Question text (supports newlines)
        question_text = Text(
            parent=camera.ui,
            text=problem.question,
            origin=(0, 0),
            scale=2.0,
            position=(0, 0.09),
            color=color.yellow,
            z=0.04,
        )
        self._entities.append(question_text)

        # Answer input field
        self._input = InputField(
            parent=camera.ui,
            default_value="",
            scale=(0.28, 0.055),
            position=(0, -0.07),
            z=0.04,
            color=color.rgba(30, 30, 70, 240),
        )
        self._entities.append(self._input)
        self._input.active = True

        # Submit button
        submit_btn = Button(
            parent=camera.ui,
            text="✔ Antwoord",
            scale=(0.22, 0.055),
            position=(0, -0.145),
            color=color.rgba(30, 140, 60, 240),
            highlight_color=color.rgba(50, 200, 80, 255),
            on_click=self._submit,
            z=0.04,
        )
        self._entities.append(submit_btn)

        # Timer bar (only if timed)
        self._timer_bg = None
        self._timer_bar = None
        if problem.time_limit:
            self._timer_bg = Entity(
                parent=camera.ui,
                model="quad",
                color=color.rgba(60, 0, 0, 200),
                scale=(0.66, 0.022),
                position=(0, 0.195),
                z=0.04,
            )
            self._entities.append(self._timer_bg)
            self._timer_bar = Entity(
                parent=camera.ui,
                model="quad",
                color=color.rgba(255, 200, 0, 240),
                scale=(0.66, 0.022),
                position=(0, 0.195),
                origin=(-0.5, 0),
                z=0.05,
            )
            self._entities.append(self._timer_bar)

        # Feedback text
        self._feedback = Text(
            parent=camera.ui,
            text="",
            origin=(0, 0),
            scale=1.3,
            position=(0, -0.215),
            z=0.04,
            color=color.white,
        )
        self._entities.append(self._feedback)

        # Hint text (shown if player has hint power-up active)
        self._hint_text = Text(
            parent=camera.ui,
            text="",
            origin=(0, 0),
            scale=1.0,
            position=(0, -0.175),
            color=color.rgba(100, 255, 200, 220),
            z=0.04,
        )
        self._entities.append(self._hint_text)

        self._timed_out = False

    def show_hint(self) -> None:
        self._hint_text.text = f"💡 {self._problem.hint}"

    def update(self) -> bool:
        """
        Called every frame. Returns True if time ran out (unanswered).
        """
        if self._problem.time_limit and not self._timed_out:
            elapsed = time.time() - self._start_time
            ratio = max(0.0, 1.0 - elapsed / self._problem.time_limit)
            if self._timer_bar:
                self._timer_bar.scale_x = 0.66 * ratio
                # Colour: green → yellow → red
                if ratio > 0.5:
                    self._timer_bar.color = color.rgba(50, 220, 50, 240)
                elif ratio > 0.25:
                    self._timer_bar.color = color.rgba(255, 200, 0, 240)
                else:
                    self._timer_bar.color = color.rgba(255, 50, 50, 240)
            if ratio <= 0.0:
                self._timed_out = True
                return True
        return False

    def _submit(self) -> None:
        answer = self._input.value
        self._on_submit(answer)

    def show_feedback(self, correct: bool, correct_answer) -> None:
        if correct:
            self._feedback.text = "✅ Goed gedaan!"
            self._feedback.color = color.rgba(50, 255, 50, 255)
        else:
            self._feedback.text = f"❌ Fout! Het juiste antwoord was: {int(correct_answer) if correct_answer == int(correct_answer) else correct_answer}"
            self._feedback.color = color.rgba(255, 80, 80, 255)

    def get_answer(self) -> str:
        return self._input.value

    def destroy(self) -> None:
        for e in self._entities:
            destroy(e)
        self._entities.clear()


# ------------------------------------------------------------------ #
#  CRAFTING UI                                                         #
# ------------------------------------------------------------------ #

class CraftingUI:
    """Panel for selecting and crafting items from recipes."""

    def __init__(self, recipes: list, inventory: dict, on_craft, on_close):
        self._entities = []
        self._on_craft = on_craft
        self._on_close = on_close

        overlay = Entity(
            parent=camera.ui,
            model="quad",
            color=color.rgba(0, 0, 0, 160),
            scale=(2, 2),
            z=0.01,
        )
        self._entities.append(overlay)

        panel = Entity(
            parent=camera.ui,
            model="quad",
            color=color.rgba(20, 40, 20, 245),
            scale=(0.75, 0.62),
            z=0.02,
        )
        self._entities.append(panel)

        header = Text(
            parent=camera.ui,
            text="🔨  Crafting Station",
            origin=(0, 0),
            scale=1.8,
            position=(0, 0.265),
            color=color.rgba(100, 255, 100, 255),
            z=0.03,
        )
        self._entities.append(header)

        close_btn = Button(
            parent=camera.ui,
            text="✖",
            scale=(0.05, 0.045),
            position=(0.35, 0.265),
            color=color.rgba(160, 30, 30, 230),
            on_click=on_close,
            z=0.03,
        )
        self._entities.append(close_btn)

        if not recipes:
            no_recipe = Text(
                parent=camera.ui,
                text="Geen recepten beschikbaar.\nVerzamel meer materialen!",
                origin=(0, 0),
                scale=1.2,
                position=(0, 0),
                color=color.rgba(200, 200, 100, 255),
                z=0.03,
            )
            self._entities.append(no_recipe)
        else:
            for i, recipe in enumerate(recipes[:5]):
                result_key = recipe["result"]
                item = ITEMS[result_key]
                recipe_str = " + ".join(f"{q}×{m}" for m, q in recipe["ingredients"])
                label = f"{item['emoji']} {item['name']}\n  {recipe_str}"
                y_pos = 0.18 - i * 0.1
                btn = Button(
                    parent=camera.ui,
                    text=label,
                    scale=(0.64, 0.078),
                    position=(0, y_pos),
                    color=color.rgba(30, 80, 40, 220),
                    highlight_color=color.rgba(50, 130, 60, 255),
                    on_click=lambda r=recipe: on_craft(r),
                    z=0.03,
                )
                self._entities.append(btn)

        # Inventory display
        inv_str = "  ".join(f"{m}:{q}" for m, q in inventory.items() if q > 0) or "Leeg"
        inv_text = Text(
            parent=camera.ui,
            text=f"Inventaris: {inv_str}",
            origin=(0, 0),
            scale=0.95,
            position=(0, -0.265),
            color=color.rgba(180, 255, 180, 220),
            z=0.03,
        )
        self._entities.append(inv_text)

    def destroy(self) -> None:
        for e in self._entities:
            destroy(e)
        self._entities.clear()


# ------------------------------------------------------------------ #
#  BOSS INTRO SCREEN                                                   #
# ------------------------------------------------------------------ #

class BossIntroUI:
    """Dramatic boss introduction panel."""

    def __init__(self, boss_name: str, boss_title: str, on_continue):
        self._entities = []

        overlay = Entity(
            parent=camera.ui,
            model="quad",
            color=color.rgba(0, 0, 0, 200),
            scale=(2, 2),
            z=0.01,
        )
        self._entities.append(overlay)

        warning = Text(
            parent=camera.ui,
            text="⚠️  EINDBAAS  ⚠️",
            origin=(0, 0),
            scale=3,
            position=(0, 0.2),
            color=color.rgba(255, 50, 50, 255),
            z=0.02,
        )
        self._entities.append(warning)

        name_text = Text(
            parent=camera.ui,
            text=boss_name,
            origin=(0, 0),
            scale=2.2,
            position=(0, 0.06),
            color=color.rgba(255, 200, 0, 255),
            z=0.02,
        )
        self._entities.append(name_text)

        title_text = Text(
            parent=camera.ui,
            text=boss_title,
            origin=(0, 0),
            scale=1.4,
            position=(0, -0.06),
            color=color.white,
            z=0.02,
        )
        self._entities.append(title_text)

        cont_btn = Button(
            parent=camera.ui,
            text="⚔️  Vecht!",
            scale=(0.26, 0.065),
            position=(0, -0.22),
            color=color.rgba(180, 30, 30, 240),
            highlight_color=color.rgba(240, 60, 60, 255),
            on_click=on_continue,
            z=0.02,
        )
        self._entities.append(cont_btn)

    def destroy(self) -> None:
        for e in self._entities:
            destroy(e)
        self._entities.clear()


# ------------------------------------------------------------------ #
#  LEVEL COMPLETE SCREEN                                               #
# ------------------------------------------------------------------ #

class LevelCompleteUI:
    """Shown when the player defeats all bosses in a level."""

    def __init__(self, level_name: str, score: int, accuracy: float,
                 on_next, on_quit, is_final: bool = False):
        self._entities = []

        overlay = Entity(
            parent=camera.ui,
            model="quad",
            color=color.rgba(0, 0, 0, 200),
            scale=(2, 2),
            z=0.01,
        )
        self._entities.append(overlay)

        header = "🏆  Gewonnen!" if is_final else "🎉  Level Voltooid!"
        title_text = Text(
            parent=camera.ui,
            text=header,
            origin=(0, 0),
            scale=3,
            position=(0, 0.28),
            color=color.yellow,
            z=0.02,
        )
        self._entities.append(title_text)

        level_text = Text(
            parent=camera.ui,
            text=level_name,
            origin=(0, 0),
            scale=1.8,
            position=(0, 0.14),
            color=color.cyan,
            z=0.02,
        )
        self._entities.append(level_text)

        stats_text = Text(
            parent=camera.ui,
            text=f"Score: {score}  |  Nauwkeurigheid: {accuracy}%",
            origin=(0, 0),
            scale=1.3,
            position=(0, 0.02),
            color=color.white,
            z=0.02,
        )
        self._entities.append(stats_text)

        if is_final:
            msg = "Gefeliciteerd! Je hebt het spel uitgespeeld! 🌟"
        else:
            msg = "Klaar voor het volgende avontuur?"
        msg_text = Text(
            parent=camera.ui,
            text=msg,
            origin=(0, 0),
            scale=1.2,
            position=(0, -0.1),
            color=color.light_gray,
            z=0.02,
        )
        self._entities.append(msg_text)

        if not is_final:
            next_btn = Button(
                parent=camera.ui,
                text="▶  Volgend Level",
                scale=(0.3, 0.065),
                position=(0, -0.24),
                color=color.rgba(30, 140, 60, 240),
                on_click=on_next,
                z=0.02,
            )
            self._entities.append(next_btn)

        quit_btn = Button(
            parent=camera.ui,
            text="🏠  Hoofdmenu",
            scale=(0.26, 0.06),
            position=(0, -0.33),
            color=color.rgba(60, 60, 130, 220),
            on_click=on_quit,
            z=0.02,
        )
        self._entities.append(quit_btn)

    def destroy(self) -> None:
        for e in self._entities:
            destroy(e)
        self._entities.clear()


# ------------------------------------------------------------------ #
#  GAME OVER SCREEN                                                    #
# ------------------------------------------------------------------ #

class GameOverUI:
    """Shown when player health reaches zero."""

    def __init__(self, score: int, on_retry, on_quit):
        self._entities = []

        overlay = Entity(
            parent=camera.ui,
            model="quad",
            color=color.rgba(0, 0, 0, 220),
            scale=(2, 2),
            z=0.01,
        )
        self._entities.append(overlay)

        title_text = Text(
            parent=camera.ui,
            text="💀  Game Over",
            origin=(0, 0),
            scale=3.5,
            position=(0, 0.2),
            color=color.rgba(255, 50, 50, 255),
            z=0.02,
        )
        self._entities.append(title_text)

        score_text = Text(
            parent=camera.ui,
            text=f"Je eindscore: {score}",
            origin=(0, 0),
            scale=1.5,
            position=(0, 0.04),
            color=color.white,
            z=0.02,
        )
        self._entities.append(score_text)

        retry_btn = Button(
            parent=camera.ui,
            text="🔄  Opnieuw Proberen",
            scale=(0.32, 0.065),
            position=(0, -0.12),
            color=color.rgba(30, 140, 60, 240),
            on_click=on_retry,
            z=0.02,
        )
        self._entities.append(retry_btn)

        quit_btn = Button(
            parent=camera.ui,
            text="🏠  Hoofdmenu",
            scale=(0.26, 0.06),
            position=(0, -0.22),
            color=color.rgba(60, 60, 130, 220),
            on_click=on_quit,
            z=0.02,
        )
        self._entities.append(quit_btn)

    def destroy(self) -> None:
        for e in self._entities:
            destroy(e)
        self._entities.clear()


# ------------------------------------------------------------------ #
#  POWER-UP BAR                                                        #
# ------------------------------------------------------------------ #

class PowerUpBar:
    """Small horizontal bar showing available power-ups and key shortcuts."""

    def __init__(self):
        self._entities = []
        self._item_texts: list[Text] = []

        bg = Entity(
            parent=camera.ui,
            model="quad",
            color=color.rgba(10, 10, 30, 180),
            scale=(0.55, 0.055),
            position=(0, -0.47),
            z=0.01,
        )
        self._entities.append(bg)

        for i in range(5):
            t = Text(
                parent=camera.ui,
                text=f"[{i + 1}] -",
                origin=(0, 0),
                scale=1.0,
                position=(-0.22 + i * 0.11, -0.47),
                color=color.rgba(200, 200, 200, 220),
                z=0.02,
            )
            self._item_texts.append(t)
            self._entities.append(t)

    def update(self, power_ups: dict) -> None:
        from src.config import ITEMS
        items = list(ITEMS.keys())
        for i, text_entity in enumerate(self._item_texts):
            if i < len(items):
                key = items[i]
                qty = power_ups.get(key, 0)
                emoji = ITEMS[key]["emoji"]
                if qty > 0:
                    text_entity.text = f"[{i + 1}] {emoji}×{qty}"
                    text_entity.color = color.rgba(255, 255, 100, 240)
                else:
                    text_entity.text = f"[{i + 1}] -"
                    text_entity.color = color.rgba(120, 120, 120, 180)

    def destroy(self) -> None:
        for e in self._entities:
            destroy(e)
        self._entities.clear()
