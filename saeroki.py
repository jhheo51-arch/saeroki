"""새록이의 콘텐츠 개인화 공통 기반.

외부 AI 서비스 없이도 취향 저장, 후보 정리, 추천, 자기 검토,
사용자 피드백, 실행 기록까지 한 흐름으로 확인할 수 있습니다.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


FEEDBACK_ACTIONS = {"saved", "known", "not_interested", "too_famous"}
TRACKING_QUERY_KEYS = {
    "fbclid",
    "gclid",
    "mc_cid",
    "mc_eid",
    "ref",
    "source",
    "utm_campaign",
    "utm_content",
    "utm_medium",
    "utm_source",
    "utm_term",
}


@dataclass(frozen=True)
class Candidate:
    id: str
    title: str
    url: str
    tags: list[str]
    source: str
    checked_at: str
    popularity: int | None = None
    author: str | None = None
    published_at: str | None = None


@dataclass
class Preference:
    interests: list[str]
    excluded: list[str] = field(default_factory=list)
    context: list[str] = field(default_factory=list)
    max_popularity: int | None = None


@dataclass
class Profile:
    name: str
    preference: Preference
    known_ids: list[str] = field(default_factory=list)
    feedback: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class Recommendation:
    candidate: Candidate
    score: int
    reasons: list[str]
    cautions: list[str]


@dataclass(frozen=True)
class ReviewResult:
    passed: bool
    notes: list[str]


@dataclass(frozen=True)
class DiscoveryRun:
    started_at: str
    plan: list[str]
    received_count: int
    prepared_count: int
    rejected: list[dict[str, object]]
    recommendations: list[Recommendation]
    review: ReviewResult


def canonical_url(url: str) -> str:
    """추적용 주소 조각을 걷어내 중복 비교용 주소를 만듭니다."""
    parts = urlsplit(url.strip())
    query = [
        (key, value)
        for key, value in parse_qsl(parts.query, keep_blank_values=True)
        if key.lower() not in TRACKING_QUERY_KEYS
    ]
    path = parts.path.rstrip("/") or "/"
    return urlunsplit(
        (
            parts.scheme.lower(),
            parts.netloc.lower(),
            path,
            urlencode(query),
            "",
        )
    )


def candidate_issues(candidate: Candidate) -> list[str]:
    """추천 후보가 최소한의 출처 정보를 갖췄는지 확인합니다."""
    issues: list[str] = []
    if not candidate.id.strip():
        issues.append("id가 없습니다")
    if not candidate.title.strip():
        issues.append("제목이 없습니다")
    if not candidate.source.strip():
        issues.append("출처가 없습니다")
    if not candidate.checked_at.strip():
        issues.append("출처 확인 시각이 없습니다")
    parts = urlsplit(candidate.url.strip())
    if parts.scheme not in {"http", "https"} or not parts.netloc:
        issues.append("웹 주소 형식이 올바르지 않습니다")
    return issues


def prepare_candidates(
    candidates: list[Candidate],
) -> tuple[list[Candidate], list[dict[str, object]]]:
    """잘못된 후보와 중복 후보를 분리합니다."""
    prepared: list[Candidate] = []
    rejected: list[dict[str, object]] = []
    seen_ids: set[str] = set()
    seen_urls: set[str] = set()

    for candidate in candidates:
        issues = candidate_issues(candidate)
        normalized_url = canonical_url(candidate.url)
        if candidate.id in seen_ids:
            issues.append("같은 id의 후보가 이미 있습니다")
        if normalized_url in seen_urls:
            issues.append("같은 웹 주소의 후보가 이미 있습니다")

        if issues:
            rejected.append({"id": candidate.id, "reasons": issues})
            continue

        prepared.append(candidate)
        seen_ids.add(candidate.id)
        seen_urls.add(normalized_url)

    return prepared, rejected


def recommend(
    candidates: list[Candidate],
    preference: Preference,
    known_ids: set[str] | None = None,
    limit: int = 5,
) -> list[Recommendation]:
    """취향과 현재 상황에 맞는 후보를 점수순으로 추천합니다."""
    if limit < 1:
        raise ValueError("limit은 1 이상이어야 합니다")

    known_ids = known_ids or set()
    interest_set = {value.casefold() for value in preference.interests}
    excluded_set = {value.casefold() for value in preference.excluded}
    context_set = {value.casefold() for value in preference.context}
    recommendations: list[Recommendation] = []

    for candidate in candidates:
        if candidate.id in known_ids:
            continue

        tags = {tag.casefold() for tag in candidate.tags}
        if tags & excluded_set:
            continue
        if (
            preference.max_popularity is not None
            and candidate.popularity is not None
            and candidate.popularity > preference.max_popularity
        ):
            continue

        interest_matches = sorted(tags & interest_set)
        context_matches = sorted(tags & context_set)
        score = len(interest_matches) * 2 + len(context_matches)
        if score == 0:
            continue

        reasons: list[str] = []
        cautions: list[str] = []
        if interest_matches:
            reasons.append(f"관심사와 일치: {', '.join(interest_matches)}")
        if context_matches:
            reasons.append(f"현재 상황과 일치: {', '.join(context_matches)}")
        if candidate.popularity is None:
            cautions.append("인지도 자료가 없어 덜 알려진 콘텐츠인지 확인이 필요합니다")

        recommendations.append(
            Recommendation(
                candidate=candidate,
                score=score,
                reasons=reasons,
                cautions=cautions,
            )
        )

    return sorted(
        recommendations,
        key=lambda item: (-item.score, item.candidate.title.casefold()),
    )[:limit]


def review_recommendations(
    recommendations: list[Recommendation],
    rejected: list[dict[str, object]],
) -> ReviewResult:
    """추천 결과에 출처와 이유가 빠지지 않았는지 다시 확인합니다."""
    notes: list[str] = []
    if not recommendations:
        notes.append("추천 결과가 없습니다. 관심사나 후보 자료를 확인해 주세요")
    for item in recommendations:
        if not item.reasons:
            notes.append(f"{item.candidate.id}: 추천 이유가 없습니다")
        if candidate_issues(item.candidate):
            notes.append(f"{item.candidate.id}: 출처 정보가 부족합니다")
    if rejected:
        notes.append(f"형식 오류 또는 중복 후보 {len(rejected)}개를 제외했습니다")
    return ReviewResult(
        passed=bool(recommendations)
        and all(not note.endswith("추천 이유가 없습니다") for note in notes),
        notes=notes,
    )


def run_discovery(
    candidates: list[Candidate],
    profile: Profile,
    limit: int = 5,
    started_at: str | None = None,
) -> DiscoveryRun:
    """계획, 후보 정리, 추천, 자기 검토를 차례로 실행합니다."""
    plan = [
        "후보의 필수 출처 정보를 확인합니다",
        "같은 id와 웹 주소를 중복 제거합니다",
        "사용자 취향과 현재 상황을 비교합니다",
        "추천 이유와 주의점을 만듭니다",
        "결과를 다시 검토합니다",
    ]
    prepared, rejected = prepare_candidates(candidates)
    known_ids = set(profile.known_ids)
    known_ids.update(
        candidate_id
        for candidate_id, action in profile.feedback.items()
        if action in {"known", "not_interested", "too_famous"}
    )
    recommendations = recommend(
        prepared,
        profile.preference,
        known_ids=known_ids,
        limit=limit,
    )
    review = review_recommendations(recommendations, rejected)
    return DiscoveryRun(
        started_at=started_at or datetime.now(timezone.utc).isoformat(),
        plan=plan,
        received_count=len(candidates),
        prepared_count=len(prepared),
        rejected=rejected,
        recommendations=recommendations,
        review=review,
    )


def apply_feedback(profile: Profile, candidate_id: str, action: str) -> None:
    """사용자의 선택을 다음 추천에 반영합니다."""
    if action not in FEEDBACK_ACTIONS:
        allowed = ", ".join(sorted(FEEDBACK_ACTIONS))
        raise ValueError(f"action은 다음 중 하나여야 합니다: {allowed}")
    profile.feedback[candidate_id] = action
    if action == "known" and candidate_id not in profile.known_ids:
        profile.known_ids.append(candidate_id)


def save_profile(profile: Profile, path: str | Path) -> None:
    """사용자 취향을 JSON 파일에 저장합니다."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(asdict(profile), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def load_profile(path: str | Path) -> Profile:
    """JSON 파일에서 사용자 취향을 불러옵니다."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    preference = Preference(**data["preference"])
    return Profile(
        name=data["name"],
        preference=preference,
        known_ids=data.get("known_ids", []),
        feedback=data.get("feedback", {}),
    )


def load_candidates(path: str | Path) -> list[Candidate]:
    """JSON 파일에서 추천 후보를 불러옵니다."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("후보 파일의 최상위 값은 목록이어야 합니다")
    return [Candidate(**item) for item in data]


def run_to_dict(run: DiscoveryRun) -> dict[str, object]:
    """실행 결과를 화면 표시와 기록에 쓰기 쉬운 형태로 바꿉니다."""
    return asdict(run)


def append_run_log(run: DiscoveryRun, path: str | Path) -> None:
    """한 번의 실행 결과를 줄 단위 JSON 기록에 덧붙입니다."""
    log_path = Path(path)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(run_to_dict(run), ensure_ascii=False) + "\n")
