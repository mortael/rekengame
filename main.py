"""Entry point for Rekengame Avontuur."""
import sys
import os

# Ensure src/ is importable regardless of where the script is run from
sys.path.insert(0, os.path.dirname(__file__))

from ursina import Ursina, window, application
from src.config import WINDOW_TITLE, WINDOW_WIDTH, WINDOW_HEIGHT
from src.game import Game


app = Ursina(
    title=WINDOW_TITLE,
    borderless=False,
    fullscreen=False,
    size=(WINDOW_WIDTH, WINDOW_HEIGHT),
)

window.title = WINDOW_TITLE

game = Game()


def update():
    game.update()


def input(key):
    game.input(key)


if __name__ == "__main__":
    app.run()
