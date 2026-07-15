# Spec-0001/T1
"""Pytest bootstrap that puts the repo root on sys.path.

Its mere presence at the project root makes pytest insert this directory onto
sys.path, so `pytest tests/test_snake_game.py` imports the top-level
`snake_game` module the same way `python -m pytest` does. No fixtures needed.

Exports:
    Nothing importable; this file exists only for its collection side effect.
"""
