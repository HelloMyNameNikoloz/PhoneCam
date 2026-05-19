from __future__ import annotations

import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Callable

from app.frame_buffer import FrameBufferWriter
from app.frame_stats import FrameStats
from app.frame_stream_server import FrameStreamServer


class ReusableHttpServer(ThreadingHTTPServer):
    allow_reuse_address = True


class FrameReceiver:
    def __init__(self, on_log: Callable[[str, str], None], port: int = 4767) -> None:
        self.port = port
        self.writer = FrameBufferWriter()
        self.stats = FrameStats()
        self.on_log = on_log
        self.frames_received = 0
        self.last_size: str | None = None
        self._condition = threading.Condition()
        self._latest_jpeg: bytes | None = None
        self._server: ThreadingHTTPServer | None = None
        self._thread: threading.Thread | None = None
        self._stream_server = FrameStreamServer(port + 1, self._accept_frame, on_log)

    def start(self) -> None:
        if self._server:
            return
        self._server = ReusableHttpServer(("127.0.0.1", self.port), self._handler())
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()
        self._stream_server.start()
        self.on_log("info", f"Frame receiver listening on USB reverse port {self.port}")

    def stop(self) -> None:
        if not self._server:
            return
        self._server.shutdown()
        self._server.server_close()
        self._server = None
        self._thread = None
        self._stream_server.stop()

    def status(self) -> dict[str, object]:
        return {
            "listening": self._server is not None,
            "framesReceived": self.frames_received,
            "lastSize": self.last_size,
            "postUrl": f"http://127.0.0.1:{self.port}/frame",
            "streamUrl": f"http://127.0.0.1:{self.port}/stream.mjpg",
            "framePort": self.port + 1,
            "frameStreamListening": self._stream_server.listening(),
        }

    def performance(self, target_fps: int) -> dict[str, object]:
        return self.stats.snapshot(target_fps)

    def reset_performance(self) -> None:
        self.stats.reset()

    def _accept_frame(self, jpeg: bytes) -> None:
        try:
            width, height = self.writer.write_jpeg(jpeg)
            self.stats.record_capture_frame(width, height)
            self.frames_received += 1
            self.last_size = f"{width}x{height}"
            with self._condition:
                self._latest_jpeg = jpeg
                self._condition.notify_all()
        except Exception as exc:
            self.on_log("error", f"Frame decode failed: {exc}")

    def _handler(self) -> type[BaseHTTPRequestHandler]:
        receiver = self

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self) -> None:
                if self.path.startswith("/health"):
                    self._send(200, b"ok")
                elif self.path.startswith("/stream.mjpg"):
                    self._stream()
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
                    receiver._accept_frame(self.rfile.read(length))
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

            def _stream(self) -> None:
                self.send_response(200)
                self.send_header("Content-Type", "multipart/x-mixed-replace; boundary=frame")
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                seen = 0
                while True:
                    with receiver._condition:
                        receiver._condition.wait_for(lambda: receiver.frames_received != seen, timeout=5)
                        frame = receiver._latest_jpeg
                        seen = receiver.frames_received
                    if not frame:
                        continue
                    try:
                        self.wfile.write(b"--frame\r\nContent-Type: image/jpeg\r\n")
                        self.wfile.write(f"Content-Length: {len(frame)}\r\n\r\n".encode())
                        self.wfile.write(frame + b"\r\n")
                    except OSError:
                        break

        return Handler
