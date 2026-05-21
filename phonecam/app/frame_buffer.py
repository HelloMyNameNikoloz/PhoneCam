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
MAX_FRAME_BYTES = 3840 * 2160 * 4
BUFFER_SIZE = HEADER.size + MAX_FRAME_BYTES


class FrameBufferWriter:
    def __init__(self) -> None:
        self.path = Path(os.environ.get("ProgramData", r"C:\ProgramData")) / "PhoneCam" / "framebuffer.bin"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._file = self.path.open("a+b")
        self._file.truncate(BUFFER_SIZE)
        self._file.seek(0)
        self._sequence = 0
        self._mapping = mmap.mmap(self._file.fileno(), BUFFER_SIZE)

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
        return width, height

    def close(self) -> None:
        self._mapping.close()
        self._file.close()

    def __del__(self) -> None:
        try:
            self.close()
        except Exception:
            pass
