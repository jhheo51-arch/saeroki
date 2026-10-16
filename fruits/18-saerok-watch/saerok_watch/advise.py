"""측정값과 현재 설정을 보고 절약 제안을 만듭니다. 여기서는 아무것도 바꾸지 않습니다."""

import re
import time
from pathlib import Path

from .apply import files, hook_installed, plugin_active
from .paths import claude_home
from .scan import simulate_cap, totals
from .store import read_json

RECENT_DAYS = 14


def _man(n: int) -> str:
    """토큰 수를 '21.3만'처럼 짧게."""
    if n >= 100_000_000:
        return f"{n / 100_000_000:.1f}억"
    if n >= 10_000:
        return f"{n / 10_000:.1f}만"
    return f"{n:,}"


def environment() -> dict:
    home = claude_home()
    settings = read_json(files()["settings"], {}) or {}
    cj = read_json(files()["claude_json"], {}) or {}
    synced = []
    for manifest in (home / "plugins" / "synced").glob("*/*/.claude-plugin/plugin.json"):
        meta = read_json(manifest, {}) or {}
        root = manifest.parent.parent
        synced.append({"name": meta.get("name") or root.name, "skills": len(list(root.glob("skills/*/SKILL.md")))})
    installed = read_json(home / "plugins" / "installed_plugins.json", {}) or {}
    disabled = {}
    for project, conf in (cj.get("projects") or {}).items():
        for server in conf.get("disabledMcpServers") or []:
            disabled.setdefault(server, []).append(project)
    return {
        "auto_compact_window": settings.get("autoCompactWindow"),
        "hook_installed": hook_installed(settings) or plugin_active(settings),
        "enabled_plugins": settings.get("enabledPlugins") or {},
        "installed_plugins": sorted((installed.get("plugins") or {}).keys()),
        "synced_plugins": sorted(synced, key=lambda p: p["name"]),
        "user_mcp_servers": sorted((cj.get("mcpServers") or {}).keys()),
        "mcp_disabled_in": disabled,
        "project_count": len(cj.get("projects") or {}),
    }


def required_reading(cwds: list[str]) -> list[dict]:
    """세션을 연 폴더와 그 바로 아래 폴더의 CLAUDE.md가 먼저 읽으라고 하는 문서 크기."""
    found = {}
    for cwd in cwds:
        base = Path(cwd)
        candidates = [base / "CLAUDE.md"] + list(base.glob("*/CLAUDE.md"))
        for md in candidates:
            if md in found or not md.is_file():
                continue
            text = md.read_text(encoding="utf-8", errors="replace")
            docs = []
            for ref in dict.fromkeys(re.findall(r"`([^`\s]+\.md)`", text)):
                target = md.parent / ref
                if target.is_file() and target.name != "CLAUDE.md":
                    docs.append({"path": ref, "bytes": target.stat().st_size})
            total = md.stat().st_size + sum(d["bytes"] for d in docs)
            found[md] = {"claude_md": str(md), "folder": md.parent.name, "docs": docs, "bytes": total}
    return sorted(found.values(), key=lambda x: -x["bytes"])


def _recent(sessions: list[dict]) -> list[dict]:
    cutoff = time.time() - RECENT_DAYS * 86400
    return [s for s in sessions if s.get("mtime", 0) >= cutoff]


