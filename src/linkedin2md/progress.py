"""CLI progress indicators using only the standard library."""

import sys
import threading
from collections.abc import Iterator
from contextlib import contextmanager
from typing import TextIO

_SPINNER_FRAMES = "|/-\\"
_SPINNER_INTERVAL_SECONDS = 0.1


@contextmanager
def show_progress(
    message: str,
    *,
    stream: TextIO | None = None,
) -> Iterator[None]:
    """Show progress while a long-running CLI operation executes.

    Uses an animated spinner on interactive terminals and a single status
    line on non-TTY streams (pipes, CI, captured output).

    Args:
        message: Status text shown to the user. Must not contain user-supplied
            input without ANSI/terminal control sanitization.
    """
    output = stream if stream is not None else sys.stderr

    if not output.isatty():
        output.write(f"{message}\n")
        output.flush()
        yield
        return

    stop_event = threading.Event()

    def animate() -> None:
        frame_index = 0
        while not stop_event.is_set():
            frame = _SPINNER_FRAMES[frame_index % len(_SPINNER_FRAMES)]
            output.write(f"\r{frame} {message}")
            output.flush()
            frame_index += 1
            stop_event.wait(_SPINNER_INTERVAL_SECONDS)

    thread = threading.Thread(target=animate, daemon=True)
    thread.start()
    try:
        yield
    finally:
        stop_event.set()
        thread.join()
        line_width = len(message) + 3
        output.write("\r" + " " * line_width + "\r")
        output.flush()
