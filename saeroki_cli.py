"""새록이 콘텐츠 개인화 흐름을 확인하는 명령줄 도구."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict

from saeroki import (
    Profile,
    Preference,
    append_run_log,
    apply_feedback,
    load_candidates,
    load_profile,
    run_discovery,
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

    feedback = commands.add_parser("feedback", help="추천에 반응 남기기")
    feedback.add_argument("--profile", required=True)
    feedback.add_argument("--candidate", required=True)
    feedback.add_argument(
        "--action",
        required=True,
        choices=["saved", "known", "not_interested", "too_famous"],
    )
    return parser


def main() -> None:
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
