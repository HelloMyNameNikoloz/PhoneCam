from __future__ import annotations

import mmap
import struct
import time
from collections import deque
from typing import Deque

STATS_NAME = "PhoneCamStats"
STATS_MAGIC = 0x50435354
STATS = struct.Struct("<IIQQQQQII")


class FrameStats:
    def __init__(self) -> None:
        self.capture_times: Deque[float] = deque(maxlen=600)
        self.width = 0
        self.height = 0
        self._last_output_count = 0
        self._last_output_time = time.monotonic()
        self._output_fps = 0.0

    def reset(self) -> None:
        self.capture_times.clear()
        self._last_output_count = 0
        self._last_output_time = time.monotonic()
        self._output_fps = 0.0

    def record_capture_frame(self, width: int, height: int) -> None:
        if self.width and self.height and (self.width != width or self.height != height):
            self.reset()
        self.capture_times.append(time.monotonic())
        self.width = width
        self.height = height

    def snapshot(self, target_fps: int) -> dict[str, object]:
        now = time.monotonic()
        capture_fps = self._capture_fps(now)
        native = self._native_stats()
        output_frames = int(native.get("outputFrames", 0))
        elapsed = max(now - self._last_output_time, 0.001)
        if output_frames != self._last_output_count:
            self._output_fps = (output_frames - self._last_output_count) / elapsed
            self._last_output_count = output_frames
            self._last_output_time = now
        actual = min(capture_fps, self._output_fps) if output_frames else capture_fps
        dropped = int(native.get("duplicateFrames", 0)) + self._capture_shortfall(now, target_fps)
        return {
            "targetFps": target_fps,
            "captureFps": round(capture_fps, 1),
            "outputFps": round(self._output_fps, 1),
            "droppedFrames": dropped,
            "latencyMs": int(native.get("latencyMs", 0)),
            "resolution": f"{self.width}x{self.height}" if self.width else None,
            "health": self._health(actual, target_fps),
        }

    def _capture_fps(self, now: float) -> float:
        while self.capture_times and now - self.capture_times[0] > 1.5:
            self.capture_times.popleft()
        if len(self.capture_times) < 2:
            return float(len(self.capture_times))
        span = max(self.capture_times[-1] - self.capture_times[0], 0.001)
        return (len(self.capture_times) - 1) / span

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
        try:
            with mmap.mmap(-1, STATS.size, tagname=STATS_NAME, access=mmap.ACCESS_READ) as mm:
                values = STATS.unpack(mm[: STATS.size])
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
