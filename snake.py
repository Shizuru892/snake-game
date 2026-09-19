"""Snake game built with tkinter (comes with Python, nothing to install).

Run it with:  python snake.py
"""

import random
import tkinter as tk
from pathlib import Path

CELL = 25              # size of one square in pixels
COLS = 20              # grid width in squares
ROWS = 20              # grid height in squares
START_DELAY = 140      # milliseconds between moves at the start
MIN_DELAY = 60         # the game never gets faster than this
SPEEDUP_PER_FOOD = 4   # how many ms faster after each food

BG_COLOR = "#14181f"
GRID_COLOR = "#1b212b"
SNAKE_COLOR = "#4ade80"
HEAD_COLOR = "#22c55e"
FOOD_COLOR = "#f43f5e"
TEXT_COLOR = "#e5e7eb"

HIGHSCORE_FILE = Path(__file__).with_name("highscore.txt")

# Key name -> (dx, dy)
DIRECTIONS = {
    "Up": (0, -1), "w": (0, -1),
    "Down": (0, 1), "s": (0, 1),
    "Left": (-1, 0), "a": (-1, 0),
    "Right": (1, 0), "d": (1, 0),
}


def load_highscore():
    try:
        return int(HIGHSCORE_FILE.read_text().strip())
    except (OSError, ValueError):
        return 0


def save_highscore(value):
    try:
        HIGHSCORE_FILE.write_text(str(value))
    except OSError:
        pass  # not being able to save is fine, the game still works


class SnakeGame:
    def __init__(self, root):
        self.root = root
        root.title("Snake")
        root.resizable(False, False)

        self.score_var = tk.StringVar()
        tk.Label(
            root, textvariable=self.score_var, font=("Consolas", 14),
            bg=BG_COLOR, fg=TEXT_COLOR, pady=6,
        ).pack(fill="x")

        self.canvas = tk.Canvas(
            root, width=COLS * CELL, height=ROWS * CELL,
            bg=BG_COLOR, highlightthickness=0,
        )
        self.canvas.pack()

        root.bind("<Key>", self.on_key)

        self.highscore = load_highscore()
        self.job = None
        self.reset()

    # ---------- game state ----------

    def reset(self):
        if self.job is not None:
            self.root.after_cancel(self.job)

        cx, cy = COLS // 2, ROWS // 2
        self.snake = [(cx, cy), (cx - 1, cy), (cx - 2, cy)]  # head first
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self.score = 0
        self.paused = False
        self.game_over = False
        self.won = False
        self.food = self.random_food()

        self.update_score_label()
        self.draw()
        self.job = self.root.after(START_DELAY, self.tick)

    def random_food(self):
        taken = set(self.snake)
        free = [(x, y) for x in range(COLS) for y in range(ROWS) if (x, y) not in taken]
        return random.choice(free) if free else None

    def update_score_label(self):
        self.score_var.set(f"Score: {self.score}     Best: {self.highscore}")

    # ---------- input ----------

    def on_key(self, event):
        key = event.keysym
        if key.lower() in ("w", "a", "s", "d"):
            key = key.lower()

        if key in DIRECTIONS:
            new = DIRECTIONS[key]
            # Compare with the direction we last moved in, so two quick key
            # presses can't turn the snake back into itself.
            if (new[0] + self.direction[0], new[1] + self.direction[1]) != (0, 0):
                self.next_direction = new
        elif key == "space" and not self.game_over:
            self.paused = not self.paused
            self.draw()
        elif key.lower() == "r":
            self.reset()
        elif key == "Escape":
            self.root.destroy()

    # ---------- game loop ----------

    def tick(self):
        if not self.game_over and not self.paused:
            self.step()
        self.draw()
        delay = max(MIN_DELAY, START_DELAY - SPEEDUP_PER_FOOD * self.score)
        self.job = self.root.after(delay, self.tick)

    def step(self):
        self.direction = self.next_direction
        hx, hy = self.snake[0]
        new_head = (hx + self.direction[0], hy + self.direction[1])

        ate = new_head == self.food

        # The tail moves out of the way this turn unless we just ate,
        # so it is only a collision when we are growing.
        body = self.snake if ate else self.snake[:-1]
        hit_wall = not (0 <= new_head[0] < COLS and 0 <= new_head[1] < ROWS)

        if hit_wall or new_head in body:
            self.end_game()
            return

        self.snake.insert(0, new_head)
        if ate:
            self.score += 1
            self.food = self.random_food()
            if self.food is None:  # board is full
                self.won = True
                self.end_game()
            self.update_score_label()
        else:
            self.snake.pop()

    def end_game(self):
        self.game_over = True
        if self.score > self.highscore:
            self.highscore = self.score
            save_highscore(self.highscore)
        self.update_score_label()

    # ---------- drawing ----------

    def draw_cell(self, x, y, color, inset=1):
        self.canvas.create_rectangle(
            x * CELL + inset, y * CELL + inset,
            (x + 1) * CELL - inset, (y + 1) * CELL - inset,
            fill=color, outline="",
        )

    def draw(self):
        c = self.canvas
        c.delete("all")

        for x in range(1, COLS):
            c.create_line(x * CELL, 0, x * CELL, ROWS * CELL, fill=GRID_COLOR)
        for y in range(1, ROWS):
            c.create_line(0, y * CELL, COLS * CELL, y * CELL, fill=GRID_COLOR)

        if self.food is not None:
            fx, fy = self.food
            c.create_oval(
                fx * CELL + 3, fy * CELL + 3,
                (fx + 1) * CELL - 3, (fy + 1) * CELL - 3,
                fill=FOOD_COLOR, outline="",
            )

        for i, (x, y) in enumerate(self.snake):
            self.draw_cell(x, y, HEAD_COLOR if i == 0 else SNAKE_COLOR)

        if self.game_over:
            title = "You win!" if self.won else "Game over"
            self.overlay(title, "Press R to play again")
        elif self.paused:
            self.overlay("Paused", "Press Space to continue")

    def overlay(self, title, subtitle):
        w, h = COLS * CELL, ROWS * CELL
        self.canvas.create_rectangle(
            w // 2 - 170, h // 2 - 55, w // 2 + 170, h // 2 + 55,
            fill=BG_COLOR, outline=GRID_COLOR, width=2,
        )
        self.canvas.create_text(
            w // 2, h // 2 - 15, text=title,
            fill=TEXT_COLOR, font=("Consolas", 24, "bold"),
        )
        self.canvas.create_text(
            w // 2, h // 2 + 22, text=subtitle,
            fill=TEXT_COLOR, font=("Consolas", 12),
        )


def main():
    root = tk.Tk()
    SnakeGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()
