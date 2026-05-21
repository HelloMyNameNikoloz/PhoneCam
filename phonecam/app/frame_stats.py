from __future__ import annotations

import mmap
import os
import struct
import time
from collections import deque
from pathlib import Path
from typing import Deque

STATS_MAGIC = 0x50435354
STATS = struct.Struct("<IIQQQQQII")


class FrameStats:
    def __init__(self) -> None:
        self.capture_times: Deque[float] = deque(maxlen=600)
        self.decode_times: Deque[float] = deque(maxlen=600)
        self.width = 0
        self.height = 0
        self.dropped_frames = 0
        self._last_output_count = 0
        self._last_output_time = time.monotonic()
        self._output_fps = 0.0

    def reset(self) -> None:
        self.capture_times.clear()
        self.decode_times.clear()
        self.dropped_frames = 0
        self._last_output_count = 0
        self._last_output_time = time.monotonic()
        self._output_fps = 0.0

    def record_capture_frame(self) -> None:
        self.capture_times.append(time.monotonic())

    def record_decoded_frame(self, width: int, height: int) -> None:
        if self.width and self.height and (self.width != width or self.height != height):
            self.reset()
        self.decode_times.append(time.monotonic())
        self.width = width
        self.height = height

    def record_dropped_frames(self, count: int = 1) -> None:
        self.dropped_frames += count

    def snapshot(self, target_fps: int) -> dict[str, object]:
        now = time.monotonic()
        capture_fps = self._capture_fps(now)
        bridge_fps = self._window_fps(self.decode_times, now)
        native = self._native_stats()
        output_frames = int(native.get("outputFrames", 0))
        elapsed = max(now - self._last_output_time, 0.001)
        if output_frames != self._last_output_count:
            self._output_fps = (output_frames - self._last_output_count) / elapsed
            self._last_output_count = output_frames
            self._last_output_time = now
        actual = min(capture_fps, bridge_fps)
        if output_frames:
            actual = min(actual, self._output_fps)
        dropped = int(native.get("duplicateFrames", 0)) + self._capture_shortfall(now, target_fps)
        return {
            "targetFps": target_fps,
            "captureFps": round(capture_fps, 1),
            "bridgeFps": round(bridge_fps, 1),
            "outputFps": round(self._output_fps, 1),
            "droppedFrames": dropped + self.dropped_frames,
            "latencyMs": int(native.get("latencyMs", 0)),
            "resolution": f"{self.width}x{self.height}" if self.width else None,
            "health": self._health(actual, target_fps),
        }

    def _capture_fps(self, now: float) -> float:
        return self._window_fps(self.capture_times, now)

    @staticmethod
    def _window_fps(times: Deque[float], now: float) -> float:
        while times and now - times[0] > 1.5:
            times.popleft()
        if len(times) < 2:
            return float(len(times))
        span = max(times[-1] - times[0], 0.001)
        return (len(times) - 1) / span

    def _capture_shortfall(self, now: float, target_fps: int) -> int:
        if target_fps <= 0 or len(self.capture_times) < 2:
            return 0
        span = min(now - self.capture_times[0], 1.5)
        expected = int(target_fps * span)
        return max(0, expected - len(self.capture_times))

    @staticmethod
    def _health(actual: float, target: int) -> str:
        if target <= 0 or actual >= target * 0.85:
            return "good"
        if actual >= target * 0.55:
            return "warn"
        return "bad"

    @staticmethod
    def _native_stats() -> dict[str, int]:
        path = Path(os.environ.get("ProgramData", r"C:\ProgramData")) / "PhoneCam" / "native_stats.bin"
        if not path.exists() or path.stat().st_size < STATS.size:
            return {}
        try:
            with path.open("rb") as file:
                with mmap.mmap(file.fileno(), STATS.size, access=mmap.ACCESS_READ) as mm:
                    values = STATS.unpack(mm[: STATS.size])
        except Exception:
            try:
                with path.open("rb") as file:
                    values = STATS.unpack(file.read(STATS.size))
            except Exception:
                return {}
        if values[0] != STATS_MAGIC:
            return {}
        return {
            "outputFrames": values[2],
            "duplicateFrames": values[3],
            "latencyMs": values[6],
            "outputWidth": values[7],
            "outputHeight": values[8],
        }
