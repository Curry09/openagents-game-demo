# Spec-0001/T1
"""Pure, I/O-free Snake game kernel usable without a terminal.

The kernel holds every game rule (movement, turning, reversal blocking,
eating, collision, scoring) so the rules live in exactly one place and can be
covered deterministically by pytest with an injected random seed. It never
touches stdin/stdout or curses.

Example:
    >>> from snake_game import SnakeGame, Direction
    >>> game = SnakeGame(width=20, height=10, seed=42)
    >>> game.step(Direction.RIGHT)
    >>> game.score, game.game_over
    (0, False)

Exports:
    Direction -- Movement direction enum with (dx, dy) vectors and opposite().
    SnakeGame -- Deterministic Snake state machine advanced one frame per step.
"""

from __future__ import annotations

import random
from collections import deque
from enum import Enum


class Direction(Enum):
    """Movement direction carrying its (dx, dy) grid vector.

    Spec-0001/T1.
    """

    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

    @property
    def dx(self) -> int:
        """Return the horizontal component of this direction.

        Spec-0001/T1.
        """
        return self.value[0]

    @property
    def dy(self) -> int:
        """Return the vertical component of this direction.

        Spec-0001/T1.
        """
        return self.value[1]

    def opposite(self) -> "Direction":
        """Return the direction pointing the opposite way.

        Spec-0001/T1.
        """
        return _OPPOSITES[self]


_OPPOSITES = {
    Direction.UP: Direction.DOWN,
    Direction.DOWN: Direction.UP,
    Direction.LEFT: Direction.RIGHT,
    Direction.RIGHT: Direction.LEFT,
}


class SnakeGame:
    """Deterministic Snake state machine advanced one frame per step.

    Spec-0001/T1.
    """

    def __init__(self, width: int = 20, height: int = 10, seed: int | None = None):
        """Build a grid, a centered snake, and the first food.

        Spec-0001/T1.

        Args:
            width: Grid width in cells; must be at least 4.
            height: Grid height in cells; must be at least 1.
            seed: Optional seed for the injected Random, making food placement
                reproducible for tests.

        Raises:
            ValueError: If width or height is too small to host the snake.
        """
        if width < 4 or height < 1:
            raise ValueError("grid must be at least 4 wide and 1 tall")
        self.width = width
        self.height = height
        self._rng = random.Random(seed)
        self.score = 0
        self.game_over = False
        # Start with a 3-cell horizontal snake centered on the grid, head right.
        cy = height // 2
        cx = width // 2
        # Head is the left end of the deque; body trails to the left.
        self.snake: deque[tuple[int, int]] = deque(
            [(cx, cy), (cx - 1, cy), (cx - 2, cy)]
        )
        self.direction = Direction.RIGHT
        self.food: tuple[int, int] | None = None
        self._spawn_food()

    def _spawn_food(self) -> None:
        """Place food on a uniformly random empty cell, or end on a full grid.

        Spec-0001/T1.
        """
        occupied = set(self.snake)
        empty = [
            (x, y)
            for y in range(self.height)
            for x in range(self.width)
            if (x, y) not in occupied
        ]
        if not empty:
            # Grid is full: the board is cleared, so there is nowhere to grow.
            self.food = None
            self.game_over = True
            return
        self.food = self._rng.choice(empty)

    def step(self, direction: Direction | None = None) -> None:
        """Advance the game one frame, applying turn, move, eat, and collisions.

        Spec-0001/T1.

        Args:
            direction: Optional new heading; ignored when it is the direct
                reverse of the current heading (anti-suicide guard) or when the
                game is already over.
        """
        if self.game_over:
            return
        if direction is not None and direction != self.direction.opposite():
            self.direction = direction

        head_x, head_y = self.snake[0]
        new_head = (head_x + self.direction.dx, head_y + self.direction.dy)
        nx, ny = new_head

        # Wall collision: the new head left the grid.
        if not (0 <= nx < self.width and 0 <= ny < self.height):
            self.game_over = True
            return

        # Self collision: the tail cell is vacated this frame unless we eat, so
        # moving onto it is only safe when we are not growing.
        eating = new_head == self.food
        body = set(self.snake)
        if not eating:
            body.discard(self.snake[-1])
        if new_head in body:
            self.game_over = True
            return

        self.snake.appendleft(new_head)
        if eating:
            self.score += 1
            self._spawn_food()
        else:
            self.snake.pop()
