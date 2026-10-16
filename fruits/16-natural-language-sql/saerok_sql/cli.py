"""PowerShell에서 `saerok-sql`로 여는 대화형 터미널."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from rich.console import Console
from rich.markup import escape
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

from . import dictionary as dict_mod
from . import keystore
from .agent import Agent, Answer
from .db import Database, app_dir
from .history import History
from .llm import DEFAULT_MODEL, MODELS, ClaudeBrain
from .router import route

SHOW_ROWS = 20
ACCENT = "#40916C"
STATUS_LABEL = {
    "ok": ("[bold green]완료[/]", "green"),
    "review": ("[bold yellow]검토 필요[/]", "yellow"),
    "error": ("[bold red]실패[/]", "red"),
    "blocked": ("[bold red]실행 막음[/]", "red"),
    "cannot_answer": ("[bold yellow]답할 수 없음[/]", "yellow"),
}

HELP = """[bold]물어보기[/]  우리말로 물으면 SQL을 만들어 실행합니다. 예: 2025년 따릉이를 가장 많이 탄 동 5곳은?
[bold]풀이[/]      SELECT·WITH로 시작하는 SQL을 붙여 넣으면 무엇을 하는지 풀어 줍니다.

/tables              표 목록
/describe 표이름      컬럼·기간·주의점
/explain 파일.sql     파일의 SQL 풀이
/history [개수]       최근 기록
/export 파일          기록 내보내기(다른 PC로 옮기기)
/import 파일          기록 불러오기
/model [sonnet|opus|haiku]  모델 보기·바꾸기
/key                 API 키 다시 등록
/exit                끝내기"""


def _cell(value) -> str:
    if value is None:
        return "[dim]NULL[/]"
    if isinstance(value, float):
        return f"{value:,.2f}"
    if isinstance(value, int) and not isinstance(value, bool):
        return f"{value:,}"
    return escape(str(value))


def render_answer(console: Console, answer: Answer, show_rows: int = SHOW_ROWS) -> None:
    label, color = STATUS_LABEL.get(answer.status, (answer.status, "white"))
    head = f"{label}  [dim]AI가 작성 · 시도 {answer.attempts}번[/]"
    console.print(head)
    if answer.summary:
        console.print(Panel(escape(answer.summary), title="무엇을 하는 SQL인가요", border_style=ACCENT, title_align="left"))
    if answer.assumptions:
        console.print(Panel("\n".join(f"• {escape(a)}" for a in answer.assumptions), title="가정", border_style="yellow", title_align="left"))
    if answer.sql:
        console.print(Panel(Syntax(answer.sql, "sql", word_wrap=True, background_color="default"), title="SQL", border_style=ACCENT, title_align="left"))
    if answer.message:
        console.print(f"[{color}]{escape(answer.message)}[/]")
    if answer.result is not None:
        result = answer.result
        table = Table(show_lines=False, header_style=f"bold {ACCENT}")
        for column in result.columns:
            table.add_column(escape(column), overflow="fold")
        for row in result.rows[:show_rows]:
            table.add_row(*[_cell(v) for v in row])
        total = f"{len(result.rows):,}행" + (" 이상(앞 1,000행만)" if result.truncated else "")
        shown = f" · 앞 {show_rows}행 표시" if len(result.rows) > show_rows else ""
        console.print(table)
        console.print(f"[dim]{total}{shown} · {result.seconds:.2f}초[/]")
    if answer.result_shape:
        console.print(f"[dim]결과 한 행 = {escape(answer.result_shape)}[/]")
    if answer.explanation:
        steps = Table(show_header=True, header_style="bold", box=None, padding=(0, 1))
        steps.add_column("부분", style=ACCENT, no_wrap=False)
        steps.add_column("하는 일")
        for step in answer.explanation:
            steps.add_row(escape(step.get("part", "")), escape(step.get("meaning", "")))
        console.print(Panel(steps, title="풀이", border_style=ACCENT, title_align="left"))
    notes = answer.review + answer.caveats + answer.data_notes
    if notes:
        console.print(Panel("\n".join(f"• {escape(n)}" for n in dict.fromkeys(notes)), title="한계·주의", border_style="yellow", title_align="left"))


def render_tables(console: Console, dictionary: dict) -> None:
    table = Table(header_style=f"bold {ACCENT}")
    table.add_column("표")
    table.add_column("설명")
    table.add_column("기간", style="dim")
    for name in sorted(dictionary["tables"]):
        info = dictionary["tables"][name]
        table.add_row(name, escape(info["description"]), escape(info["period"]))
    console.print(table)


def render_describe(console: Console, dictionary: dict, schema: dict, name: str) -> None:
    info = dictionary["tables"].get(name)
    if not info:
        console.print(f"[red]그런 표가 없습니다: {escape(name)}[/] /tables로 목록을 보세요.")
        return
    types = dict(schema.get(name, []))
    console.print(f"[bold]{name}[/] · {escape(info['description'])}")
    console.print(f"[dim]한 행: {escape(info['grain'])} · 기간: {escape(info['period'])}[/]")
    console.print(f"[dim]출처: {escape(info['source'])} · 이용 조건: {escape(info['license'])}[/]")
    cols = Table(header_style=f"bold {ACCENT}")
    cols.add_column("컬럼")
    cols.add_column("형식", style="dim")
    cols.add_column("뜻")
    for column, meaning in info["columns"].items():
        cols.add_row(column, types.get(column, "?"), escape(meaning))
    console.print(cols)
    for note in info["notes"]:
        console.print(f"[yellow]• {escape(note)}[/]")


def ask_key(console: Console) -> str | None:
    import getpass

    if not sys.stdin.isatty():
        console.print("[red]API 키는 터미널 창에서 saerok-sql을 실행해 /key로 등록해 주세요.[/]")
        return None
    console.print("Claude API 키가 필요합니다. https://console.anthropic.com 의 API Keys에서 만든 키를 붙여 넣어 주세요.")
    console.print("[dim]키는 Windows 자격 증명 관리자에만 저장되고 화면·파일에 남지 않습니다. 빈칸으로 두면 취소합니다.[/]")
    key = getpass.getpass("API 키> ").strip()
    if not key:
        return None
    try:
        keystore.set_key(key)
    except ValueError as e:
        console.print(f"[red]{e}[/]")
        return None
    console.print("[green]저장했습니다.[/]")
    return key


class App:
    def __init__(self, console: Console, model: str = DEFAULT_MODEL, keep_history: bool = True):
        self.console = console
        self.model = model
        self.history = History() if keep_history else None
        with console.status("데이터 준비 중… (처음 한 번만 조금 걸립니다)"):
            self.db = Database()
        self.dictionary = dict_mod.load()
        self.schema = self.db.tables()
        self.agent: Agent | None = None
        self.last_status = "error"

    def ensure_agent(self, interactive: bool) -> bool:
        if self.agent:
            return True
        key = keystore.get_key()
        if not key and interactive:
            key = ask_key(self.console)
        if not key:
            self.console.print("[red]API 키가 없어 AI에게 물을 수 없습니다.[/] saerok-sql을 실행해 /key로 등록해 주세요.")
            return False
        self.agent = Agent(ClaudeBrain(key, self.model), self.db, self.dictionary)
        return True

    def handle(self, raw: str, interactive: bool = True) -> bool:
        """한 줄을 처리합니다. 끝내야 하면 False를 돌려줍니다."""
        r = route(raw)
        if r.kind == "empty":
            return True
        if r.kind == "command":
            return self.command(r.command, r.arg, interactive)
        if not self.ensure_agent(interactive):
            return True
        with self.console.status("생각하는 중…" if r.kind == "question" else "풀이하는 중…"):
            answer = self.agent.ask(r.text) if r.kind == "question" else self.agent.explain(r.text)
        render_answer(self.console, answer)
        if self.history:
            self.history.add(answer, self.model)
        self.last_status = answer.status
        return True

    def command(self, name: str, arg: str, interactive: bool) -> bool:
        c = self.console
        if name in ("exit", "quit", "q"):
            return False
        if name in ("help", "?"):
            c.print(HELP)
        elif name == "tables":
            render_tables(c, self.dictionary)
        elif name == "describe":
            render_describe(c, self.dictionary, self.schema, arg)
        elif name == "explain":
            path = Path(arg.strip('"'))
            if not arg or not path.exists():
                c.print("[red]SQL 파일 경로를 적어 주세요.[/] 예: /explain report.sql")
            else:
                return self.handle(path.read_text(encoding="utf-8-sig"), interactive)
        elif name == "history":
            if not self.history:
                c.print("기록을 끄고 실행했습니다.")
                return True
            n = int(arg) if arg.isdigit() else 10
            table = Table(header_style=f"bold {ACCENT}")
            for col in ("때", "입력", "상태", "행"):
                table.add_column(col)
            for e in self.history.recent(n):
                table.add_row(e["at"][5:16].replace("T", " "), escape(e["input"][:60]), e["status"], "" if e["rows"] is None else str(e["rows"]))
            c.print(table)
            c.print(f"[dim]기록 파일: {self.history.path}[/]")
        elif name == "export":
            if not self.history or not arg:
                c.print("[red]내보낼 파일 이름을 적어 주세요.[/] 예: /export 새록SQL기록.json")
            else:
                c.print(f"{self.history.export(Path(arg.strip(chr(34))))}개 기록을 내보냈습니다.")
        elif name == "import":
            if not self.history or not arg or not Path(arg.strip('"')).exists():
                c.print("[red]불러올 파일 경로를 적어 주세요.[/]")
            else:
                try:
                    c.print(f"새 기록 {self.history.import_(Path(arg.strip(chr(34))))}개를 불러왔습니다.")
                except (ValueError, KeyError) as e:
                    c.print(f"[red]불러오지 못했습니다: {escape(str(e))}[/]")
        elif name == "model":
            if not arg:
                c.print(f"지금 모델: [bold]{self.model}[/]  ·  고를 수 있음: {', '.join(MODELS)}")
            elif arg.lower() in MODELS:
                self.model = MODELS[arg.lower()]
                self.agent = None
                c.print(f"모델을 {self.model}로 바꿨습니다.")
            else:
                c.print(f"[red]모르는 모델입니다.[/] {', '.join(MODELS)} 중에서 고르세요.")
        elif name == "key":
            if interactive and ask_key(c):
                self.agent = None
        else:
            c.print(f"[red]모르는 명령입니다: /{escape(name)}[/] /help를 입력해 보세요.")
        return True

    def welcome(self) -> None:
        key = "등록됨" if keystore.get_key() else "등록 필요"
        body = (
            f"[bold]{escape(self.dictionary['dataset'])}[/] {len(self.dictionary['tables'])}개 표 · 모델 {self.model} · 읽기 전용 · API 키 {key}\n"
            "우리말로 묻거나 SQL을 붙여 넣으세요.  /help 도움말 · /tables 표 목록 · /exit 끝내기"
        )
        self.console.print(Panel(body, title="[bold]새록 SQL[/]", border_style=ACCENT, title_align="left"))

    def repl(self) -> None:
        from prompt_toolkit import PromptSession
        from prompt_toolkit.history import FileHistory

        try:
            session = PromptSession(history=FileHistory(str(app_dir() / "input-history.txt")))
            read = lambda: session.prompt("> ")
        except Exception:
            # 터미널 창이 아닌 곳(파이프·일부 편집기 출력 창)에서는 일반 입력으로 받습니다.
            read = lambda: input("> ")
        self.welcome()
        while True:
            try:
                raw = read()
            except KeyboardInterrupt:
                continue
            except EOFError:
                break
            if not self.handle(raw):
                break
        self.console.print("[dim]새록 SQL을 닫습니다.[/]")


def _read_stdin() -> str:
    """Windows에서는 표준 입력 기본 인코딩이 cp949라 한글이 깨지므로 바이트로 읽어 UTF-8부터 시도합니다."""
    data = sys.stdin.buffer.read()
    for encoding in ("utf-8-sig", "cp949"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(prog="saerok-sql", description="새록 SQL: 우리말로 묻고 SQL로 답하는 터미널")
    parser.add_argument("-q", "--question", help="한 번만 묻고 끝내기")
    parser.add_argument("--explain", type=Path, help="SQL 파일을 풀이하고 끝내기")
    parser.add_argument("--model", choices=sorted(MODELS), help="모델(기본 sonnet)")
    parser.add_argument("--no-history", action="store_true", help="기록을 남기지 않기")
    tool = parser.add_argument_group("AI 없이 쓰기(Claude Code 스킬용)")
    tool.add_argument("--schema", action="store_true", help="데이터 사전 글 출력")
    tool.add_argument("--run", metavar="SQL", help="SQL을 안전 검사 후 실행해 JSON으로 출력. '-'면 표준 입력에서 읽음")
    tool.add_argument("--label", default="", help="--run 기록에 남길 원래 질문")
    tool.add_argument("--install-skill", action="store_true", help="Claude Code 스킬 설치(~/.claude/skills/saerok-sql)")
    args = parser.parse_args(argv)
    console = Console()
    if args.install_skill:
        from .tools import install_skill

        console.print(f"Claude Code 스킬을 설치했습니다: {install_skill()}")
        console.print("Claude Code를 다시 열고 /saerok-sql 뒤에 질문을 붙여 쓰세요.")
        return 0
    if args.schema or args.run:
        from .tools import dumps, run_json, schema_text

        db = Database()
        try:
            if args.schema:
                sys.stdout.write(schema_text(db))
                return 0
            sql = _read_stdin() if args.run == "-" else args.run
            result = run_json(db, sql, args.label, None if args.no_history else History())
            sys.stdout.write(dumps(result) + "\n")
            return 0 if result["status"] in ("ok", "review") else 1
        finally:
            db.close()
    try:
        app = App(console, MODELS[args.model] if args.model else DEFAULT_MODEL, keep_history=not args.no_history)
    except FileNotFoundError as e:
        console.print(f"[red]{escape(str(e))}[/]")
        return 2
    if args.question or args.explain:
        text = args.question or args.explain.read_text(encoding="utf-8-sig")
        app.handle(text, interactive=False)
        return 0 if app.last_status in ("ok", "review") else 1
    app.repl()
    return 0


if __name__ == "__main__":
    sys.exit(main())
