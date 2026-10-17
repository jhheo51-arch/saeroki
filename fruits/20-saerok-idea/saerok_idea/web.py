"""심사 화면(web/)을 내 PC에서 엽니다. `saerok-idea`만 치면 이 서버가 뜨고 브라우저가 열립니다.

- 127.0.0.1에서만 듣고, 다른 사이트가 이 서버를 부르지 못하게 Host·Origin·전용 헤더를 확인합니다.
- 기록은 store를 거쳐 ~/.saerok/idea에만 쓰고, 그 밖의 폴더는 읽거나 쓰지 않습니다.
- Claude 호출은 이 서버가 자격 증명 관리자의 키를 붙여 Anthropic에 그대로 넘깁니다. 키는 브라우저로 보내지 않습니다."""

import json
import mimetypes
import threading
import urllib.error
import urllib.request
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from . import keystore, store

PLUGIN = Path(__file__).resolve().parent.parent
WEB = PLUGIN / "web"
AGENTS = PLUGIN / "agents"
DEFAULT_PORT = 8740
UPSTREAM = "https://api.anthropic.com/v1/messages"
API_HEADER = "X-Saerok-Idea"
MAX_BODY = 2_000_000
# 화면은 심사위원 3명·조사 결과를 동시에 보냅니다. result.json을 읽고 고쳐 쓰는 동안 다른 요청이 끼면 앞 기록이 사라지므로 한 번에 하나씩 씁니다.
WRITE_LOCK = threading.Lock()


def _inside_home(path: str) -> Path:
    folder = store.run_of(path).resolve()
    home = store.home()
    if folder != home and home not in folder.parents:
        raise ValueError("기록 폴더 밖의 경로는 쓰지 않습니다.")
    return folder


def ideas() -> list[dict]:
    """기록 폴더의 아이디어별 기록 목록(새것이 먼저)."""
    home = store.home()
    if not home.is_dir():
        return []
    out = []
    for idea_folder in sorted(p for p in home.iterdir() if p.is_dir()):
        runs = []
        for run in store.runs(idea_folder):
            try:
                runs.append({"run": run.name, "folder": str(run), "result": store.load(run)})
            except (ValueError, json.JSONDecodeError):
                continue
        if runs:
            out.append({"slug": idea_folder.name, "runs": runs})
    out.sort(key=lambda i: max(r["run"] for r in i["runs"]), reverse=True)
    return out


