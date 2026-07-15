#!/usr/bin/env bash
# Spec-0001/T3
# Offline end-to-end check for the Snake CLI game: lint + kernel tests + entry
# grep anchors. Exit 0 means the headless segment passed; the curses TUI itself
# needs a real tty and is covered by the manual checklist in README.md.
set -euo pipefail

cd "$(dirname "$0")/.."

echo "== ruff check =="
ruff check .

echo "== pytest (pure kernel) =="
pytest -q tests/test_snake_game.py

echo "== snake.py entry anchors =="
grep -q "curses.wrapper" snake.py
grep -q "curses.KEY_UP" snake.py
grep -q "curses.KEY_DOWN" snake.py
grep -q "curses.KEY_LEFT" snake.py
grep -q "curses.KEY_RIGHT" snake.py
grep -Eq 'ord\("w"\)' snake.py
grep -Eq 'ord\("a"\)' snake.py
grep -Eq 'ord\("s"\)' snake.py
grep -Eq 'ord\("d"\)' snake.py
grep -q '__main__' snake.py
# The entry must delegate rules to the kernel, not reimplement them.
grep -q "from snake_game import" snake.py

echo "OK: spec-0001 offline e2e passed"
