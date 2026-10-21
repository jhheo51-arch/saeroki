"""면접 화면(web/)을 내 PC에서 엽니다. `saerok-interview`만 치면 이 서버가 뜨고 브라우저가 열립니다.

- 127.0.0.1에서만 듣고, 다른 사이트가 이 서버를 부르지 못하게 Host·Origin·전용 헤더를 확인합니다.
- 세션은 session·store를 거쳐 면접 폴더(~/.saerok/interview)에만 쓰고, 그 밖의 폴더는 읽거나 쓰지 않습니다.
- Claude 호출은 기본으로 내 Claude 구독(Claude Code의 `claude -p`)으로 돌립니다(subscription.py).
  API 키 방식을 고르면 자격 증명 관리자의 키를 붙여 Anthropic에 그대로 넘깁니다. 키는 브라우저로 보내지 않습니다."""

import json
import mimetypes
import threading
import urllib.error
import urllib.request
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from . import docs, keystore, session, store, subscription, terms

PLUGIN = Path(__file__).resolve().parent.parent
WEB = PLUGIN / "web"
AGENTS = PLUGIN / "agents"
DATA = PLUGIN / "data"
DEFAULT_PORT = 8750
UPSTREAM = "https://api.anthropic.com/v1/messages"
API_HEADER = "X-Saerok-Interview"
MAX_BODY = 2_000_000
# 화면은 면접관 5명 결과를 동시에 보냅니다. score.json을 읽고 고쳐 쓰는 동안 다른 요청이 끼면 앞 기록이 사라지므로 한 번에 하나씩 씁니다.
WRITE_LOCK = threading.Lock()
ENGINES = ("subscription", "api")
# 어떤 방식으로 Claude를 부를지. 기본은 구독(claude 명령이 있을 때), 없으면 API 키.
ENGINE = {"now": None}
RECORD = {"document": store.record_document, "answer": store.record_answer, "real": store.record_real}


def engine() -> str:
    if ENGINE["now"] is None:
        ENGINE["now"] = "subscription" if subscription.cli() else "api"
    return ENGINE["now"]


def _inside_home(path: str) -> Path:
    if not path:
        raise ValueError("세션 폴더가 없습니다.")
    folder = Path(path).resolve()
    home = session.home()
    if home not in folder.parents:
        raise ValueError("면접 폴더 밖의 경로는 쓰지 않습니다.")
    session.load(folder)  # 세션 폴더가 아니면 여기서 멈춥니다.
    return folder


def sessions() -> list[dict]:
    """면접 폴더의 세션 목록(이름 순). 본문(inputs)은 넣지 않습니다."""
    out = []
    for folder in session.sessions():
        try:
            meta, score = session.load(folder)
        except (ValueError, json.JSONDecodeError):
            continue
        out.append({"folder": str(folder), "meta": meta, "score": score})
    return out


