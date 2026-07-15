# Spec-0001/T2
"""Play Snake in the terminal with a thin curses front end.

Run `python snake.py` to play: arrow keys or WASD steer, `q` quits, eating food
grows the snake and scores, and hitting a wall or yourself ends the game with
your final score. Every rule is delegated to snake_game.SnakeGame; this module
only reads keys, ticks the kernel, and draws the state.

Exports:
    main -- Run the curses game loop against a provided stdscr window.
"""

from __future__ import annotations

import curses
import time

from snake_game import Direction, SnakeGame

# Arrow keys and WASD (either case) both map onto the same four directions.
_KEY_TO_DIRECTION = {
    curses.KEY_UP: Direction.UP,
    curses.KEY_DOWN: Direction.DOWN,
    curses.KEY_LEFT: Direction.LEFT,
    curses.KEY_RIGHT: Direction.RIGHT,
    ord("w"): Direction.UP,
    ord("W"): Direction.UP,
    ord("s"): Direction.DOWN,
    ord("S"): Direction.DOWN,
    ord("a"): Direction.LEFT,
    ord("A"): Direction.LEFT,
    ord("d"): Direction.RIGHT,
    ord("D"): Direction.RIGHT,
}

_QUIT_KEYS = frozenset({ord("q"), ord("Q")})

_GRID_WIDTH = 24
_GRID_HEIGHT = 14
_TICK_SECONDS = 0.12


def _read_direction(stdscr) -> Direction | None:
    """Drain pending keys and return the latest steering direction, if any.

    Spec-0001/T2.

    Args:
        stdscr: The curses window, expected in non-blocking (nodelay) mode.

    Returns:
        The most recent Direction pressed this tick, or None if none was.

    Raises:
        _QuitGame: If a quit key was pressed.
    """
    direction: Direction | None = None
    while True:
        key = stdscr.getch()
        if key == -1:
            break
        if key in _QUIT_KEYS:
            raise _QuitGame
        mapped = _KEY_TO_DIRECTION.get(key)
        if mapped is not None:
            direction = mapped
    return direction


class _QuitGame(Exception):
    """Signal that the player asked to quit.

    Spec-0001/T2.
    """


def _render(stdscr, game: SnakeGame) -> None:
    """Draw the border, snake, food, and score for the current frame.

    Spec-0001/T2.

    Args:
        stdscr: The curses window to draw into.
        game: The kernel whose state is rendered.
    """
    stdscr.erase()
    # Border: a box one cell larger than the grid on every side.
    for x in range(game.width + 2):
        stdscr.addch(0, x, ord("#"))
        stdscr.addch(game.height + 1, x, ord("#"))
    for y in range(game.height + 2):
        stdscr.addch(y, 0, ord("#"))
        stdscr.addch(y, game.width + 1, ord("#"))
    if game.food is not None:
        fx, fy = game.food
        stdscr.addch(fy + 1, fx + 1, ord("*"))
    for i, (sx, sy) in enumerate(game.snake):
        stdscr.addch(sy + 1, sx + 1, ord("O") if i == 0 else ord("o"))
    stdscr.addstr(game.height + 2, 0, f"Score: {game.score}   (arrows/WASD, q quits)")
    stdscr.noutrefresh()
    curses.doupdate()


def _render_game_over(stdscr, game: SnakeGame) -> None:
    """Clear the screen and show Game Over with the final score.

    Spec-0001/T2.

    Args:
        stdscr: The curses window to draw into.
        game: The finished kernel whose score is shown.
    """
    stdscr.nodelay(False)
    stdscr.erase()
    stdscr.addstr(1, 2, "Game Over")
    stdscr.addstr(3, 2, f"Final score: {game.score}")
    stdscr.addstr(5, 2, "Press any key to exit.")
    stdscr.noutrefresh()
    curses.doupdate()
    stdscr.getch()


def main(stdscr) -> None:
    """Run the curses game loop against a provided stdscr window.

    Spec-0001/T2.

    Args:
        stdscr: The curses standard window supplied by curses.wrapper.
    """
    curses.curs_set(0)
    stdscr.nodelay(True)  # getch returns -1 immediately when no key is waiting
    stdscr.keypad(True)  # decode arrow keys into curses.KEY_* constants

    game = SnakeGame(width=_GRID_WIDTH, height=_GRID_HEIGHT)
    _render(stdscr, game)
    pending: Direction | None = None
    last_tick = time.monotonic()
    try:
        while not game.game_over:
            steered = _read_direction(stdscr)
            if steered is not None:
                pending = steered
            now = time.monotonic()
            if now - last_tick >= _TICK_SECONDS:
                game.step(pending)
                pending = None
                last_tick = now
                _render(stdscr, game)
            else:
                time.sleep(0.005)  # yield instead of busy-spinning between ticks
    except _QuitGame:
        return
    _render_game_over(stdscr, game)


if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except curses.error as exc:  # e.g. no real tty available
        raise SystemExit(
            f"snake.py needs an interactive terminal to run: {exc}"
        ) from exc
