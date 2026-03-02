# Rekengame Avontuur – Projectgids

Deze gids beschrijft hoe het project intern is opgebouwd en hoe je het kunt uitbreiden.

## Architectuur in het kort

- `main.py` start Ursina en routeert `update()` en `input()` naar de `Game`-controller.
- `src/game.py` bevat de state machine met alle spelmodi (menu, spelen, combat, crafting, game over).
- `src/world.py` bouwt de 3D-wereld en beheert interactieve markers (vijanden, bazen, crafting).
- `src/math_engine.py` genereert opgaven op basis van moeilijkheid en type som.
- `src/player.py` beheert leven, score, inventaris, power-ups en leerstatistieken.
- `src/level_manager.py` verzorgt levelconfiguratie, vijanden en bazen.
- `src/ui.py` bevat de visuele panelen (HUD, combat, crafting, menu).

## Nieuwe uitbreiding: leerstatistieken per rekentype

De `Player` houdt nu niet alleen totaalprestaties bij, maar ook resultaten per rekentype:

- `record_answer(correct, operation=...)` registreert goede/foute antwoorden per operatie.
- `operation_accuracy(operation)` geeft nauwkeurigheid voor één rekentype terug.
- `weakest_operations()` geeft zwakste rekentypes terug voor extra oefening.
- `performance_summary()` levert één samenvattend object voor rapportage/UI.

Daarnaast biedt `Game.generate_progress_report()` een kant-en-klaar tekstrapport dat je in een UI-scherm of exportfunctie kunt gebruiken.

## Aanbevolen uitbreidingen

1. **Adaptieve moeilijkheid**
   - Gebruik `weakest_operations()` om vaker opgaven uit zwakke categorieën te kiezen.
2. **Opslaan van voortgang**
   - Schrijf `performance_summary()` weg naar JSON per spelerprofiel.
3. **Docent/ouder-dashboard**
   - Toon trends per sessie: nauwkeurigheid, streak, meest geoefende type.
4. **UI-rapportscherm**
   - Voeg een extra paneel toe in `src/ui.py` dat `generate_progress_report()` toont.

## Teststrategie

- Unit-tests in `tests/` valideren kernlogica van:
  - `MathEngine`
  - `Player`
  - `CraftingSystem`
  - `LevelManager`
- Nieuwe statistiekfuncties zijn toegevoegd aan `tests/test_player.py`.

## Development workflow

```bash
pip install -r requirements.txt
python -m pytest -v
python main.py
```