class Handler(BaseHTTPRequestHandler):
    server_version = "saerok-idea"

    def log_message(self, *args):  # 아이디어가 담길 수 있는 요청 줄을 터미널에 남기지 않습니다.
        pass

    # ---------- 공통 ----------
    def _send(self, status: int, body: bytes, kind: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", kind)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, data, status: int = 200) -> None:
        self._send(status, json.dumps(data, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")

    def _error(self, message: str, status: int = 400) -> None:
        self._json({"error": message}, status)

    def _origin(self) -> str:
        return f"http://{self.headers.get('Host', '')}"

    def _allowed(self, api: bool) -> bool:
        port = self.server.server_address[1]
        if self.headers.get("Host") not in (f"127.0.0.1:{port}", f"localhost:{port}"):
            self._error("이 화면은 127.0.0.1 주소로만 엽니다.", 403)
            return False
        if api:
            origin = self.headers.get("Origin")
            if self.headers.get(API_HEADER) != "1" or (origin and origin != self._origin()):
                self._error("심사 화면에서 온 요청만 받습니다.", 403)
                return False
        return True

    def _body(self) -> dict:
        size = int(self.headers.get("Content-Length") or 0)
        if size > MAX_BODY:
            raise ValueError("요청이 너무 큽니다.")
        raw = self.rfile.read(size) if size else b"{}"
        try:
            data = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise ValueError("JSON을 읽지 못했습니다.")
        if not isinstance(data, dict):
            raise ValueError("JSON 객체여야 합니다.")
        return data

    # ---------- GET ----------
    def do_GET(self):
        url = urlparse(self.path)
        api = url.path.startswith("/api/")
        if not self._allowed(api):
            return
        if url.path == "/api/info":
            key, where = keystore.get_key()
            return self._json({"mode": "local", "home": str(store.home()), "key": keystore.masked(key), "key_from": where,
                               "keyring": keystore.keyring is not None})
        if url.path == "/api/runs":
            return self._json(ideas())
        if url.path == "/api/result":
            try:
                folder = _inside_home(parse_qs(url.query).get("folder", [""])[0])
                return self._json({"folder": str(folder), "run": folder.name, "result": store.load(folder)})
            except ValueError as e:
                return self._error(str(e))
        if api:
            return self._error("없는 주소입니다.", 404)
        self._static(url.path)

    def _static(self, path: str) -> None:
        if path in ("", "/"):
            path = "/index.html"
        base, name = (AGENTS, path[len("/agents/"):]) if path.startswith("/agents/") else (WEB, path.lstrip("/"))
        target = (base / name).resolve()
        if base not in target.parents or not target.is_file():
            return self._error("없는 파일입니다.", 404)
        kind = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
        if target.suffix == ".md":
            kind = "text/markdown"
        if kind.startswith("text/") or kind.endswith("javascript"):
            kind += "; charset=utf-8"
        self._send(200, target.read_bytes(), kind)

    # ---------- POST ----------
    def do_POST(self):
        path = urlparse(self.path).path
        if not self._allowed(True):
            return
        try:
            data = self._body()
            if path == "/api/claude":
                return self._claude(data)
            with WRITE_LOCK:
                return self._write(path, data)
        except (ValueError, TypeError, KeyError, AttributeError) as e:
            return self._error(str(e) or "요청 형식이 맞지 않습니다.")

    def _write(self, path: str, data: dict) -> None:
        if path == "/api/key":
            where = keystore.set_key(data.get("key") or "")
            return self._json({"key": keystore.masked(keystore.get_key()[0]), "key_from": where})
        if path == "/api/key/delete":
            keystore.delete_key()
            key, where = keystore.get_key()
            return self._json({"key": keystore.masked(key), "key_from": where})
        if path == "/api/new":
            return self._json(self._new(data))
        if path == "/api/record":
            folder = _inside_home(data.get("folder") or "")
            return self._json(store.record(folder, data.get("part"), data.get("data")))
        if path == "/api/report":
            folder = _inside_home(data.get("folder") or "")
            report = store.write_report(folder)
            return self._json({"path": str(report), "markdown": report.read_text(encoding="utf-8"),
                               "decided": store.decide(folder), "result": store.load(folder)})
        return self._error("없는 주소입니다.", 404)

    def _new(self, data: dict) -> dict:
        origin = data.get("from")
        if origin:
            prev = _inside_home(origin.get("folder") or "")
            number = origin.get("direction")
            # 화면에서 방향 입력을 고쳤으면 고친 입력을 씁니다. 출처(from)는 그대로 남깁니다.
            idea = data.get("idea") or (store.direction(prev, number)["idea"] if number else store.load(prev)["idea"])
            made = store.create(idea, name=prev.parent.name, base=prev.parent.parent,
                                origin={"verdict": str(prev / "verdict.md"), "direction": number})
        else:
            made = store.create(data.get("idea") or {})
        folder = Path(made["folder"])
        return {"folder": str(folder), "run": folder.name, "slug": folder.parent.name, "result": store.load(folder)}

    def _claude(self, body: dict) -> None:
        key, _ = keystore.get_key()
        if not key:
            return self._error("Claude API 키가 없습니다. 화면 위 '키' 칸에 등록해 주세요.", 401)
        request = urllib.request.Request(UPSTREAM, data=json.dumps(body).encode("utf-8"), method="POST", headers={
            "x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"})
        try:
            with urllib.request.urlopen(request, timeout=600) as response:
                status, raw = response.status, response.read()
        except urllib.error.HTTPError as e:
            status, raw = e.code, e.read()
        except (urllib.error.URLError, TimeoutError) as e:
            return self._error(f"Anthropic에 닿지 못했습니다: {e}", 502)
        self._send(status, raw, "application/json; charset=utf-8")


def serve(port: int = DEFAULT_PORT, open_browser: bool = True) -> int:
    server = None
    for candidate in [port, *range(port + 1, port + 20), 0]:
        try:
            server = ThreadingHTTPServer(("127.0.0.1", candidate), Handler)
            break
        except OSError:
            continue
    if server is None:
        print("빈 포트를 찾지 못했습니다.")
        return 1
    url = f"http://127.0.0.1:{server.server_address[1]}/"
    print(f"새록 심사단 화면: {url}")
    print(f"기록 폴더: {store.home()}")
    print("끝내려면 Ctrl+C를 누르세요.")
    if open_browser:
        threading.Timer(0.3, webbrowser.open, [url]).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n심사 화면을 닫았습니다.")
    finally:
        server.server_close()
    return 0
