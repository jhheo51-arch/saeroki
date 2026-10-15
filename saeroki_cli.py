"""새록이 콘텐츠 개인화 흐름을 확인하는 명령줄 도구."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from saeroki import (
    Profile,
    Preference,
    append_run_log,
    apply_feedback,
    load_candidates,
    load_profile,
    run_discovery,
    scheduled_recommend,
    save_profile,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="새록이 콘텐츠 개인화 실험")
    commands = parser.add_subparsers(dest="command", required=True)

    init = commands.add_parser("init-profile", help="취향 파일 만들기")
    init.add_argument("--output", required=True)
    init.add_argument("--name", default="나")
    init.add_argument("--interest", action="append", required=True)
    init.add_argument("--exclude", action="append", default=[])
    init.add_argument("--context", action="append", default=[])
    init.add_argument("--max-popularity", type=int)

    recommend = commands.add_parser("recommend", help="후보 추천하기")
    recommend.add_argument("--profile", required=True)
    recommend.add_argument("--candidates", required=True)
    recommend.add_argument("--limit", type=int, default=5)
    recommend.add_argument("--log")

    scheduled = commands.add_parser("scheduled-recommend", help="시간대별 후보 추천하기")
    scheduled.add_argument("--profile", required=True)
    scheduled.add_argument("--candidates", required=True)
    scheduled.add_argument("--at", help="ISO 시간, 생략하면 현재 시각")
    scheduled.add_argument("--weather-condition", help="아침 음악에 사용할 서울 날씨")
    scheduled.add_argument("--live-weather", action="store_true", help="서울 현재 날씨 조회")

    feedback = commands.add_parser("feedback", help="추천에 반응 남기기")
    feedback.add_argument("--profile", required=True)
    feedback.add_argument("--candidate", required=True)
    feedback.add_argument(
        "--action",
        required=True,
        choices=["saved", "known", "not_interested", "too_famous"],
    )

    collect = commands.add_parser("collect", help="확인된 공개 출처의 메타데이터 수집")
    collect.add_argument("--sources", required=True)
    collect.add_argument("--output", required=True)
    return parser


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    args = build_parser().parse_args()

    if args.command == "init-profile":
        profile = Profile(
            name=args.name,
            preference=Preference(
                interests=args.interest,
                excluded=args.exclude,
                context=args.context,
                max_popularity=args.max_popularity,
            ),
        )
        save_profile(profile, args.output)
        print(f"취향 파일을 만들었습니다: {args.output}")
        return

    if args.command == "feedback":
        profile = load_profile(args.profile)
        apply_feedback(profile, args.candidate, args.action)
        save_profile(profile, args.profile)
        print(f"피드백을 저장했습니다: {args.candidate} -> {args.action}")
        return

    if args.command == "collect":
        from source_collector import collect_confirmed_sources, load_source_records

        records = load_source_records(args.sources)
        candidates, errors = collect_confirmed_sources(records)
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(
            json.dumps([asdict(item) for item in candidates], ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(json.dumps({
            "collected": len(candidates),
            "errors": errors,
            "output": args.output,
        }, ensure_ascii=False, indent=2))
        return

    if args.command == "scheduled-recommend":
        profile = load_profile(args.profile)
        candidates = load_candidates(args.candidates)
        current = datetime.fromisoformat(args.at) if args.at else datetime.now(timezone.utc)
        weather_condition = args.weather_condition
        if args.live_weather:
            from weather import fetch_seoul_weather

            weather_condition = fetch_seoul_weather().condition
        run = scheduled_recommend(candidates, profile, current, weather_condition)
        print(json.dumps({
            "mode": run.mode,
            "slots": [asdict(slot) for slot in run.slots],
            "recommendations": {
                content_type: [
                    {
                        "id": item.candidate.id,
                        "title": item.candidate.title,
                        "url": item.candidate.url,
                        "reasons": item.reasons,
                        "cautions": item.cautions,
                    }
                    for item in recommendations
                ]
                for content_type, recommendations in run.recommendations.items()
            },
        }, ensure_ascii=False, indent=2))
        return

    profile = load_profile(args.profile)
    candidates = load_candidates(args.candidates)
    run = run_discovery(candidates, profile, limit=args.limit)
    if args.log:
        append_run_log(run, args.log)

    output = {
        "plan": run.plan,
        "recommendations": [
            {
                "id": item.candidate.id,
                "title": item.candidate.title,
                "url": item.candidate.url,
                "source": item.candidate.source,
                "score": item.score,
                "reasons": item.reasons,
                "cautions": item.cautions,
            }
            for item in run.recommendations
        ],
        "review": asdict(run.review),
        "excluded_count": len(run.rejected),
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
