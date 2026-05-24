"""Tests for CLI progress indicators."""

import io
import threading
from unittest.mock import patch

import pytest

from linkedin2md.progress import show_progress


class TestShowProgress:
    """Tests for show_progress context manager."""

    def test_non_tty_writes_status_line(self):
        """Non-interactive streams get a single progress message."""
        stream = io.StringIO()

        with patch.object(stream, "isatty", return_value=False):
            with show_progress("Working...", stream=stream):
                pass

        assert stream.getvalue() == "Working...\n"

    def test_tty_shows_spinner_and_clears_line(self):
        """Interactive terminals show a spinner that is cleared on exit."""
        stream = io.StringIO()
        captured: list[str] = []
        spinner_seen = threading.Event()

        original_write = stream.write

        def capture_write(text: str) -> int:
            captured.append(text)
            if text.startswith("\r") and "Processing..." in text:
                spinner_seen.set()
            return original_write(text)

        with patch.object(stream, "isatty", return_value=True):
            with patch.object(stream, "write", side_effect=capture_write):
                with patch("linkedin2md.progress._SPINNER_INTERVAL_SECONDS", 0.01):
                    with show_progress("Processing...", stream=stream):
                        assert spinner_seen.wait(timeout=2.0)

        combined = "".join(captured)
        assert any(frame in combined for frame in "|/-\\")
        assert "Processing..." in combined
        assert combined.endswith("\r" + " " * (len("Processing...") + 3) + "\r")

    def test_tty_thread_joined_after_exit(self):
        """Spinner thread is joined when the context exits."""
        stream = io.StringIO()
        join_called = threading.Event()
        real_thread = threading.Thread

        def thread_factory(*args, **kwargs):
            thread = real_thread(*args, **kwargs)
            real_join = thread.join

            def join(*join_args, **join_kwargs):
                join_called.set()
                return real_join(*join_args, **join_kwargs)

            thread.join = join  # type: ignore[method-assign]
            return thread

        with patch.object(stream, "isatty", return_value=True):
            with patch(
                "linkedin2md.progress.threading.Thread", side_effect=thread_factory
            ):
                with show_progress("Working...", stream=stream):
                    pass

        assert join_called.is_set()

    def test_tty_exception_propagates(self):
        """Exceptions in the wrapped block propagate after cleanup."""
        stream = io.StringIO()

        with patch.object(stream, "isatty", return_value=True):
            with pytest.raises(RuntimeError, match="test error"):
                with show_progress("Working...", stream=stream):
                    raise RuntimeError("test error")
