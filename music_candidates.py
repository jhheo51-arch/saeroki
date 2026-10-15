"""API 없이 관리하는 수동 YouTube Music 후보 목록."""

from __future__ import annotations

from pathlib import Path
from urllib.parse import urlsplit

from saeroki import Candidate, load_candidates


def validate_music_candidate(candidate: Candidate) -> list[str]:
    issues: list[str] = []
    if candidate.content_type != "music":
        issues.append("content_type이 music이 아닙니다")
    host = urlsplit(candidate.url).netloc.casefold()
    if host not in {"music.youtube.com", "www.youtube.com", "youtube.com"}:
        issues.append("YouTube 또는 YouTube Music 주소가 아닙니다")
    return issues


def load_music_candidates(path: str | Path) -> list[Candidate]:
    candidates = load_candidates(path)
    invalid = [
        {"id": candidate.id, "reasons": validate_music_candidate(candidate)}
        for candidate in candidates
        if validate_music_candidate(candidate)
    ]
    if invalid:
        raise ValueError(f"음악 후보 형식이 올바르지 않습니다: {invalid}")
    return candidates
