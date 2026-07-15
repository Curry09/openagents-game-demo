# Spec-0001/T2
"""Drive snake.py inside a pseudo-terminal and capture the rendered screen.

Run `python docs/evidence/spec-0001/drive_pty.py` from the repo root. It forks a
pty, execs `python snake.py`, injects arrow-key and WASD keystrokes to steer the
snake into a wall, and prints the captured (escape-stripped) terminal frames plus
a marker checklist. This provides real-app evidence for the curses entry, which
needs a tty and so cannot run under headless pytest.

Exports:
    strip -- Remove ANSI/terminal escape sequences from captured bytes.
    drive -- Fork a pty, run snake.py, inject timed keystrokes, return raw bytes.
"""

import os
import pty
import re
import select
import sys
import time


def strip(data: bytes) -> str:
    """Remove ANSI and terminal escape sequences from captured bytes.

    Spec-0001/T2.

    Args:
        data: Raw bytes read from the pty master.

    Returns:
        The decoded text with cursor/color/charset escapes stripped.
    """
    cleaned = re.sub(rb"\x1b\[[0-9;?]*[A-Za-z]|\x1b[()][AB0]|\x1b[=>]|\r", b"", data)
    return cleaned.decode("utf-8", "replace")


def drive(keys_over_time: list[tuple[float, bytes]]) -> bytes:
    """Fork a pty, run snake.py, inject timed keystrokes, return raw output.

    Spec-0001/T2.

    Args:
        keys_over_time: (seconds_after_launch, key_bytes) pairs to inject.

    Returns:
        All bytes emitted by snake.py during the run.
    """
    pid, fd = pty.fork()
    if pid == 0:
        os.environ["TERM"] = "xterm"
        os.execvp(sys.executable, [sys.executable, "snake.py"])
    frames: list[bytes] = []
    start = time.monotonic()
    sent = 0
    while True:
        ready, _, _ = select.select([fd], [], [], 0.05)
        if ready:
            try:
                chunk = os.read(fd, 65536)
            except OSError:
                break
            if not chunk:
                break
            frames.append(chunk)
        elapsed = time.monotonic() - start
        if sent < len(keys_over_time) and elapsed >= keys_over_time[sent][0]:
            try:
                os.write(fd, keys_over_time[sent][1])
            except OSError:
                pass
            sent += 1
        if elapsed > 4.0:
            break
    try:
        os.write(fd, b"q")
        os.close(fd)
    except OSError:
        pass
    return b"".join(frames)


def main() -> None:
    """Run the scripted drive and print the capture plus a marker checklist.

    Spec-0001/T2.
    """
    sequence = [
        (0.3, b"\x1b[A"),  # arrow Up
        (0.5, b"w"),  # WASD up
        (0.8, b"\x1b[C"),  # arrow Right
        (1.1, b"d"),  # WASD right
        *[(1.4 + 0.2 * i, b"\x1b[A") for i in range(6)],  # into the top wall
    ]
    text = strip(drive(sequence))
    print("=== captured (stripped, tail) ===")
    print(text[-1200:])
    print("=== markers ===")
    for marker in ("Score:", "Game Over", "Final score", "O", "*", "#"):
        print(f"{marker!r}: {'FOUND' if marker in text else 'absent'}")


if __name__ == "__main__":
    main()
