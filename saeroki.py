"""새록이의 첫 번째 모델 독립 추천 흐름."""

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class Candidate:
    id: str
    title: str
    url: str
    tags: tuple[str, ...]
    source: str
    checked_at: str
    popularity: float | None = None


@dataclass(frozen=True)
class Preference:
    interests: frozenset[str]
    excluded: frozenset[str] = frozenset()
    context: frozenset[str] = frozenset()
    max_popularity: float | None = None


@dataclass(frozen=True)
class Recommendation:
    candidate: Candidate
    score: int
    reason: str
    discovery_note: str


def recommend(
    preference: Preference,
    candidates: Iterable[Candidate],
    known_ids: frozenset[str] = frozenset(),
    limit: int = 3,
) -> list[Recommendation]:
    """알려진 항목과 제외 조건을 거른 뒤 근거가 있는 후보만 반환합니다."""
    if limit < 1:
        raise ValueError("limit은 1 이상이어야 합니다.")

    results: list[Recommendation] = []
    for candidate in candidates:
        tags = frozenset(candidate.tags)
        if candidate.id in known_ids or tags & preference.excluded:
            continue
        if (
            preference.max_popularity is not None
            and candidate.popularity is not None
            and candidate.popularity > preference.max_popularity
        ):
            continue

        interest_matches = sorted(tags & preference.interests)
        context_matches = sorted(tags & preference.context)
        score = len(interest_matches) * 2 + len(context_matches)
        if score == 0:
            continue

        reasons = []
        if interest_matches:
            reasons.append(f"관심사 일치: {', '.join(interest_matches)}")
        if context_matches:
            reasons.append(f"현재 상황 일치: {', '.join(context_matches)}")

        if candidate.popularity is None:
            discovery_note = "인기도 자료가 없어 덜 알려졌다고 단정하지 않음"
        else:
            discovery_note = f"확인된 인기도 값: {candidate.popularity:g}"

        results.append(
            Recommendation(candidate, score, "; ".join(reasons), discovery_note)
        )

    return sorted(results, key=lambda item: (-item.score, item.candidate.title))[:limit]