class Handler(BaseHTTPRequestHandler):
    server_version = "saerok-interview"

    def log_message(self, *args):  # 회사 이름 같은 요청 줄을 터미널에 남기지 않습니다.
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
                self._error("면접 화면에서 온 요청만 받습니다.", 403)
                return False
        return True

    def _read_raw(self) -> None:
        # 거절할 요청도 본문을 먼저 읽어 둡니다. 읽지 않은 채 닫으면 Windows에서 연결이 끊겨(RST) 응답이 사라집니다.
        try:
            size = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            size = -1
        self._bad_size = size < 0 or size > MAX_BODY
        if self._bad_size:
            self.close_connection = True
        self._raw = b"" if self._bad_size or not size else self.rfile.read(size)

    def _body(self) -> dict:
        if self._bad_size:
            raise ValueError("요청이 너무 크거나 본문 길이가 잘못됐습니다.")
        raw = self._raw or b"{}"
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
        query = parse_qs(url.query)
        try:
            if url.path == "/api/info":
                key, where = keystore.get_key()
                return self._json({"mode": "local", "home": str(session.home()), "key": keystore.masked(key), "key_from": where,
                                   "keyring": keystore.keyring is not None, "engine": engine(),
                                   "claude_cli": subscription.cli() is not None})
            if url.path == "/api/sessions":
                return self._json(sessions())
            if url.path == "/api/session":
                folder = _inside_home(query.get("folder", [""])[0])
                meta, score = session.load(folder)
                return self._json({"folder": str(folder), "meta": meta, "score": score, "inputs": session.inputs(folder, meta)})
            if url.path == "/api/docs":
                found = docs.pick(query.get("company", [""])[0].strip())
                texts = {kind: session.read(Path(path)) for kind, path in (found["pick"] or {}).items()}
                return self._json({**found, "texts": texts})
        except ValueError as e:
            return self._error(str(e))
        if api:
            return self._error("없는 주소입니다.", 404)
        self._static(url.path)

    def _static(self, path: str) -> None:
        if path in ("", "/"):
            path = "/index.html"
        if path.startswith("/agents/"):
            base, name = AGENTS, path[len("/agents/"):]
        elif path.startswith("/data/"):
            base, name = DATA, path[len("/data/"):]
        else:
            base, name = WEB, path.lstrip("/")
        target = (base / name).resolve()
        if base not in target.parents or not target.is_file():
            return self._error("없는 파일입니다.", 404)
        kind = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
        if target.suffix == ".md":
            kind = "text/markdown"
        if kind.startswith("text/") or kind.endswith("javascript") or kind.endswith("json"):
            kind += "; charset=utf-8"
        self._send(200, target.read_bytes(), kind)

    # ---------- POST ----------
    def do_POST(self):
        path = urlparse(self.path).path
        self._read_raw()
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
        if path == "/api/engine":
            choice = data.get("engine")
            if choice not in ENGINES:
                raise ValueError("engine은 subscription 또는 api입니다.")
            if choice == "subscription" and not subscription.cli():
                raise ValueError("claude 명령을 찾지 못했습니다. Claude Code를 설치하고 로그인해 주세요.")
            ENGINE["now"] = choice
            return self._json({"engine": choice})
        if path == "/api/key":
            where = keystore.set_key(data.get("key") or "")
            return self._json({"key": keystore.masked(keystore.get_key()[0]), "key_from": where})
        if path == "/api/key/delete":
            keystore.delete_key()
            key, where = keystore.get_key()
            return self._json({"key": keystore.masked(key), "key_from": where})
        if path == "/api/docs/init":
            return self._json(docs.init())
        if path == "/api/new":
            return self._json(self._new(data))
        if path == "/api/record":
            folder = _inside_home(data.get("folder") or "")
            kind = data.get("kind")
            if kind not in RECORD:
                raise ValueError("kind는 document·answer·real 중 하나입니다.")
            if not isinstance(data.get("data"), dict):
                raise ValueError("data는 JSON 객체여야 합니다.")
            return self._json({"result": RECORD[kind](folder, data["data"])})
        if path == "/api/report":
            folder = _inside_home(data.get("folder") or "")
            report = store.write_report(folder)
            meta, score = session.load(folder)
            return self._json({"path": str(report), "verdict": report.read_text(encoding="utf-8"),
                               "practice": store.render_practice(meta, score)})
        return self._error("없는 주소입니다.", 404)

    def _new(self, data: dict) -> dict:
        texts = data.get("texts")
        if not isinstance(texts, dict):
            raise ValueError("texts는 서류 종류별 본문 객체여야 합니다.")
        industry, role = data.get("industry") or "", data.get("role") or ""
        if bool(industry) != bool(role):
            raise ValueError("산업과 직무는 함께 고르거나 함께 비워 주세요.")
        if industry:
            terms.pick(industry, role, limit=1)  # 잘못된 id를 먼저 막습니다.
        made = session.create_texts(texts, company=(data.get("company") or "").strip(), industry=industry, role=role)
        folder = Path(made["folder"])
        meta, score = session.load(folder)
        return {"folder": str(folder), "meta": meta, "score": score, "inputs": session.inputs(folder, meta),
                "privacy": made["privacy"]}

    def _claude(self, body: dict) -> None:
        if engine() == "subscription":
            try:
                return self._json(subscription.call(body))
            except RuntimeError as e:
                return self._error(str(e), 502)
        key, _ = keystore.get_key()
        if not key:
            return self._error("Claude API 키가 없습니다. 화면 위 '키·설정'에서 등록해 주세요.", 401)
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


def serve(port: int = DEFAULT_PORT, open_browser: bool = True, use_api: bool = False) -> int:
    if use_api:
        ENGINE["now"] = "api"
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
    print(f"새록 면접관 화면: {url}")
    print(f"면접 폴더: {session.home()}")
    print("Claude 호출: " + ("내 Claude 구독(claude 명령)" if engine() == "subscription" else "API 키(크레딧 차감)"))
    print("끝내려면 Ctrl+C를 누르세요.")
    if open_browser:
        threading.Timer(0.3, webbrowser.open, [url]).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n면접 화면을 닫았습니다.")
    finally:
        server.server_close()
    return 0
