import random
import tkinter as tk
from dataclasses import dataclass


CELL = 24
SNAKE_COLS = 20
SNAKE_ROWS = 20
TETRIS_COLS = 10
TETRIS_ROWS = 20


class GameApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Python 小游戏合集")

        self.game_var = tk.StringVar(value="贪吃蛇")
        self.score_var = tk.StringVar(value="分数: 0")
        self.status_var = tk.StringVar(value="点击“开始/重开”开始游戏")

        toolbar = tk.Frame(root)
        toolbar.pack(fill="x", padx=10, pady=8)

        tk.Label(toolbar, text="选择游戏:").pack(side="left")
        self.menu = tk.OptionMenu(toolbar, self.game_var, "贪吃蛇", "俄罗斯方块")
        self.menu.pack(side="left", padx=8)
        tk.Button(toolbar, text="开始 / 重开", command=self.start_game).pack(side="left")

        info = tk.Frame(root)
        info.pack(fill="x", padx=10)
        tk.Label(info, textvariable=self.score_var).pack(side="left")
        tk.Label(info, textvariable=self.status_var).pack(side="right")

        self.canvas = tk.Canvas(root, width=SNAKE_COLS * CELL, height=SNAKE_ROWS * CELL, bg="#111")
        self.canvas.pack(padx=10, pady=10)

        help_text = (
            "操作说明\n"
            "贪吃蛇: 方向键移动\n"
            "俄罗斯方块: ←/→ 移动, ↓ 加速, ↑ 旋转"
        )
        tk.Label(root, text=help_text, justify="left", anchor="w").pack(fill="x", padx=10, pady=(0, 10))

        self.after_id = None
        self.mode = "snake"

        self.root.bind("<Key>", self.on_key)

        self.snake = SnakeGame(self)
        self.tetris = TetrisGame(self)

        self.start_game()

    def start_game(self) -> None:
        self.cancel_loop()

        game_name = self.game_var.get()
        if game_name == "贪吃蛇":
            self.mode = "snake"
            self.canvas.config(width=SNAKE_COLS * CELL, height=SNAKE_ROWS * CELL)
            self.snake.reset()
            self.loop_snake()
        else:
            self.mode = "tetris"
            self.canvas.config(width=TETRIS_COLS * CELL, height=TETRIS_ROWS * CELL)
            self.tetris.reset()
            self.loop_tetris()

    def cancel_loop(self) -> None:
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None

    def loop_snake(self) -> None:
        alive = self.snake.step()
        self.snake.draw()
        if alive:
            self.after_id = self.root.after(120, self.loop_snake)
        else:
            self.status_var.set("游戏结束（贪吃蛇）: 点击开始/重开")

    def loop_tetris(self) -> None:
        alive = self.tetris.step()
        self.tetris.draw()
        if alive:
            self.after_id = self.root.after(140, self.loop_tetris)
        else:
            self.status_var.set("游戏结束（俄罗斯方块）: 点击开始/重开")

    def on_key(self, event: tk.Event) -> None:
        if self.mode == "snake":
            self.snake.handle_key(event.keysym)
        else:
            self.tetris.handle_key(event.keysym)


@dataclass
class Point:
    x: int
    y: int


