const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");
const gameSelect = document.getElementById("gameSelect");
const startBtn = document.getElementById("startBtn");
const scoreEl = document.getElementById("score");
const statusEl = document.getElementById("status");

let loopId = null;
let mode = "snake";

const snake = {
  grid: 20,
  board: 15,
  direction: { x: 1, y: 0 },
  body: [{ x: 7, y: 7 }],
  food: { x: 10, y: 10 },
  score: 0,
};

const tetris = {
  cols: 10,
  rows: 20,
  block: 25,
  board: [],
  piece: null,
  dropCounter: 0,
  dropInterval: 450,
  lastTime: 0,
  score: 0,
};

const tetrisShapes = {
  I: [[1, 1, 1, 1]],
  O: [
    [1, 1],
    [1, 1],
  ],
  T: [
    [0, 1, 0],
    [1, 1, 1],
  ],
  L: [
    [1, 0],
    [1, 0],
    [1, 1],
  ],
  J: [
    [0, 1],
    [0, 1],
    [1, 1],
  ],
  S: [
    [0, 1, 1],
    [1, 1, 0],
  ],
  Z: [
    [1, 1, 0],
    [0, 1, 1],
  ],
};

function clearLoop() {
  if (loopId) {
    cancelAnimationFrame(loopId);
    loopId = null;
  }
}

function resetSnake() {
  snake.direction = { x: 1, y: 0 };
  snake.body = [{ x: 7, y: 7 }];
  snake.food = randomFood();
  snake.score = 0;
  scoreEl.textContent = "0";
  statusEl.textContent = "贪吃蛇进行中";
}

function randomFood() {
  return {
    x: Math.floor(Math.random() * snake.board),
    y: Math.floor(Math.random() * snake.board),
  };
}

function stepSnake() {
  const head = {
    x: snake.body[0].x + snake.direction.x,
    y: snake.body[0].y + snake.direction.y,
  };

  if (
    head.x < 0 ||
    head.y < 0 ||
    head.x >= snake.board ||
    head.y >= snake.board ||
    snake.body.some((p) => p.x === head.x && p.y === head.y)
  ) {
    statusEl.textContent = "游戏结束：撞到了，点击重新开始";
    clearInterval(snake.timer);
    return;
  }

  snake.body.unshift(head);

  if (head.x === snake.food.x && head.y === snake.food.y) {
    snake.score += 10;
    scoreEl.textContent = String(snake.score);
    snake.food = randomFood();
  } else {
    snake.body.pop();
  }

  drawSnake();
}

function drawSnake() {
  canvas.width = snake.board * snake.grid;
  canvas.height = snake.board * snake.grid;

  ctx.fillStyle = "#0b0f1e";
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  ctx.fillStyle = "#fa5252";
  ctx.fillRect(
    snake.food.x * snake.grid,
    snake.food.y * snake.grid,
    snake.grid - 1,
    snake.grid - 1,
  );

  ctx.fillStyle = "#74f0a7";
  for (const cell of snake.body) {
    ctx.fillRect(
      cell.x * snake.grid,
      cell.y * snake.grid,
      snake.grid - 1,
      snake.grid - 1,
    );
  }
}

function resetTetris() {
  tetris.board = Array.from({ length: tetris.rows }, () =>
    Array(tetris.cols).fill(0),
  );
  tetris.score = 0;
  scoreEl.textContent = "0";
  statusEl.textContent = "俄罗斯方块进行中";
  tetris.lastTime = 0;
  tetris.dropCounter = 0;
  tetris.piece = createPiece();
}

function createPiece() {
  const types = Object.keys(tetrisShapes);
  const type = types[Math.floor(Math.random() * types.length)];
  const shape = tetrisShapes[type].map((row) => [...row]);
  return {
    shape,
    x: Math.floor((tetris.cols - shape[0].length) / 2),
    y: 0,
  };
}

function collide(board, piece) {
  return piece.shape.some((row, y) =>
    row.some((value, x) => {
      if (!value) return false;
      const px = piece.x + x;
      const py = piece.y + y;
      return (
        px < 0 ||
        px >= tetris.cols ||
        py >= tetris.rows ||
        (py >= 0 && board[py][px] !== 0)
      );
    }),
  );
}

