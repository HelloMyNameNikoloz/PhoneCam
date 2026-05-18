from __future__ import annotations

from collections import deque
from datetime import datetime
from threading import Lock
from typing import Deque, Dict, List


class MemoryLogger:
    def __init__(self, max_entries: int = 300) -> None:
        self._entries: Deque[Dict[str, str]] = deque(maxlen=max_entries)
        self._lock = Lock()

    def add(self, level: str, message: str) -> None:
        entry = {
            "time": datetime.now().strftime("%H:%M:%S"),
            "level": level,
            "message": message,
        }
        with self._lock:
            self._entries.append(entry)

    def info(self, message: str) -> None:
        self.add("info", message)

    def warning(self, message: str) -> None:
        self.add("warning", message)

    def error(self, message: str) -> None:
        self.add("error", message)

    def success(self, message: str) -> None:
        self.add("success", message)

    def all(self) -> List[Dict[str, str]]:
        with self._lock:
            return list(self._entries)
