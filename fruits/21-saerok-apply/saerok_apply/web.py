"""지원서 화면(web/)을 내 PC에서 엽니다. `saerok-apply`만 치면 이 서버가 뜨고 브라우저가 열립니다.

- 127.0.0.1에서만 듣고, 다른 사이트가 이 서버를 부르지 못하게 Host·Origin·전용 헤더를 확인합니다.
- 지원 폴더(~/.saerok/apply)의 정해진 파일(ledger.md·style.md, 회사 폴더의 posting.md·analysis.md·draft-*.md)만
  읽고 씁니다. 초안은 늘 새 이름으로 저장해 이전 판을 덮어쓰지 않습니다. 제출본은 store.submit이 19번 서류 폴더로 넘깁니다.
- Claude 호출은 기본으로 내 Claude 구독(`claude -p`)으로 돌립니다. 구독 방식은 글만 넘기므로 이미지 공고는 API 키 방식에서만 읽습니다."""

import json
import mimetypes
import threading
import urllib.error
import urllib.request
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from . import keystore, store, subscription

PLUGIN = Path(__file__).resolve().parent.parent
WEB = PLUGIN / "web"
DATA = PLUGIN / "data"
DEFAULT_PORT = 8760
UPSTREAM = "https://api.anthropic.com/v1/messages"
API_HEADER = "X-Saerok-Apply"
MAX_BODY = 8_000_000  # 캡처 이미지(base64)가 들어올 수 있습니다.
WRITE_LOCK = threading.Lock()
ENGINES = ("subscription", "api")
ENGINE = {"now": None}
HOME_FILES = (store.LEDGER, store.STYLE)
SAVE_COMPANY = ("posting.md", "analysis.md")


def engine() -> str:
    if ENGINE["now"] is None:
        ENGINE["now"] = "subscription" if subscription.cli() else "api"
    return ENGINE["now"]


def file_path(company: str, name: str, writing: bool = False) -> Path:
    """화면이 읽고 쓸 수 있는 파일만 경로로 바꿉니다. 그 밖의 이름은 ValueError."""
    if not company:
        if name not in HOME_FILES:
            raise ValueError("지원 폴더에서는 ledger.md·style.md만 다룹니다.")
        return store.home() / name
    if name not in SAVE_COMPANY and (writing or not store.DRAFT.match(name)):  # 초안은 /api/draft/new로만 씁니다.
        raise ValueError("회사 폴더에서는 posting.md·analysis.md·draft-*.md만 다룹니다.")
    return store.company_dir(company) / name


def _has_image(body: dict) -> bool:
    for m in body.get("messages") or []:
        content = m.get("content") if isinstance(m, dict) else None
        if isinstance(content, list) and any(isinstance(b, dict) and b.get("type") == "image" for b in content):
            return True
    return False


