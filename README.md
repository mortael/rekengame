# rekengame
rekengame

# 🧮 Rekengame Avontuur

Een educatief 3D-rekenspel voor kinderen van groep 5 en ouder (ca. 10+ jaar).

## Over het spel

Navigeer in een visuele 3D-wereld en versla vijanden door rekenopgaven op te lossen. Verzamel materialen, craft power-ups via de crafting-stations en overwin eindbazen om levels te voltooien!

### Soorten sommen
- ➕ **Optellen** – eenvoudig beginnen
- ➖ **Aftrekken** – pas op voor negatieve getallen!
- ✖️ **Tafels / Vermenigvuldigen** – van de 2 t/m de 12
- ➗ **Delen** – altijd exacte uitkomsten
- 📖 **Verhaalsommen** – context in het dagelijks leven
- 💰 **Rekenen met geld** – wisselgeld, totaalbedragen, splitsen
- √ **Worteltrekken** – alleen op Expert-niveau

### Moeilijkheidsgraden
| Niveau    | Getallen  | Tijdslimiet | Soorten sommen                        |
|-----------|-----------|-------------|---------------------------------------|
| Makkelijk | 1 – 20    | Geen        | Optellen, aftrekken                   |
| Normaal   | 1 – 100   | 45 sec      | + Vermenigvuldigen, geld              |
| Moeilijk  | 1 – 1000  | 30 sec      | + Delen, verhaalsommen                |
| Expert    | 1 – 10000 | 20 sec      | + Worteltrekken                       |

### Gameplay
- **WASD** – bewegen
- **Muis** – kijken
- **E** – interactie (vecht tegen vijanden, gebruik crafting-station)
- **C** – open crafting-menu
- **1–5** – gebruik power-up uit de snelbalk
- **Esc** – terug naar hoofdmenu

### Levels
1. 🌿 **Het Groene Woud** – bosomgeving, eenvoudige vijanden
2. 🏰 **De Stenen Vesting** – steenachtige muren, stevigere vijanden
3. ❄️ **De IJsvlakte** – ijzige omgeving, harder rekenwerk
4. 🌋 **De Vulkaanberg** – expert-niveau eindbazen

Elk level bevat **~6-12 reguliere vijanden** en **3 eindbazen**, elk met meerdere rekenfases.

### Power-ups (crafting)
| Item              | Recept                 | Effect                              |
|-------------------|------------------------|-------------------------------------|
| ❤️ Levensdrankje  | 2× kruid + 1× water    | Herstelt 1 levenspunt               |
| 🛡️ Schild         | 3× hout + 1× metaal    | Blokkeert de volgende fout          |
| ⏳ Tijdstop        | 2× kristal + 1× kruid  | Stopt de timer voor 1 vraag         |
| 💡 Hint-kaart     | 1× rol + 1× inkt       | Toont een hint bij de volgende vraag|
| ⭐ Dubbel Punten  | 2× goud + 1× kristal   | Verdubbelt punten voor volgende som |

## Installatie

```bash
pip install -r requirements.txt
python main.py
```

## Tests uitvoeren

```bash
python -m pytest tests/ -v
```

## Projectstructuur

```
main.py              – Startpunt
requirements.txt     – Afhankelijkheden
src/
  config.py          – Spelconstanten en moeilijkheidsgraden
  math_engine.py     – Generatie van rekenopgaven
  player.py          – Spelersmodel (levens, score, inventaris)
  enemy.py           – Vijanden en eindbazen
  crafting.py        – Crafting-systeem
  level_manager.py   – Levelbeheer en voortgang
  world.py           – 3D-wereld met Ursina
  ui.py              – Alle UI-panelen
  game.py            – Hoofd-controller (state machine)
tests/
  test_math_engine.py
  test_level_manager.py
  test_player.py
  test_crafting.py
```

