import queue
import threading
from typing import Any, Callable, Optional


class AsyncWorker:
    """
    Runs a blocking callable on a background thread and delivers progress/result/error
    events through a thread-safe queue that the GUI can poll from its main loop.
    """

    def __init__(self) -> None:
        self._queue: "queue.Queue[tuple]" = queue.Queue()
        self._thread: Optional[threading.Thread] = None

    def run(self, target: Callable[..., Any], *args, **kwargs) -> None:
        """Starts `target(*args, progress_callback=..., **kwargs)` on a background thread."""
        def progress_callback(percent: float, message: str = "") -> None:
            self._queue.put(("progress", percent, message))

        def worker() -> None:
            try:
                result = target(*args, progress_callback=progress_callback, **kwargs)
                self._queue.put(("done", result, None))
            except Exception as exc:
                self._queue.put(("error", None, exc))

        self._thread = threading.Thread(target=worker, daemon=True)
        self._thread.start()

    def poll(self) -> Optional[tuple]:
        """Returns the next queued event as a (kind, payload, error) tuple, or None if empty."""
        try:
            return self._queue.get_nowait()
        except queue.Empty:
            return None

    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()
