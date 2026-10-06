"""
Thread-safe memory buffer log handler for live UI viewing.
"""

from __future__ import annotations
import logging
import threading
from collections import deque
from typing import List, Callable, Optional


class BufferLogHandler(logging.Handler):
    """Stores recent log records in memory for UI display and notifies listeners."""

    def __init__(self, capacity: int = 2000):
        super().__init__()
        self.capacity = capacity
        self.buffer: deque = deque(maxlen=capacity)
        self._buf_lock = threading.RLock()
        self.listeners: List[Callable[[logging.LogRecord], None]] = []

    def emit(self, record: logging.LogRecord) -> None:
        try:
            with self._buf_lock:
                self.buffer.append(record)
                listeners = list(self.listeners)

            for listener in listeners:
                try:
                    listener(record)
                except Exception:
                    pass
        except Exception:
            self.handleError(record)

    def add_listener(self, callback: Callable[[logging.LogRecord], None]) -> None:
        with self._buf_lock:
            if callback not in self.listeners:
                self.listeners.append(callback)

    def remove_listener(self, callback: Callable[[logging.LogRecord], None]) -> None:
        with self._buf_lock:
            if callback in self.listeners:
                self.listeners.remove(callback)

    def get_records(self) -> List[logging.LogRecord]:
        with self._buf_lock:
            return list(self.buffer)

    def clear(self) -> None:
        with self._buf_lock:
            self.buffer.clear()
