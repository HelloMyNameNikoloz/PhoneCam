from __future__ import annotations

import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Callable

from app.frame_buffer import FrameBufferWriter


class ReusableHttpServer(ThreadingHTTPServer):
    allow_reuse_address = True


class FrameReceiver:
    def __init__(self, on_log: Callable[[str, str], None], port: int = 4767) -> None:
        self.port = port
        self.writer = FrameBufferWriter()
        self.on_log = on_log
        self.frames_received = 0
        self.last_size: str | None = None
        self._server: ThreadingHTTPServer | None = None
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        if self._server:
            return
        self._server = ReusableHttpServer(("127.0.0.1", self.port), self._handler())
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()
        self.on_log("info", f"Frame receiver listening on USB reverse port {self.port}")

    def stop(self) -> None:
        if not self._server:
            return
        self._server.shutdown()
        self._server.server_close()
        self._server = None
        self._thread = None

    def status(self) -> dict[str, object]:
        return {
            "listening": self._server is not None,
            "framesReceived": self.frames_received,
            "lastSize": self.last_size,
            "postUrl": f"http://127.0.0.1:{self.port}/frame",
        }

    def _handler(self) -> type[BaseHTTPRequestHandler]:
        receiver = self

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self) -> None:
                if self.path.startswith("/health"):
                    self._send(200, b"ok")
                else:
                    self._send(404, b"not found")

            def do_POST(self) -> None:
                if not self.path.startswith("/frame"):
                    self._send(404, b"not found")
                    return
                length = int(self.headers.get("Content-Length", "0"))
                if length <= 0 or length > 8 * 1024 * 1024:
                    self._send(400, b"invalid frame")
                    return
                try:
                    width, height = receiver.writer.write_jpeg(self.rfile.read(length))
                    receiver.frames_received += 1
                    receiver.last_size = f"{width}x{height}"
                    self._send(200, b"ok")
                except Exception as exc:
                    receiver.on_log("error", f"Frame decode failed: {exc}")
                    self._send(500, b"decode failed")

            def log_message(self, *_args: object) -> None:
                return

            def _send(self, code: int, data: bytes) -> None:
                self.send_response(code)
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

        return Handler