class Handler(BaseHTTPRequestHandler):
    server_version = "saerok-apply"

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

    def _allowed(self, api: bool) -> bool:
        port = self.server.server_address[1]
        host = self.headers.get("Host")
        if host not in (f"127.0.0.1:{port}", f"localhost:{port}"):
            self._error("이 화면은 127.0.0.1 주소로만 엽니다.", 403)
            return False
        if api:
            origin = self.headers.get("Origin")
            if self.headers.get(API_HEADER) != "1" or (origin and origin != f"http://{host}"):
                self._error("지원서 화면에서 온 요청만 받습니다.", 403)
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
        query = {k: v[0] for k, v in parse_qs(url.query).items()}
        try:
            if url.path == "/api/info":
                key, where = keystore.get_key()
                return self._json({"mode": "local", "home": str(store.home()), "interview_docs": str(store.interview_docs()),
                                   "warning": store.git_warning(), "companies": store.companies_here(),
                                   "key": keystore.masked(key), "key_from": where, "keyring": keystore.keyring is not None,
                                   "engine": engine(), "claude_cli": subscription.cli() is not None})
            if url.path == "/api/file":
                path = file_path(query.get("company", "").strip(), query.get("name", ""))
                return self._json({"path": str(path), "text": store.read(path)})
            if url.path == "/api/drafts":
                return self._json([p.name for p in store.drafts(query.get("company", "").strip())])
            if url.path == "/api/companies":
                return self._json(store.company_names())
        except ValueError as e:
            return self._error(str(e))
        if api:
            return self._error("없는 주소입니다.", 404)
        self._static(url.path)

    def _static(self, path: str) -> None:
        if path in ("", "/"):
            path = "/index.html"
        if path.startswith("/data/"):
            base, name = DATA, path[len("/data/"):]
        else:
            base, name = WEB, path.lstrip("/")
        target = (base / name).resolve()
        if base not in target.parents or not target.is_file():
            return self._error("없는 파일입니다.", 404)
        kind = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
        if kind.startswith("text/") or kind.endswith("javascript") or kind.endswith("json"):
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
        company = (data.get("company") or "").strip()
        if path == "/api/file":
            target = file_path(company, data.get("name") or "", writing=True)
            text = data.get("text")
            if not isinstance(text, str):
                raise ValueError("text는 글이어야 합니다.")
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text, encoding="utf-8")
            return self._json({"path": str(target), "privacy": store.scan(text), "warning": store.git_warning()})
        if path == "/api/draft/new":
            text = data.get("text")
            if not company or not isinstance(text, str) or not text.strip():
                raise ValueError("회사와 초안 글이 필요합니다.")
            target = store.new_draft_path(company)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text, encoding="utf-8")
            return self._json({"path": str(target), "name": target.name, "privacy": store.scan(text)})
        if path == "/api/check":
            target = file_path(company, data.get("draft") or "")
            if not store.DRAFT.match(target.name):
                raise ValueError("draft-*.md 초안만 검사합니다.")
            previous = data.get("previous") or ""
            prev = str(file_path(company, previous)) if previous else ""
            return self._json(store.run_check(target, company, previous=prev))
        if path == "/api/submit":
            target = file_path(company, data.get("draft") or "")
            if not store.DRAFT.match(target.name):
                raise ValueError("draft-*.md 초안만 넘깁니다.")
            return self._json(store.submit(target, company, dry_run=bool(data.get("dry_run"))))
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
        return self._error("없는 주소입니다.", 404)

    def _claude(self, body: dict) -> None:
        if engine() == "subscription":
            if _has_image(body):
                return self._error("구독 방식은 이미지를 넘기지 못합니다. 공고 본문을 붙여 넣거나 '키·설정'에서 API 키 방식을 골라 주세요.", 400)
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


def make_server(port: int = DEFAULT_PORT) -> ThreadingHTTPServer | None:
    for candidate in [port, *range(port + 1, port + 20), 0]:
        try:
            return ThreadingHTTPServer(("127.0.0.1", candidate), Handler)
        except OSError:
            continue
    return None


def serve(port: int = DEFAULT_PORT, open_browser: bool = True, use_api: bool = False) -> int:
    if use_api:
        ENGINE["now"] = "api"
    server = make_server(port)
    if server is None:
        print("빈 포트를 찾지 못했습니다.")
        return 1
    url = f"http://127.0.0.1:{server.server_address[1]}/"
    print(f"새록 지원서 화면: {url}")
    print(f"지원 폴더: {store.home()}")
    warning = store.git_warning()
    if warning:
        print("경고: " + warning)
    print("Claude 호출: " + ("내 Claude 구독(claude 명령)" if engine() == "subscription" else "API 키(크레딧 차감)"))
    print("끝내려면 Ctrl+C를 누르세요.")
    if open_browser:
        threading.Timer(0.3, webbrowser.open, [url]).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n지원서 화면을 닫았습니다.")
    finally:
        server.server_close()
    return 0