def suggestions(sessions: list[dict], config: dict) -> list[dict]:
    env = environment()
    t = totals(sessions)
    out = []
    total = t["processed"] or 1

    # 1. 긴 세션: 30만 넘는 응답 비율
    over300 = (t["buckets"][2] + t["buckets"][3]) / total
    window = env["auto_compact_window"]
    if over300 >= 0.2:
        cap = 200_000
        ratio = simulate_cap(sessions, cap)
        already = bool(window and window <= 300_000)
        out.append({
            "id": "long-sessions", "size": "큼",
            "title": "긴 세션이 컨텍스트를 크게 키움",
            "measured": f"처리량 {_man(t['processed'])} 토큰 중 {over300:.0%}가 컨텍스트 30만 이상인 응답에서 나옴",
            "estimate": f"20만에서 압축하면 처리량이 지금의 약 {ratio:.0%}(구간 근사, 압축 비용 제외)",
            "how": "자동 압축 창을 낮추고, 작업이 바뀌면 새 세션이나 /clear를 씁니다.",
            "loss": "압축 뒤에는 앞부분의 세세한 맥락이 요약으로 바뀝니다.",
            "action": None if already else f"autocompact:{cap}",
            "action_label": "자동 압축 창 200K로",
            "status": f"지금 설정: {window:,}" if window else "지금 설정: 없음(1M 창의 97%에서 압축)",
        })

    # 2. 실시간 경고 훅
    if not env["hook_installed"]:
        out.append({
            "id": "hook", "size": "큼",
            "title": "작업 중 컨텍스트 크기가 보이지 않음",
            "measured": f"주의 {_man(config['caution'])} · 경고 {_man(config['warn'])} 기준이 아직 작동하지 않음",
            "estimate": "넘는 순간 대화에 한 줄로 알려 세션을 끊을 때를 놓치지 않게 함",
            "how": "Claude Code Stop 훅으로 응답이 끝날 때마다 크기를 잽니다.",
            "loss": "응답마다 기록 파일 끝부분을 읽는 짧은 작업이 더해집니다.",
            "action": "hook_install", "action_label": "파수꾼 훅 설치",
        })

    # 3. 스크린샷
    recent = _recent(sessions)
    heavy = [s for s in recent if s["images"] >= 20]
    if heavy:
        imgs = sum(s["images"] for s in heavy)
        out.append({
            "id": "images", "size": "큼",
            "title": "스크린샷이 세션 끝까지 따라다님",
            "measured": f"최근 {RECENT_DAYS}일 세션 {len(heavy)}개에서 스크린샷 {imgs}장",
            "estimate": f"한 장 1천~1.6천 토큰이면 약 {_man(imgs * 1300)} 토큰이 매 응답 다시 읽힘",
            "how": "확인은 read_page·get_page_text로 먼저, 스크린샷은 마지막 증거로만, scale 0.5를 씁니다.",
            "loss": "화면을 눈으로 확인하는 횟수가 줄어듭니다.",
            "action": None, "manual": "Claude에게 '스크린샷은 마지막에 한 번만'이라고 요청하세요.",
        })

    # 4. 큰 도구 출력
    chars = {}
    for s in recent:
        for name, n in s["tool_chars"].items():
            chars[name] = chars.get(name, 0) + n
    top = sorted(chars.items(), key=lambda kv: -kv[1])[:3]
    if top and top[0][1] >= 300_000:
        out.append({
            "id": "tool-output", "size": "중간",
            "title": "큰 도구 출력이 대화에 쌓임",
            "measured": "최근 출력 글자 수 상위: " + ", ".join(f"{n} {_man(c)}자" for n, c in top),
            "estimate": "출력은 세션이 끝날 때까지 매 응답 다시 읽힙니다.",
            "how": "필요한 줄만 읽고, 로그·탐색처럼 긴 일은 서브에이전트에 맡겨 요약만 받습니다.",
            "loss": "서브에이전트는 자기 토큰을 따로 씁니다.",
            "action": None, "manual": "Claude에게 '큰 출력은 서브에이전트로'라고 요청하세요.",
        })

    # 5. 사용자 MCP 서버
    used = {}
    for s in recent:
        for server, n in s["mcp_used"].items():
            used[server] = used.get(server, 0) + n
    for server in env["user_mcp_servers"]:
        off_everywhere = len(env["mcp_disabled_in"].get(server, [])) >= env["project_count"]
        if used.get(server) or off_everywhere:
            continue
        out.append({
            "id": f"mcp-{server}", "size": "중간",
            "title": f"안 쓰는 MCP 서버 {server}가 매 세션 실림",
            "measured": f"최근 {RECENT_DAYS}일 호출 0번",
            "estimate": "서버 안내문과 지연 도구 이름이 매 세션 실림(도구가 많을수록 큼)",
            "how": "평소에는 끄고, 필요할 때 /mcp에서 켭니다.",
            "loss": "그 서버가 필요할 때 다시 켜야 합니다.",
            "action": f"mcp_off:{server}", "action_label": f"{server} 끄기",
        })

    # 6. 직접 설치한 플러그인
    skill_uses = {}
    for s in recent:
        for skill, n in s["skills_used"].items():
            prefix = skill.split(":")[0]
            skill_uses[prefix] = skill_uses.get(prefix, 0) + n
    for plugin, on in env["enabled_plugins"].items():
        short = plugin.split("@")[0]
        if on is True and short != "saerok-watch" and not skill_uses.get(short):
            out.append({
                "id": f"plugin-{short}", "size": "작음",
                "title": f"플러그인 {short}의 스킬을 최근 쓰지 않음",
                "measured": f"최근 {RECENT_DAYS}일 {short} 스킬 호출 0번",
                "estimate": "스킬 목록과 훅이 매 세션 실림",
                "how": "끄고, 필요할 때 다시 켭니다.",
                "loss": "그 플러그인의 스킬·훅 전부.",
                "action": f"plugin_off:{plugin}", "action_label": f"{short} 끄기",
            })

    # 7. 계정 동기화 플러그인
    idle = [p for p in env["synced_plugins"] if p["skills"] and not skill_uses.get(p["name"])]
    if idle:
        n = sum(p["skills"] for p in idle)
        out.append({
            "id": "synced-plugins", "size": "중간",
            "title": "claude.ai 계정에서 동기화된 플러그인 스킬을 쓰지 않음",
            "measured": f"최근 {RECENT_DAYS}일 호출 0번: " + ", ".join(f"{p['name']}({p['skills']})" for p in idle) + f", 스킬 {n}개",
            "estimate": "스킬 목록이 길어지고 인증 안 된 커넥터 안내가 매 세션 실림",
            "how": "앱이나 터미널의 /plugin 화면에서 끕니다.",
            "loss": "그 플러그인의 스킬과 커넥터.",
            "action": None,
            "manual": "동기화 플러그인을 설정 파일로 끄는 방법은 확인하지 못해 자동 적용하지 않습니다.",
        })

    # 8. CLAUDE.md 필독 문서
    cwds = sorted({s["cwd"] for s in recent if s.get("cwd")})
    for item in required_reading(cwds):
        if item["bytes"] < 30_000:
            continue
        out.append({
            "id": f"reading-{item['folder']}", "size": "중간",
            "title": f"{item['folder']}의 CLAUDE.md 필독 문서가 큼",
            "measured": f"CLAUDE.md와 필독 문서 {len(item['docs'])}개 합계 {item['bytes'] / 1000:.0f}KB",
            "estimate": "한국어 문서는 대략 1KB에 300~500토큰. 읽은 뒤 세션 끝까지 매 응답 다시 읽힘",
            "how": "최신 문서만 필수로 두고 옛 버전은 '필요할 때만'으로 바꿉니다.",
            "loss": "옛 문서와 비교할 때 한 번 더 읽어야 합니다.",
            "action": None,
            "manual": "내용 판단이 필요해 자동으로 고치지 않습니다. 문서: " + ", ".join(
                f"{d['path']} {d['bytes'] / 1000:.0f}KB" for d in sorted(item["docs"], key=lambda d: -d["bytes"])),
        })

    rank = {"큼": 0, "중간": 1, "작음": 2}
    out.sort(key=lambda x: rank[x["size"]])
    return out
