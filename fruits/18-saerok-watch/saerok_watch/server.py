"""대시보드 서버. 127.0.0.1에서만 열고, 페이지를 열 때 넣어 준 일회용 토큰이 있어야 바꾸는 요청을 받습니다."""

import json
import secrets
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from . import advise, apply, character, effect, notify, scan
from .paths import data_home
from .store import load_config, read_json, save_config

WEB = Path(__file__).resolve().parent.parent / "web"
TYPES = {".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8", ".css": "text/css; charset=utf-8"}
LIVE_SECONDS = 30 * 60


def recent_alerts(limit: int = 30) -> list[dict]:
    path = data_home() / "alerts.jsonl"
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines()[-limit:]:
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    return list(reversed(rows))


def session_detail(session_id: str) -> dict | None:
    """추이 탭 세션 그래프: 응답별 컨텍스트 곡선과 급증 지점."""
    for s in scan.scan_all():
        if s["session_id"] == session_id:
            return {"session_id": session_id, "title": s["title"], "project": s["project"],
                    "responses": s["responses"], "timeline": scan.downsample(s.get("timeline") or []),
                    "spikes": sorted(s.get("spikes") or [], key=lambda x: x["n"])}
    return None


def summary() -> dict:
    sessions = scan.scan_all()
    config = load_config()
    now = time.time()
    log = apply.load_log()
    hook_state = read_json(data_home() / "hook-state.json", {}) or {}
    live = []
    for s in sessions:
        if now - s.get("mtime", 0) > LIVE_SECONDS:
            continue
        live.append({k: s[k] for k in ("session_id", "project", "title", "responses", "last_ctx", "max_ctx", "images", "compactions", "last_ts")})
    table = [{k: s[k] for k in ("session_id", "project", "title", "first_ts", "last_ts", "responses",
                                "processed", "max_ctx", "images", "compactions", "buckets")} for s in sessions]
    return {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "config": config,
        "totals": scan.totals(sessions),
        "live": live,
        "daily": scan.daily(sessions),
        "sessions": table,
        "suggestions": advise.suggestions(sessions, config),
        "spike_kinds": scan.spike_summary(advise._recent(sessions)),
        "environment": advise.environment(),
        "alerts": recent_alerts(),
        "hook_sessions": len(hook_state),
        "apply_log": list(reversed(log)),
        "effects": effect.effects(sessions, log),
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
        path, _, query = self.path.partition("?")
        if path == "/api/session":
            from urllib.parse import parse_qs
            detail = session_detail((parse_qs(query).get("id") or [""])[0])
            return self._json(200, detail) if detail else self._json(404, {"error": "세션을 찾지 못했습니다."})
        if path == "/api/summary":
            try:
                return self._json(200, summary())
            except Exception as e:  # 화면에 실패를 그대로 보여 줍니다.
                return self._json(500, {"error": f"집계 실패: {e}"})
        if path in ("/character.svg", "/character.png"):
            try:
                if path.endswith(".svg"):
                    return self._send(200, character.render_svg().encode("utf-8"), "image/svg+xml")
                return self._send(200, character.render_png(), "image/png")
            except Exception:  # 그림을 못 그려도 대시보드는 열립니다.
                return self._send(404, b"no character", "text/plain")
        name = "index.html" if path == "/" else path.lstrip("/")
        file = (WEB / name).resolve()
        if file.parent != WEB.resolve() or not file.is_file():
            return self._send(404, b"not found", "text/plain")
        body = file.read_bytes()
        if file.name == "index.html":
            body = body.replace(b"__SAEROK_TOKEN__", self.token.encode())
        self._send(200, body, TYPES.get(file.suffix, "application/octet-stream"))

    def do_POST(self):
        # 거절할 요청도 본문을 먼저 다 읽습니다. 안 읽은 채 연결을 닫으면 Windows가 연결을 끊어(RST) 403 대신 오류가 납니다.
        try:
            raw = self.rfile.read(int(self.headers.get("Content-Length") or 0))
        except ValueError:
            return self._json(400, {"error": "본문 길이가 잘못됐습니다."})
        if not self._local_host() or not secrets.compare_digest(self.headers.get("X-Saerok-Token", ""), self.token):
            return self._json(403, {"error": "대시보드 페이지에서 보낸 요청만 받습니다."})
        try:
            body = json.loads(raw or b"{}")
            if self.path == "/api/apply":
                return self._json(200, apply.apply(str(body["action"])))
            if self.path == "/api/undo":
                return self._json(200, apply.undo(str(body["id"])))
            if self.path == "/api/config":
                config = save_config(int(body["caution"]), int(body["warn"]), bool(body.get("toast", True)))
                return self._json(200, {"ok": True, "config": config})
            if self.path == "/api/test-toast":
                ok = notify.toast(*notify.TEST, wait=True)
                return self._json(200, {"ok": ok, "message": "알림을 보냈습니다. 화면 오른쪽 아래를 확인하세요." if ok else "Windows에서만 알림을 띄울 수 있습니다."})
            return self._json(404, {"error": "없는 요청입니다."})
        except (KeyError, ValueError, RuntimeError) as e:
            return self._json(400, {"error": str(e)})


def serve(port: int = 8718, open_browser: bool = True) -> None:
    Handler.token = secrets.token_urlsafe(24)
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    url = f"http://127.0.0.1:{port}/"
    print(f"새록 파수꾼 대시보드: {url}  (끝내려면 Ctrl+C)")
    if open_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
