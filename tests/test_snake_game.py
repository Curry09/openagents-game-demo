# Spec-0001/T1
"""Deterministic unit tests for the pure Snake kernel.

Covers movement, turning, reversal blocking, eating/growth/scoring, wall and
self collisions, and food never spawning on the snake -- all with an injected
seed so results are reproducible without a terminal.

Exports:
    Test functions exercised by pytest; no importable API.
"""

from collections import deque

import pytest

from snake_game import Direction, SnakeGame


def test_import_has_no_terminal_side_effects():
    """Ensure importing and constructing never initializes a terminal.

    Spec-0001/T1.
    """
    import sys

    assert "curses" not in sys.modules
    SnakeGame(width=10, height=6, seed=1)
    assert "curses" not in sys.modules


def test_initial_state_is_centered_and_deterministic():
    """Confirm a fresh game centers the snake with a fixed seeded food.

    Spec-0001/T1.
    """
    game = SnakeGame(width=20, height=10, seed=42)
    assert game.score == 0
    assert game.game_over is False
    assert game.direction is Direction.RIGHT
    assert len(game.snake) == 3
    head = game.snake[0]
    assert head == (10, 5)
    # Food is placed and never lands on the snake body.
    assert game.food is not None
    assert game.food not in set(game.snake)


def test_seed_makes_food_reproducible():
    """Verify the same seed yields the same initial food placement.

    Spec-0001/T1.
    """
    a = SnakeGame(width=20, height=10, seed=7)
    b = SnakeGame(width=20, height=10, seed=7)
    assert a.food == b.food


def test_move_advances_head_by_one_cell():
    """Check a plain step shifts the head one cell along the heading.

    Spec-0001/T1.
    """
    game = SnakeGame(width=20, height=10, seed=42)
    head_before = game.snake[0]
    length_before = len(game.snake)
    game.step()
    assert game.snake[0] == (head_before[0] + 1, head_before[1])
    assert len(game.snake) == length_before


def test_turn_changes_heading():
    """Ensure a perpendicular turn updates the heading and head vector.

    Spec-0001/T1.
    """
    game = SnakeGame(width=20, height=10, seed=42)
    hx, hy = game.snake[0]
    game.step(Direction.UP)
    assert game.direction is Direction.UP
    assert game.snake[0] == (hx, hy - 1)


def test_reverse_direction_is_ignored():
    """Verify pressing the exact reverse keeps the current heading.

    Spec-0001/T1.
    """
    game = SnakeGame(width=20, height=10, seed=42)
    game.step(Direction.LEFT)  # snake is moving RIGHT; LEFT is the reverse
    assert game.direction is Direction.RIGHT
    # Head still advanced rightward rather than reversing into the body.
    assert game.snake[0] == (11, 5)


def test_eating_food_grows_and_scores():
    """Confirm eating grows the snake by one and increments the score.

    Spec-0001/T1.
    """
    game = SnakeGame(width=20, height=10, seed=42)
    hx, hy = game.snake[0]
    # Plant the food directly ahead of the head so the next step eats it.
    game.food = (hx + 1, hy)
    length_before = len(game.snake)
    game.step()
    assert game.score == 1
    assert len(game.snake) == length_before + 1
    assert game.snake[0] == (hx + 1, hy)
    # A fresh food is spawned off the snake.
    assert game.food is not None
    assert game.food not in set(game.snake)


def test_wall_collision_ends_game():
    """Verify running the head off the grid sets game_over.

    Spec-0001/T1.
    """
    game = SnakeGame(width=6, height=5, seed=1)
    game.food = (-99, -99)  # keep food out of the way
    for _ in range(10):
        game.step(Direction.RIGHT)
        if game.game_over:
            break
    assert game.game_over is True
    # Score preserved and readable after the loss.
    assert game.score == 0


def test_self_collision_ends_game():
    """Confirm stepping the head onto an interior body cell ends the game.

    Spec-0001/T1.
    """
    game = SnakeGame(width=20, height=10, seed=42)
    # Hand-place a coiled snake whose head, moving UP, lands on a body cell
    # that is not the vacating tail -- a genuine self collision.
    game.snake = deque([(1, 1), (0, 1), (0, 0), (1, 0), (2, 0), (2, 1), (2, 2)])
    game.direction = Direction.RIGHT
    game.food = (-99, -99)
    game.step(Direction.UP)  # head (1,1) -> (1,0), an interior body cell
    assert game.game_over is True


def test_tail_cell_is_enterable_when_not_growing():
    """Ensure moving into the vacating tail cell is not a self collision.

    Spec-0001/T1.
    """
    game = SnakeGame(width=20, height=10, seed=42)
    game.food = (-99, -99)  # never eat during this maneuver
    # A 3-cell snake doing a full square returns onto the old tail cell, which
    # has moved on by then, so it must survive.
    game.step(Direction.UP)
    game.step(Direction.LEFT)
    game.step(Direction.DOWN)
    assert game.game_over is False


def test_food_only_spawns_on_empty_cells():
    """Verify repeated eating never places food onto the snake body.

    Spec-0001/T1.
    """
    game = SnakeGame(width=8, height=6, seed=3)
    for _ in range(50):
        # Always feed the snake the cell ahead when reachable, else just move.
        hx, hy = game.snake[0]
        ahead = (hx + game.direction.dx, hy + game.direction.dy)
        if 0 <= ahead[0] < game.width and 0 <= ahead[1] < game.height:
            game.food = ahead
        game.step()
        if game.game_over:
            break
        assert game.food is None or game.food not in set(game.snake)


def test_small_grid_rejected():
    """Confirm an undersized grid raises ValueError.

    Spec-0001/T1.
    """
    with pytest.raises(ValueError):
        SnakeGame(width=3, height=5)


def test_step_after_game_over_is_noop():
    """Ensure stepping a finished game changes nothing.

    Spec-0001/T1.
    """
    game = SnakeGame(width=6, height=5, seed=1)
    game.game_over = True
    snapshot = deque(game.snake)
    game.step(Direction.UP)
    assert game.snake == snapshot
