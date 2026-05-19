from __future__ import annotations

import os
import struct
import time
from io import BytesIO
from pathlib import Path

from PIL import Image

MAGIC = 0x50434642
VERSION = 1
FORMAT_BGRA = 1
HEADER = struct.Struct("<IIIIIIIIQ")


class FrameBufferWriter:
    def __init__(self) -> None:
        self.path = Path(os.environ.get("ProgramData", r"C:\ProgramData")) / "PhoneCam" / "framebuffer.bin"
        self._sequence = 0

    def write_jpeg(self, jpeg: bytes) -> tuple[int, int]:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        image = Image.open(BytesIO(jpeg)).convert("RGBA")
        width, height = image.size
        stride = width * 4
        bgra = image.tobytes("raw", "BGRA")
        self._sequence = (self._sequence + 1) & 0xFFFFFFFF
        header = HEADER.pack(
            MAGIC,
            VERSION,
            width,
            height,
            stride,
            FORMAT_BGRA,
            len(bgra),
            self._sequence,
            time.perf_counter_ns(),
        )
        temp = self.path.with_suffix(".tmp")
        temp.write_bytes(header + bgra)
        os.replace(temp, self.path)
        return width, height