function merge(board, piece) {
  piece.shape.forEach((row, y) => {
    row.forEach((value, x) => {
      if (value) board[piece.y + y][piece.x + x] = value;
    });
  });
}

function clearLines() {
  let lines = 0;
  for (let y = tetris.rows - 1; y >= 0; y--) {
    if (tetris.board[y].every((cell) => cell !== 0)) {
      tetris.board.splice(y, 1);
      tetris.board.unshift(Array(tetris.cols).fill(0));
      lines += 1;
      y++;
    }
  }
  if (lines > 0) {
    tetris.score += lines * 100;
    scoreEl.textContent = String(tetris.score);
  }
}

function rotate(shape) {
  return shape[0].map((_, i) => shape.map((row) => row[i]).reverse());
}

function drawTetris() {
  canvas.width = tetris.cols * tetris.block;
  canvas.height = tetris.rows * tetris.block;

  ctx.fillStyle = "#0b0f1e";
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  ctx.fillStyle = "#6ea8ff";
  tetris.board.forEach((row, y) => {
    row.forEach((value, x) => {
      if (value) {
        ctx.fillRect(
          x * tetris.block,
          y * tetris.block,
          tetris.block - 1,
          tetris.block - 1,
        );
      }
    });
  });

  ctx.fillStyle = "#ffd56b";
  tetris.piece.shape.forEach((row, y) => {
    row.forEach((value, x) => {
      if (value) {
        ctx.fillRect(
          (tetris.piece.x + x) * tetris.block,
          (tetris.piece.y + y) * tetris.block,
          tetris.block - 1,
          tetris.block - 1,
        );
      }
    });
  });
}

function updateTetris(time = 0) {
  const delta = time - tetris.lastTime;
  tetris.lastTime = time;
  tetris.dropCounter += delta;

  if (tetris.dropCounter > tetris.dropInterval) {
    tetris.piece.y += 1;
    if (collide(tetris.board, tetris.piece)) {
      tetris.piece.y -= 1;
      merge(tetris.board, tetris.piece);
      clearLines();
      tetris.piece = createPiece();
      if (collide(tetris.board, tetris.piece)) {
        statusEl.textContent = "游戏结束：堆满了，点击重新开始";
        return;
      }
    }
    tetris.dropCounter = 0;
  }

  drawTetris();
  loopId = requestAnimationFrame(updateTetris);
}

function startGame() {
  clearLoop();
  clearInterval(snake.timer);

  mode = gameSelect.value;
  if (mode === "snake") {
    resetSnake();
    drawSnake();
    snake.timer = setInterval(stepSnake, 120);
  } else {
    resetTetris();
    drawTetris();
    loopId = requestAnimationFrame(updateTetris);
  }
}

document.addEventListener("keydown", (e) => {
  if (mode === "snake") {
    const map = {
      ArrowUp: { x: 0, y: -1 },
      ArrowDown: { x: 0, y: 1 },
      ArrowLeft: { x: -1, y: 0 },
      ArrowRight: { x: 1, y: 0 },
    };
    const next = map[e.key];
    if (!next) return;

    if (
      snake.direction.x + next.x === 0 &&
      snake.direction.y + next.y === 0
    ) {
      return;
    }
    snake.direction = next;
  } else if (mode === "tetris") {
    if (!tetris.piece) return;

    if (e.key === "ArrowLeft") {
      tetris.piece.x -= 1;
      if (collide(tetris.board, tetris.piece)) tetris.piece.x += 1;
    }
    if (e.key === "ArrowRight") {
      tetris.piece.x += 1;
      if (collide(tetris.board, tetris.piece)) tetris.piece.x -= 1;
    }
    if (e.key === "ArrowDown") {
      tetris.piece.y += 1;
      if (collide(tetris.board, tetris.piece)) tetris.piece.y -= 1;
    }
    if (e.key === "ArrowUp") {
      const rotated = rotate(tetris.piece.shape);
      const backup = tetris.piece.shape;
      tetris.piece.shape = rotated;
      if (collide(tetris.board, tetris.piece)) {
        tetris.piece.shape = backup;
      }
    }
    drawTetris();
  }
});

startBtn.addEventListener("click", startGame);

startGame();
