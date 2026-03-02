# 🧮 Rekengame Avontuur

Een educatief 3D-rekenspel voor kinderen van groep 5 en ouder (ca. 10+ jaar), gebouwd met **Python + Ursina**.

## Features

- 3D-verkenning met combat op basis van rekenopgaven.
- Meerdere moeilijkheidsniveaus met oplopende tijddruk.
- Crafting-systeem met materialen, recepten en power-ups.
- Meerdere levels met reguliere vijanden en eindbazen.
- Leergerichte statistieken per rekentype (nieuw).

## Rekenopgaven

- ➕ Optellen
- ➖ Aftrekken
- ✖️ Vermenigvuldigen (tafels)
- ➗ Delen
- 📖 Verhaalsommen
- 💰 Geldrekenen
- √ Worteltrekken (expert)

## Installatie

```bash
pip install -r requirements.txt
```

## Starten

```bash
python main.py
```

## Tests

```bash
python -m pytest tests/ -v
```

## Projectstructuur

```text
main.py
src/
  config.py          # game-instellingen en constanten
  game.py            # centrale state machine
  world.py           # 3D-wereld en interactiepunten
  math_engine.py     # generatie van rekenproblemen
  player.py          # spelerstatus + leerstatistieken
  level_manager.py   # level-, vijand- en baasbeheer
  crafting.py        # recepten en crafting-flow
  ui.py              # UI-panelen
tests/
  test_math_engine.py
  test_player.py
  test_level_manager.py
  test_crafting.py
docs/
  PROJECT_GUIDE.md   # uitgebreide architectuur- en uitbreidingsgids
```

## Nieuwe uitbreiding: leerstatistieken

De spelerlogica ondersteunt nu gerichtere feedback:

- registratie van correcte/foute antwoorden per operatie;
- berekening van nauwkeurigheid per operatie;
- detectie van zwakste rekentypes om gerichter te oefenen;
- samenvattend voortgangsoverzicht via `Game.generate_progress_report()`.

Zie `docs/PROJECT_GUIDE.md` voor uitbreidingsideeën zoals adaptieve moeilijkheid of het opslaan van voortgang per speler.
