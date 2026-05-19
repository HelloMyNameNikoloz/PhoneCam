from __future__ import annotations

import socketserver
import struct
import threading
from typing import Callable


MAX_JPEG_BYTES = 8 * 1024 * 1024


class ReusableTcpServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


class FrameStreamServer:
    def __init__(
        self,
        port: int,
        on_frame: Callable[[bytes], None],
        on_log: Callable[[str, str], None],
    ) -> None:
        self.port = port
        self.on_frame = on_frame
        self.on_log = on_log
        self._server: ReusableTcpServer | None = None
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        if self._server:
            return
        self._server = ReusableTcpServer(("127.0.0.1", self.port), self._handler())
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()
        self.on_log("info", f"High-rate frame stream listening on USB reverse port {self.port}")

    def stop(self) -> None:
        if not self._server:
            return
        self._server.shutdown()
        self._server.server_close()
        self._server = None
        self._thread = None

    def listening(self) -> bool:
        return self._server is not None

    def _handler(self) -> type[socketserver.StreamRequestHandler]:
        owner = self

        class Handler(socketserver.StreamRequestHandler):
            def handle(self) -> None:
                while True:
                    header = self._read_exact(4)
                    if not header:
                        break
                    length = struct.unpack(">I", header)[0]
                    if length <= 0 or length > MAX_JPEG_BYTES:
                        owner.on_log("warning", "Android sent an invalid frame size")
                        break
                    jpeg = self._read_exact(length)
                    if not jpeg:
                        break
                    owner.on_frame(jpeg)

            def _read_exact(self, size: int) -> bytes | None:
                chunks = bytearray()
                while len(chunks) < size:
                    chunk = self.rfile.read(size - len(chunks))
                    if not chunk:
                        return None
                    chunks.extend(chunk)
                return bytes(chunks)

        return Handler
