"""면접 화면의 Claude 호출을 API 키 대신 내 Claude 구독으로 돌립니다.

화면은 Messages API 형식(system·messages)으로 보내고, 여기서 `claude -p`(Claude Code)로 바꿔 돌린 뒤
화면이 읽는 Messages API 응답 모양(text·usage)으로 되돌립니다.

- ANTHROPIC_API_KEY를 빼고 실행해 API 크레딧이 아니라 Claude Code에 로그인한 구독 사용량을 씁니다.
- 빈 임시 폴더에서, 설정·MCP·스킬을 읽지 않고, 도구를 하나도 주지 않습니다(서류 본문은 메시지에 붙어 옵니다).
- --no-session-persistence로 자기소개서가 Claude Code 대화 기록(~/.claude)에 남지 않게 합니다."""

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

TIMEOUT = 600


def cli() -> str | None:
    """설치된 claude 명령 경로. 없으면 None."""
    return shutil.which("claude")


def _prompt(body: dict) -> str:
    messages = body.get("messages") or []
    if not messages or messages[0].get("role") != "user":
        raise ValueError("user 메시지가 없습니다.")
    content = messages[0].get("content")
    if isinstance(content, list):
        content = "".join(c.get("text", "") for c in content if isinstance(c, dict))
    if not isinstance(content, str) or not content.strip():
        raise ValueError("user 메시지가 비었습니다.")
    return content


def args_for(body: dict, system_file: Path) -> list[str]:
    """claude -p 인자. 도구 없이 한 번만 답합니다."""
    args = ["-p", "--output-format", "stream-json", "--verbose", "--no-session-persistence",
            "--setting-sources", "", "--strict-mcp-config", "--disable-slash-commands",
            "--system-prompt-file", str(system_file), "--tools", "", "--max-turns", "1"]
    if body.get("model"):
        args += ["--model", str(body["model"])]
    return args


def _system(body: dict) -> str:
    system = body.get("system") or ""
    if isinstance(system, list):
        system = "\n".join(s.get("text", "") for s in system if isinstance(s, dict))
    return system


def convert(lines) -> dict:
    """claude -p stream-json 줄들을 Messages API 응답 모양으로 바꿉니다."""
    content, result = [], None
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        kind = event.get("type")
        message = event.get("message") or {}
        blocks = message.get("content") if isinstance(message.get("content"), list) else []
        if kind == "assistant":
            for block in blocks:
                if block.get("type") == "text" and block.get("text"):
                    content.append({"type": "text", "text": block["text"]})
        elif kind == "result":
            result = event
    if result is None:
        raise RuntimeError("Claude Code가 결과 없이 끝났습니다.")
    if result.get("is_error"):
        raise RuntimeError(str(result.get("result") or result.get("subtype") or "Claude Code 오류"))
    usage = result.get("usage") or {}
    return {
        "type": "message", "role": "assistant", "content": content, "stop_reason": "end_turn",
        "usage": {
            "input_tokens": sum(int(usage.get(k) or 0) for k in
                                ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")),
            "output_tokens": int(usage.get("output_tokens") or 0),
        },
    }


def call(body: dict, command: str | None = None) -> dict:
    """화면의 Messages API 요청 하나를 claude -p로 돌려 응답을 돌려줍니다."""
    command = command or cli()
    if not command:
        raise RuntimeError("claude 명령을 찾지 못했습니다. Claude Code를 설치하고 로그인해 주세요.")
    prompt = _prompt(body)
    env = {k: v for k, v in os.environ.items() if k not in ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN")}
    with tempfile.TemporaryDirectory(prefix="saerok-interview-") as work:
        system_file = Path(work) / "system.md"
        system_file.write_text(_system(body), encoding="utf-8")
        try:
            done = subprocess.run([command, *args_for(body, system_file)], input=prompt.encode("utf-8"),
                                  capture_output=True, cwd=work, env=env, timeout=TIMEOUT)
        except subprocess.TimeoutExpired:
            raise RuntimeError(f"Claude Code가 {TIMEOUT // 60}분 안에 끝나지 않았습니다.")
    out = done.stdout.decode("utf-8", errors="replace")
    try:
        return convert(out.splitlines())
    except RuntimeError as e:
        if done.returncode and not out.strip():
            err = done.stderr.decode("utf-8", errors="replace").strip().splitlines()
            raise RuntimeError(f"Claude Code 실행 실패: {err[-1] if err else done.returncode}")
        if "login" in str(e).lower() or "auth" in str(e).lower():
            raise RuntimeError(f"Claude Code 로그인이 필요합니다(터미널에서 claude 실행 후 /login): {e}")
        raise
