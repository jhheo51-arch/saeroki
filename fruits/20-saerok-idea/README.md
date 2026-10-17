# 🌸 20 새록 심사단 (아이디어 검증)

서비스 아이디어 한 줄을 심사위원 3명이 평가하고, 핵심 가정을 공개 근거로 직접 검증해 `진행·조건부·보류` 판정과 다듬은 방향 2~3개를 냅니다. 기획서는 쓰지 않고 [4번 새록 검토관](../04-prd-assistant)에 넘깁니다.

- 상태: 🌸 꽃(만드는 중, 2026-10-17 첫 구현)
- 설계: [PRD v2.0-idea](../../docs/PRD-v2.0-idea.md)(검토관 PRD 버전을 따름)
- 공통 원칙: [AGENT-SPEC.md](../../AGENT-SPEC.md)
- 참고: [AI-ANTENNA 창업 아이디어 가이드](https://imyoung-man.github.io/AI-ANTENNA/aitip-founder/guide.html)의 '심사위원 서브에이전트 + 가상 패널' 방식에, 가정 검증·출처 표시·결정적 판정·방향 제안을 더했습니다.

## 아이디어는 내 PC에만

아이디어와 심사 기록은 이 저장소에 두지 않고 내 PC 기록 폴더(기본 `~/.saerok/idea/`, `SAEROK_IDEA_HOME`으로 바꿈)에만 저장합니다.

- 기록 폴더가 git 저장소 안이면 기록을 만들지 않고 멈춥니다.
- 웹 검색어에는 아이디어 원문을 넣지 않고 일반 낱말만 쓰며, 보내기 전에 목록을 보여 주고 확인받습니다.
- 분석은 Claude가 하고 검색어는 검색 서비스로 나가므로 완전한 비공개는 아닙니다.
- 이 폴더의 [`examples/`](examples)는 모두 지어낸 가상 아이디어입니다.

## 설치

Claude Code 대화창에서:

```text
/plugin marketplace add jhheo51-arch/saeroki
/plugin install saerok-idea@saeroki
```

Python 3.10 이상이 필요합니다.

## 쓰는 순서

| 단계 | 명령 | 하는 일 |
|---|---|---|
| 심사 | `/saerok-idea:judge 동네 1인 카페 사장님에게 재고 알림` | 4칸(무엇을·누구에게·돈·왜 지금) 확인, 심사위원 3명, 가정 3개 검증, 경쟁 조사, 패널, 손익분기를 거쳐 `verdict.md`를 만듭니다 |
| 방향 다시 심사 | `/saerok-idea:judge --from <verdict.md> --direction 2` | 다듬은 방향 하나를 같은 아이디어 폴더에 새 기록으로 심사합니다 |
| 한 단계만 다시 | `/saerok-idea:judge --step assumptions <기록 폴더>` | 그 단계만 바꿔 쓰고, 옛 값은 `replaced`에 남깁니다 |
| 기록 비교 | `/saerok-idea:compare <아이디어 폴더>` | 날짜·방향별 판정, 심사위원 점수, 가정 결과를 표로 봅니다 |
| 기획으로 넘기기 | `/saerok-prd:design --from <verdict.md>` | `진행`·`조건부`일 때 4번 검토관 설계 스무고개를 심사 결과에서 시작합니다 |

패널은 기본 20명, `--full`이면 100명입니다.

## 판정 규칙

판정은 AI가 아니라 [`saerok_idea/verdict.py`](saerok_idea/verdict.py)가 정합니다.

1. 무엇을·누구에게가 `미정`이거나 가정 3개가 모두 `확인 못 함`이면 `판단 보류(정보 부족)`
2. 심사위원 표: 보류 2표 이상이면 보류, 진행 2표 이상이고 보류 0표면 진행, 나머지는 조건부
3. 문제 가정이 `반박`이면 보류, 다른 가정이 `반박`이면 진행을 조건부로 낮춤

가상 패널과 손익분기는 판정에 쓰지 않습니다. 패널은 AI 시뮬레이션이고, 손익분기는 사용자가 준 값이나 링크가 있는 값으로만 계산합니다(AI가 추정한 가격은 받지 않음).

## 두 층

- **AI 계층**: 심사위원 3명과 가상 패널([`agents/`](agents), Sonnet)이 JSON으로 답하고, 가정 검증·경쟁 조사·방향 제안은 진행자(세션 모델)가 웹 검색으로 합니다. 가정마다 반박 쪽 검색어를 먼저 씁니다.
- **결정적 계층**([`saerok_idea/`](saerok_idea), AI 없음): 형식 검사(근거마다 링크·확인 날짜), 판정, 손익분기 계산, `verdict.md` 렌더링, 기록 비교.

명령만 따로 쓸 수도 있습니다.

```bash
bin/saerok-idea breakeven --price 9900 --unit-cost 1500 --fixed-cost 300000
bin/saerok-idea compare ~/.saerok/idea/<아이디어 폴더>
```

## PRD 버전

심사단 PRD는 검토관 PRD의 짝 문서라 버전을 따라갑니다. 검토관 PRD가 새 버전으로 올라오면 [`scripts/sync_idea_prd.py`](../../scripts/sync_idea_prd.py)가 이름·제목·머리말·링크를 맞추고(본문은 그대로, '내용 다시 보기 전' 표시), Actions가 이를 커밋합니다. `python -m unittest`가 어긋남을 잡습니다.

## 검사

```bash
python -m unittest test_saerok_idea
```
