# 🌸 20 새록 심사단 (아이디어 검증)

서비스 아이디어 한 줄을 심사위원 3명이 평가하고, 핵심 가정을 공개 근거로 직접 검증해 `진행·조건부·보류` 판정과 다듬은 방향 2~3개를 냅니다. 기획서는 쓰지 않고 [4번 새록 검토관](../04-prd-assistant)에 넘깁니다.

- 상태: 🌸 꽃(만드는 중, 2026-10-17 첫 구현)
- 설계: [PRD v2.0-idea](../../docs/PRD-v2.0-idea.md)(검토관 PRD 버전을 따름)
- 공통 원칙: [AGENT-SPEC.md](../../AGENT-SPEC.md)
- 참고: [AI-ANTENNA 창업 아이디어 가이드](https://imyoung-man.github.io/AI-ANTENNA/aitip-founder/guide.html)의 '심사위원 서브에이전트 + 가상 패널' 방식에, 가정 검증·출처 표시·결정적 판정·방향 제안을 더했습니다.

## 바로 심사하기

| 어디서 | 여는 법 | 키·기록 |
|---|---|---|
| 웹 | **[심사 화면 열기](https://jhheo51-arch.github.io/saeroki/idea/)** | 내 Claude API 키를 화면에 넣으면 브라우저가 Anthropic에 바로 연결합니다. 키와 기록은 그 브라우저에만 남고, `verdict.md`·`result.json`으로 내려받습니다 |
| 터미널 | `saerok-idea` | 같은 화면이 내 PC(127.0.0.1)에서 열립니다. API 키 없이 Claude Code에 로그인한 내 Claude 구독 사용량으로 돌고, 기록은 `~/.saerok/idea/`에 남습니다. API 키로 돌리려면 `saerok-idea --api`(키는 Windows 자격 증명 관리자) |
| Claude Code | `/saerok-idea:judge <아이디어 한 줄>` | 아래 '쓰는 순서' |

터미널 명령은 한 번만 설치하면 됩니다.

```bash
pip install -e "fruits/20-saerok-idea[keyring]"
saerok-idea
```

구독으로 돌릴 때는 화면이 보낸 요청을 `claude -p`(Claude Code)로 바꿔 실행합니다. 환경에서 API 키를 빼고, 빈 임시 폴더에서 웹 검색 말고는 도구를 주지 않으며, 아이디어는 명령줄이 아니라 표준 입력으로 넘기고 `--no-session-persistence`로 Claude Code 대화 기록에 남기지 않습니다. Claude Code가 없거나 로그인하지 않았으면 화면의 설정에서 API 키 방식으로 바꿀 수 있습니다.

두 화면 모두 판정·형식 검사·`verdict.md`는 Python과 똑같이 옮긴 [`web/idea-core.js`](web/idea-core.js)가 내고, AI가 적은 근거 링크 중 실제 검색 결과에 나온 것만 남깁니다. 공용 PC에서는 웹 화면에 키를 넣지 마세요.

## 아이디어는 내 PC에만

아이디어와 심사 기록은 이 저장소에 두지 않고 내 PC 기록 폴더(기본 `~/.saerok/idea/`, `SAEROK_IDEA_HOME`으로 바꿈)에만 저장합니다. 웹 화면은 그 브라우저 저장소에만 둡니다.

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
