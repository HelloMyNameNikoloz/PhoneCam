from __future__ import annotations

import threading
import time
import socket
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any


class FrameStore:
    def __init__(self) -> None:
        self._condition = threading.Condition()
        self._frame: bytes | None = None
        self._updated = 0.0
        self._count = 0

    def set_frame(self, data: bytes) -> None:
        with self._condition:
            self._frame = data
            self._updated = time.time()
            self._count += 1
            self._condition.notify_all()

    def snapshot(self) -> tuple[bytes | None, float, int]:
        with self._condition:
            return self._frame, self._updated, self._count

    def wait_for_frame(self, last_count: int, timeout: float = 5.0) -> tuple[bytes | None, int]:
        with self._condition:
            self._condition.wait_for(lambda: self._count != last_count, timeout=timeout)
            return self._frame, self._count


class ObsReceiver:
    def __init__(self, port: int = 4767) -> None:
        self.port = port
        self.frames = FrameStore()
        self._server: ThreadingHTTPServer | None = None
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        if self._server:
            return
        handler = self._make_handler()
        self._server = ThreadingHTTPServer(("0.0.0.0", self.port), handler)
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        if not self._server:
            return
        self._server.shutdown()
        self._server.server_close()
        self._server = None

    def status(self) -> dict[str, Any]:
        frame, updated, count = self.frames.snapshot()
        age_ms = int((time.time() - updated) * 1000) if updated else None
        active = bool(frame and age_ms is not None and age_ms < 3000)
        lan_host = self._local_ip()
        return {
            "active": active,
            "framesReceived": count,
            "frameAgeMs": age_ms,
            "obsUrl": f"http://127.0.0.1:{self.port}/obs",
            "streamUrl": f"http://127.0.0.1:{self.port}/stream.mjpg",
            "postUrl": f"http://{lan_host}:{self.port}/frame",
            "receiverPort": self.port,
        }

    @staticmethod
    def _local_ip() -> str:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as probe:
                probe.connect(("8.8.8.8", 80))
                return probe.getsockname()[0]
        except OSError:
            try:
                return socket.gethostbyname(socket.gethostname())
            except OSError:
                return "127.0.0.1"

    def _make_handler(self) -> type[BaseHTTPRequestHandler]:
        frames = self.frames

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self) -> None:
                if self.path.startswith("/obs"):
                    self._send_obs_page()
                elif self.path.startswith("/stream.mjpg"):
                    self._send_stream()
                elif self.path.startswith("/health"):
                    self._send_bytes(b"ok", "text/plain")
                else:
                    self.send_error(404)

            def do_POST(self) -> None:
                if not self.path.startswith("/frame"):
                    self.send_error(404)
                    return
                length = int(self.headers.get("Content-Length", "0"))
                if length <= 0 or length > 8 * 1024 * 1024:
                    self.send_error(400, "Invalid frame size")
                    return
                data = self.rfile.read(length)
                frames.set_frame(data)
                self._send_bytes(b"ok", "text/plain")

            def log_message(self, *_args: object) -> None:
                return

            def _send_obs_page(self) -> None:
                html = b"""<!doctype html><html><head><meta charset='utf-8'>
<style>html,body{margin:0;width:100%;height:100%;background:#000;overflow:hidden}
img{width:100%;height:100%;object-fit:contain;background:#000}</style></head>
<body><img src='/stream.mjpg' alt='PhoneCam'></body></html>"""
                self._send_bytes(html, "text/html; charset=utf-8")

            def _send_stream(self) -> None:
                self.send_response(200)
                self.send_header("Content-Type", "multipart/x-mixed-replace; boundary=frame")
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                last_count = -1
                while True:
                    frame, last_count = frames.wait_for_frame(last_count)
                    if not frame:
                        continue
                    try:
                        self.wfile.write(b"--frame\r\nContent-Type: image/jpeg\r\n")
                        self.wfile.write(f"Content-Length: {len(frame)}\r\n\r\n".encode())
                        self.wfile.write(frame + b"\r\n")
                    except OSError:
                        break

            def _send_bytes(self, data: bytes, content_type: str) -> None:
                self.send_response(200)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

        return Handler
