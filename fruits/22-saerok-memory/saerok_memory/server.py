"""대시보드 서버. 127.0.0.1에서만 열고, 페이지를 열 때 넣어 준 일회용 토큰이 있어야 바꾸는 요청을 받습니다.

바꾸는 요청은 경로를 받지 않고 후보 id만 받습니다.
"""

import json
import secrets
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from . import apply, memory, sessions, versions
from .paths import data_home
from .store import INDEX_LIMIT, LINE_LIMIT, MEMORY_DAYS, SESSION_DAYS, VERSION_DAYS, read_json

WEB = Path(__file__).resolve().parent.parent / "web"
TYPES = {".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8", ".css": "text/css; charset=utf-8"}


def suggestions() -> dict:
    """trim 스킬이 남긴 AI 요약 문장. {후보 id: 문장}"""
    return read_json(data_home() / "suggestions.json", {}) or {}


def archived_sessions() -> int:
    path = data_home() / "session-archive.jsonl"
    return sum(1 for _ in open(path, encoding="utf-8")) if path.exists() else 0


def summary() -> dict:
    mem = memory.scan()
    ai = suggestions()
    for c in mem["candidates"]:
        if c["kind"] == "index_line" and c["id"] in ai:
            c["ai_proposal"] = ai[c["id"]]
    return {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "limits": {"line": LINE_LIMIT, "index": INDEX_LIMIT, "memory_days": MEMORY_DAYS,
                   "version_days": VERSION_DAYS, "session_days": SESSION_DAYS},
        "memory": mem,
        "versions": versions.scan(),
        "sessions": sessions.scan(),
        "archived_sessions": archived_sessions(),
        "hook_installed": apply.hook_installed(),
        "apply_log": list(reversed(apply.load_log())),
    }


class Handler(BaseHTTPRequestHandler):
    token = ""

    def log_message(self, *args):
        pass

    def _send(self, status: int, body: bytes, ctype: str = "application/json; charset=utf-8"):
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _json(self, status: int, value):
        self._send(status, json.dumps(value, ensure_ascii=False).encode("utf-8"))

    def _local_host(self) -> bool:
        host = (self.headers.get("Host") or "").split(":")[0]
        return host in ("127.0.0.1", "localhost")

    def do_GET(self):
        if not self._local_host():
            return self._send(403, b"forbidden", "text/plain")
        path = self.path.partition("?")[0]
        if path == "/api/summary":
            try:
                return self._json(200, summary())
            except Exception as e:  # 화면에 실패를 그대로 보여 줍니다.
                return self._json(500, {"error": f"검사 실패: {e}"})
        name = "index.html" if path == "/" else path.lstrip("/")
        file = (WEB / name).resolve()
        if file.parent != WEB.resolve() or not file.is_file():
            return self._send(404, b"not found", "text/plain")
        body = file.read_bytes()
        if file.name == "index.html":
            body = body.replace(b"__SAEROK_TOKEN__", self.token.encode())
        self._send(200, body, TYPES.get(file.suffix, "application/octet-stream"))

    def do_POST(self):
        # 거절할 요청도 본문을 먼저 다 읽습니다. 안 읽고 닫으면 Windows가 연결을 끊어 403 대신 오류가 납니다.
        try:
            raw = self.rfile.read(int(self.headers.get("Content-Length") or 0))
        except ValueError:
            return self._json(400, {"error": "본문 길이가 잘못됐습니다."})
        if not self._local_host() or not secrets.compare_digest(self.headers.get("X-Saerok-Token", ""), self.token):
            return self._json(403, {"error": "대시보드 페이지에서 보낸 요청만 받습니다."})
        try:
            body = json.loads(raw or b"{}")
            if self.path == "/api/trim":
                text = body.get("text")
                return self._json(200, apply.index_trim(str(body["id"]), str(text) if text else None))
            if self.path == "/api/archive":
                return self._json(200, apply.archive(str(body["id"])))
            if self.path == "/api/trash":
                ids = body.get("ids")
                if not isinstance(ids, list):
                    raise ValueError("ids는 목록이어야 합니다.")
                return self._json(200, apply.trash_items([str(i) for i in ids]))
            if self.path == "/api/hook":
                return self._json(200, apply.hook_install() if body.get("on") else apply.hook_remove())
            if self.path == "/api/undo":
                return self._json(200, apply.undo(str(body["id"])))
            return self._json(404, {"error": "없는 요청입니다."})
        except (KeyError, ValueError, RuntimeError, OSError) as e:
            return self._json(400, {"error": str(e)})


def serve(port: int = 8738, open_browser: bool = True) -> None:
    Handler.token = secrets.token_urlsafe(24)
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    url = f"http://127.0.0.1:{port}/"
    print(f"새록 가지치기 대시보드: {url}  (끝내려면 Ctrl+C)")
    if open_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
