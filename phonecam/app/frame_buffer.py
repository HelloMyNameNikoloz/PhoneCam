from __future__ import annotations

import os
import mmap
import struct
import time
from io import BytesIO
from pathlib import Path

from PIL import Image

MAGIC = 0x50434642
VERSION = 1
FORMAT_BGRA = 1
HEADER = struct.Struct("<IIIIIIIIQ")
BUFFER_NAME = "PhoneCamFrameBuffer"
MAX_FRAME_BYTES = 3840 * 2160 * 4
BUFFER_SIZE = HEADER.size + MAX_FRAME_BYTES


class FrameBufferWriter:
    def __init__(self) -> None:
        self.path = Path(os.environ.get("ProgramData", r"C:\ProgramData")) / "PhoneCam" / "framebuffer.bin"
        self._sequence = 0
        self._mapping = mmap.mmap(-1, BUFFER_SIZE, tagname=BUFFER_NAME)
        self._last_debug_write = 0.0

    def write_jpeg(self, jpeg: bytes) -> tuple[int, int]:
        with Image.open(BytesIO(jpeg)) as image:
            if image.mode != "RGB":
                image = image.convert("RGB")
            width, height = image.size
            stride = width * 4
            bgra = image.tobytes("raw", "BGRX")
        if len(bgra) > MAX_FRAME_BYTES:
            raise ValueError("Frame exceeds shared buffer size")
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
            time.time_ns(),
        )
        self._mapping.seek(HEADER.size)
        self._mapping.write(bgra)
        self._mapping.seek(0)
        self._mapping.write(header)
        self._write_debug_file(header, bgra)
        return width, height

    def _write_debug_file(self, header: bytes, sample: bytes) -> None:
        now = time.monotonic()
        if now - self._last_debug_write < 1:
            return
        self._last_debug_write = now
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_bytes(header + sample)