class SnakeGame:
    def __init__(self, app: GameApp) -> None:
        self.app = app
        self.body: list[Point] = []
        self.direction = Point(1, 0)
        self.food = Point(0, 0)
        self.score = 0

    def reset(self) -> None:
        self.body = [Point(SNAKE_COLS // 2, SNAKE_ROWS // 2)]
        self.direction = Point(1, 0)
        self.food = self.random_food()
        self.score = 0
        self.app.score_var.set("分数: 0")
        self.app.status_var.set("贪吃蛇进行中")

    def random_food(self) -> Point:
        while True:
            p = Point(random.randrange(SNAKE_COLS), random.randrange(SNAKE_ROWS))
            if all(seg.x != p.x or seg.y != p.y for seg in self.body):
                return p

    def handle_key(self, key: str) -> None:
        mapping = {
            "Up": Point(0, -1),
            "Down": Point(0, 1),
            "Left": Point(-1, 0),
            "Right": Point(1, 0),
        }
        if key not in mapping:
            return

        nxt = mapping[key]
        if self.direction.x + nxt.x == 0 and self.direction.y + nxt.y == 0:
            return
        self.direction = nxt

    def step(self) -> bool:
        head = self.body[0]
        new_head = Point(head.x + self.direction.x, head.y + self.direction.y)

        hit_wall = new_head.x < 0 or new_head.y < 0 or new_head.x >= SNAKE_COLS or new_head.y >= SNAKE_ROWS
        hit_self = any(seg.x == new_head.x and seg.y == new_head.y for seg in self.body)
        if hit_wall or hit_self:
            return False

        self.body.insert(0, new_head)
        if new_head.x == self.food.x and new_head.y == self.food.y:
            self.score += 10
            self.app.score_var.set(f"分数: {self.score}")
            self.food = self.random_food()
        else:
            self.body.pop()

        return True

    def draw(self) -> None:
        c = self.app.canvas
        c.delete("all")

        c.create_rectangle(
            self.food.x * CELL,
            self.food.y * CELL,
            (self.food.x + 1) * CELL,
            (self.food.y + 1) * CELL,
            fill="#ff5252",
            width=0,
        )

        for i, seg in enumerate(self.body):
            color = "#70f8a1" if i else "#30c96d"
            c.create_rectangle(
                seg.x * CELL,
                seg.y * CELL,
                (seg.x + 1) * CELL,
                (seg.y + 1) * CELL,
                fill=color,
                width=1,
                outline="#0f2517",
            )


class TetrisGame:
    SHAPES = [
        [[1, 1, 1, 1]],  # I
        [[1, 1], [1, 1]],  # O
        [[0, 1, 0], [1, 1, 1]],  # T
        [[1, 0], [1, 0], [1, 1]],  # L
        [[0, 1], [0, 1], [1, 1]],  # J
        [[0, 1, 1], [1, 1, 0]],  # S
        [[1, 1, 0], [0, 1, 1]],  # Z
    ]

    def __init__(self, app: GameApp) -> None:
        self.app = app
        self.board: list[list[int]] = []
        self.piece: list[list[int]] = []
        self.px = 0
        self.py = 0
        self.drop_tick = 0
        self.score = 0

    def reset(self) -> None:
        self.board = [[0 for _ in range(TETRIS_COLS)] for _ in range(TETRIS_ROWS)]
        self.drop_tick = 0
        self.score = 0
        self.app.score_var.set("分数: 0")
        self.app.status_var.set("俄罗斯方块进行中")
        self.spawn_piece()

    def spawn_piece(self) -> None:
        self.piece = [row[:] for row in random.choice(self.SHAPES)]
        self.py = 0
        self.px = (TETRIS_COLS - len(self.piece[0])) // 2

    def collide(self, px: int, py: int, shape: list[list[int]]) -> bool:
        for y, row in enumerate(shape):
            for x, val in enumerate(row):
                if not val:
                    continue
                bx, by = px + x, py + y
                if bx < 0 or bx >= TETRIS_COLS or by >= TETRIS_ROWS:
                    return True
                if by >= 0 and self.board[by][bx]:
                    return True
        return False

    def merge(self) -> None:
        for y, row in enumerate(self.piece):
            for x, val in enumerate(row):
                if val:
                    self.board[self.py + y][self.px + x] = 1

    def clear_lines(self) -> None:
        kept = [row for row in self.board if not all(row)]
        removed = TETRIS_ROWS - len(kept)
        for _ in range(removed):
            kept.insert(0, [0] * TETRIS_COLS)
        self.board = kept

        if removed:
            self.score += removed * 100
            self.app.score_var.set(f"分数: {self.score}")

    def rotate(self, shape: list[list[int]]) -> list[list[int]]:
        return [list(col) for col in zip(*shape[::-1])]

    def handle_key(self, key: str) -> None:
        if key == "Left" and not self.collide(self.px - 1, self.py, self.piece):
            self.px -= 1
        elif key == "Right" and not self.collide(self.px + 1, self.py, self.piece):
            self.px += 1
        elif key == "Down" and not self.collide(self.px, self.py + 1, self.piece):
            self.py += 1
        elif key == "Up":
            rotated = self.rotate(self.piece)
            if not self.collide(self.px, self.py, rotated):
                self.piece = rotated

        self.draw()

    def step(self) -> bool:
        self.drop_tick += 1
        if self.drop_tick < 3:
            return True

        self.drop_tick = 0
        if not self.collide(self.px, self.py + 1, self.piece):
            self.py += 1
            return True

        self.merge()
        self.clear_lines()
        self.spawn_piece()

        if self.collide(self.px, self.py, self.piece):
            return False
        return True

    def draw(self) -> None:
        c = self.app.canvas
        c.delete("all")

        for y, row in enumerate(self.board):
            for x, val in enumerate(row):
                if val:
                    c.create_rectangle(
                        x * CELL,
                        y * CELL,
                        (x + 1) * CELL,
                        (y + 1) * CELL,
                        fill="#5fa8ff",
                        outline="#20324d",
                    )

        for y, row in enumerate(self.piece):
            for x, val in enumerate(row):
                if val:
                    c.create_rectangle(
                        (self.px + x) * CELL,
                        (self.py + y) * CELL,
                        (self.px + x + 1) * CELL,
                        (self.py + y + 1) * CELL,
                        fill="#ffd166",
                        outline="#4d3d15",
                    )


def main() -> None:
    root = tk.Tk()
    GameApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
