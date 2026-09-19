# Snake

A small Snake game written in Python with tkinter. It runs in a normal window and needs no extra packages.

## Run it

You need Python 3.8 or newer. tkinter is bundled with the Windows and macOS installers from python.org. On some Linux distros you have to install it separately (`sudo apt install python3-tk` on Debian and Ubuntu).

```bash
python snake.py
```

## Controls

| Key | Action |
| --- | --- |
| Arrow keys or W A S D | Move |
| Space | Pause or resume |
| R | Restart |
| Esc | Quit |

## How it plays

The board is 20 by 20 squares. Eating food grows the snake by one square and adds a point. The game speeds up a little with every food until it hits a speed limit. Running into a wall or your own body ends the round. Your best score is saved in `highscore.txt` next to the script.

## Ideas for changes

- Change `COLS`, `ROWS` or `CELL` at the top of `snake.py` to resize the board.
- Tweak `START_DELAY` and `SPEEDUP_PER_FOOD` to make the game easier or harder.
- Swap the colour constants for a different theme.
- Add obstacles or a second kind of food.
