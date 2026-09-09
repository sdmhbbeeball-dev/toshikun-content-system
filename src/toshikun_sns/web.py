from __future__ import annotations

import argparse
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import threading
from typing import Any, Callable
import webbrowser

from .client import ApiError, generate_json
from .config import Settings
from .prompt import SYSTEM_PROMPT, build_prompt
from .quality import report, validate


STATIC_DIR = Path(__file__).with_name("static")
MAX_REQUEST_BYTES = 2 * 1024 * 1024


def generate_content(manuscript: str, access_password: str = "") -> dict[str, Any]:
    manuscript = manuscript.strip()
    if not manuscript:
        raise ValueError("YouTube原稿を貼り付けてください。")
    expected_password = os.getenv("TOSHIKUN_ACCESS_PASSWORD", "")
    if expected_password and access_password != expected_password:
        raise ValueError("アクセスパスワードが違います。管理者に確認してください。")
    settings = Settings.from_env()
    content = generate_json(
        api_url=settings.api_url,
        model=settings.model,
        system=SYSTEM_PROMPT,
        prompt=build_prompt(manuscript, settings),
    )
    return {"content": content, "quality": report(validate(content, manuscript, settings))}


class AppHandler(BaseHTTPRequestHandler):
    generator: Callable[[str, str], dict[str, Any]] = staticmethod(generate_content)

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/health":
            self._json({"status": "ok"})
            return
        files = {"/": "index.html", "/app.js": "app.js", "/style.css": "style.css"}
        filename = files.get(self.path)
        if filename is None:
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        content_type = "text/html" if filename.endswith(".html") else (
            "text/javascript" if filename.endswith(".js") else "text/css"
        )
        self._send(STATIC_DIR.joinpath(filename).read_bytes(), content_type)

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/api/generate":
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length > MAX_REQUEST_BYTES:
                raise ValueError("原稿が大きすぎます。2MB以内にしてください。")
            payload = json.loads(self.rfile.read(length))
            result = self.generator(
                str(payload.get("manuscript", "")), str(payload.get("access_password", ""))
            )
            self._json(result)
        except (ValueError, TypeError, json.JSONDecodeError, ApiError) as error:
            self._json({"error": str(error)}, HTTPStatus.BAD_REQUEST)
        except OSError as error:
            self._json({"error": f"通信または保存に失敗しました: {error}"}, HTTPStatus.BAD_GATEWAY)

    def _json(self, value: Any, status: HTTPStatus = HTTPStatus.OK) -> None:
        self._send(json.dumps(value, ensure_ascii=False).encode(), "application/json", status)

    def _send(self, body: bytes, content_type: str, status: HTTPStatus = HTTPStatus.OK) -> None:
        self.send_response(status)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        return


def parser() -> argparse.ArgumentParser:
    command = argparse.ArgumentParser(description="としくんSNS制作ライン ブラウザ版")
    command.add_argument("--host", default=os.getenv("HOST", "127.0.0.1"))
    command.add_argument("--port", type=int, default=int(os.getenv("PORT", "8765")))
    command.add_argument("--no-browser", action="store_true")
    return command


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    server = ThreadingHTTPServer((args.host, args.port), AppHandler)
    url = f"http://{args.host}:{server.server_port}"
    print(f"ブラウザ版を起動しました: {url}")
    print("終了するときは、このウィンドウを閉じてください。")
    if not args.no_browser:
        threading.Timer(0.4, webbrowser.open, args=(url,)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
