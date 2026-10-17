# 🌸 19 새록 면접관 (모의 면접)

면접관 5명(압박·인사·실무·임원·숫자 검증)이 내 자기소개서·이력서·채용 공고를 각자 고정된 기준으로 심사하고, 꼬리 질문이 붙는 실전 연습과 회차별 점수 비교를 하는 모의 면접 에이전트입니다. 질문마다 어느 문장을 보고 물었는지 원문과 줄 번호를 달고, 합격 가능성은 예측하지 않습니다.

- 상태: 🌸 꽃(만드는 중, 2026-10-17 첫 구현)
- 설계: [PRD v2.1](../../docs/PRD-v2.1.md)
- 공통 원칙: [AGENT-SPEC.md](../../AGENT-SPEC.md)
- 사용 안내: **[새록 면접관 5명에게 모의 면접 보는 법](https://jhheo51-arch.github.io/saeroki/interview/guide.html)** (한 장짜리 화면) · [GUIDE.md](GUIDE.md) (파일 이름 규칙·결과 폴더까지)
- 바탕: [AI-ANTENNA 면접 가이드](https://imyoung-man.github.io/AI-ANTENNA/aitip-interview/guide.html)의 '면접관 서브에이전트 + 판정.md + 실전 연습' 방식을 새록이 방식(면접관 5명·고정 기준표·근거 줄 확인·회차 비교)으로 다시 만들었습니다.

## 바로 면접 보기

| 어디서 | 여는 법 | 키·기록 |
|---|---|---|
| 웹 | **[면접 화면 열기](https://jhheo51-arch.github.io/saeroki/interview/)** | 내 Claude API 키를 화면에 넣으면 브라우저가 Anthropic에 바로 연결합니다. 키와 기록은 그 브라우저에만 남고, `verdict.md`·`practice.md`로 내려받습니다 |
| 터미널 | `saerok-interview` | 같은 화면이 내 PC(127.0.0.1)에서 열립니다. API 키 없이 Claude Code에 로그인한 내 Claude 구독 사용량으로 돌고, 기록은 면접 폴더(`~/.saerok/interview/`)에 남습니다. 서류 폴더에서 불러오기도 됩니다. API 키로 돌리려면 `saerok-interview --api`(키는 Windows 자격 증명 관리자) |
| Claude Code | `/saerok-interview:panel --company 골목장터` | 아래 '빠른 시작' |

터미널 명령은 한 번만 설치하면 됩니다.

```bash
pip install -e "fruits/19-saerok-interview[keyring]"
saerok-interview
```

화면에는 탭이 세 개입니다. **새 면접**에서 서류를 넣으면 면접관 5명이 동시에 심사하고, **실전 연습**에서 꼬리 질문과 채점을 받고, **기록·비교**에서 회차 변화와 실제 면접 적중률을 봅니다.

구독으로 돌릴 때는 화면이 보낸 요청을 `claude -p`(Claude Code)로 바꿔 실행합니다. 환경에서 API 키를 빼고, 빈 임시 폴더에서 도구를 하나도 주지 않으며, 서류는 명령줄이 아니라 표준 입력으로 넘기고 `--no-session-persistence`로 Claude Code 대화 기록에 남기지 않습니다. Claude Code가 없거나 로그인하지 않았으면 화면의 '키·설정'에서 API 키 방식으로 바꿀 수 있습니다.

두 화면 모두 기준표 검사·근거 원문 확인·`verdict.md`·`practice.md`·회차 비교는 Python과 똑같이 옮긴 [`web/interview-core.js`](web/interview-core.js)가 냅니다(검사가 두 결과를 맞대어 봅니다). 공용 PC에서는 웹 화면에 키를 넣지 마세요.

## 내 기록은 내 PC에만

자기소개서·답변·점수 기록은 이 저장소에 두지 않고 내 PC 면접 폴더(기본 `~/.saerok/interview/`, `SAEROK_INTERVIEW_HOME`으로 바꿈)에만 저장합니다. 웹 화면은 그 브라우저 저장소에만 둡니다.

- 면접 폴더가 git 저장소 안이면 세션을 만들지 않고 멈춥니다.
- 시작 전에 주민번호·전화번호·이메일 꼴을 찾아 가린 값으로 보여 주고, 진행할지 묻습니다.
- 이 폴더의 [`examples/`](examples)는 모두 지어낸 가상 지원자·가상 회사입니다.

## 빠른 시작

Claude Code 플러그인으로 쓸 때는 Claude Code와 Python 3.10 이상이 필요합니다. 설치 없이 쓰려면 위 웹 화면을 엽니다.

**Claude Code 대화창에서** 처음 한 번 설치합니다.

```text
/plugin marketplace add jhheo51-arch/saeroki
/plugin install saerok-interview@saeroki
```

새 대화창에서 `/saerok-interview:panel`을 입력하면, 처음에는 내 PC에 **서류 폴더**(`~/.saerok/interview/서류/`)와 양식 두 개를 만들어 줍니다. 양식을 채우면 준비 끝입니다.

```text
~/.saerok/interview/서류/
├─ 자기소개서.md         내 자기소개서(한 줄에 한 문장)
└─ 공고-골목장터.md      채용 공고 본문. '-' 뒤가 회사 이름
```

그다음부터는 파일 경로 없이 한 줄로 시작합니다. "골목장터 면접 보자"처럼 말해도 됩니다.

```text
/saerok-interview:panel --company 골목장터
```

**터미널에서** Claude Code를 면접 명령과 함께 바로 띄울 수도 있습니다.

```bash
claude "/saerok-interview:panel --company 골목장터"
```

**설치 없이 한 번만 써 보기**: 저장소를 받아 이번 실행에만 플러그인을 불러옵니다.

```bash
git clone https://github.com/jhheo51-arch/saeroki.git
claude --plugin-dir saeroki/fruits/19-saerok-interview "/saerok-interview:panel"
```

어느 방법이든 기록은 저장소가 아니라 내 PC 면접 폴더에 쌓입니다.

원본 AI ANTENNA 방식과 달라진 점, 서류 폴더 위치와 파일 이름 규칙, 자기소개서 쓰는 법, 대화창·말·터미널로 부르는 법, 서류 폴더 밖 파일을 쓰는 법, 심사 뒤 연습·비교까지는 **[사용 안내(GUIDE.md)](GUIDE.md)**에 자세히 적었습니다.

## 쓰는 순서

| 단계 | 명령 | 하는 일 |
|---|---|---|
| 서류 심사 | `/saerok-interview:panel --company 골목장터 --industry platform --role pm` | 서류 폴더에서 자기소개서·공고를 골라 면접관 5명이 동시에 심사하고, 질문 10개(면접관당 2개)와 `verdict.md`를 만듭니다 |
| 실전 연습 | `/saerok-interview:practice --level 보통` | 서류 점수가 낮은 면접관 질문부터 하나씩 묻고, 꼬리 질문 1~2번 뒤 채점해 `practice.md`에 남깁니다 |
| 회차 비교 | `/saerok-interview:compare --last 3` | 답변 점수 변화, 반복해서 낮은 항목, 실제 면접 적중률을 보여 줍니다 |
| 실제 면접 기록 | `/saerok-interview:compare --real <세션 폴더>` | 실제로 받은 질문을 모의 질문과 짝지어 보고, 내가 확인한 짝만 적중으로 셉니다 |

강도는 `순한맛`·`보통`·`매운맛` 세 가지입니다. 산업(`ecommerce`·`platform`·`finance`)·직무(`pm`·`data`·`marketing`·`cx`)를 넘기면 [17번 새록 사전](../17-saerok-dictionary)의 핵심 용어를 실무·숫자 검증 면접관에게 줍니다.

## 면접관 5명과 기준표

면접관마다 4항목 10점입니다. 이 표 밖의 기준으로 점수를 매기지 않고, 볼 수 없는 항목은 0점이 아니라 '해당 없음'으로 빼고 10점으로 환산합니다.

| 면접관 | 3점 항목 | 2점 항목 |
|---|---|---|
| 압박 | 근거·수치, 본인 역할 | 앞뒤 일관성, 침착함(답변에서만) |
| 인사 | 지원 동기, 협업 | 조직 적합, 장기 근속 |
| 실무 | 상황 판단, 실행 순서 | 직무 용어, 공고 요건 연결(공고 필요) |
| 임원 | 회사 이해(공고 필요), 왜 이 회사 | 장기 포부, 핵심 요약(답변에서만) |
| 숫자 검증 | 수치의 출처, 계산 과정 | 지표 정의, 비교 기준 |

판정은 7점 이상 합격권, 5점 이상 보류, 그 아래 부족입니다. 서류 단계의 판정이며 실제 합격 예측이 아닙니다.

## 두 층

- **AI 계층**: 면접관 5명([`agents/`](agents), Sonnet)이 질문·점수를 JSON으로 내고, 실전 채점은 세션 모델이 합니다.
- **결정적 계층**([`saerok_interview/`](saerok_interview), AI 없음): 점수 범위·항목 검사, 근거 원문이 입력 파일 그 줄(±1)에 정말 있는지 확인, `verdict.md`·`practice.md` 렌더링, 회차 비교. 근거 원문을 찾지 못한 질문은 '확인 안 됨, 일반 질문'으로 표시됩니다.

명령만 따로 쓸 수도 있습니다.

```bash
bash bin/saerok-interview init
bash bin/saerok-interview docs --company 골목장터
bash bin/saerok-interview rubric
bash bin/saerok-interview scan examples/resume-letter.md
bash bin/saerok-interview new examples/resume-letter.md --posting examples/posting.md --company 골목장터
bash bin/saerok-interview record <세션 폴더> document --file examples/pressure-result.json
bash bin/saerok-interview report <세션 폴더>
```

## 면접 폴더

```text
~/.saerok/interview/
├─ 서류/          내가 고치는 원본(자기소개서.md · 공고-회사이름.md · 이력서.md · 포트폴리오.md)
└─ 2026-10-17-골목장터/
   ├─ inputs/        자기소개서.md · 채용 공고.md 사본
   ├─ session.json   회사·산업·직무, 입력 파일 sha256
   ├─ score.json     서류 점수·질문, 답변 점수, 실제 면접 질문
   ├─ verdict.md     판정표·기준 항목·질문 10개와 근거·고칠 점
   └─ practice.md    실전 연습 기록
```

## 검사

```bash
python -m unittest test_saerok_interview
```

`data/terms-lite.json`은 17번 새록 사전 용어집을 줄인 사본입니다(플러그인은 저장소 밖에 설치되므로 함께 싣습니다). 17번 용어가 바뀌면 검사가 실패하니, 아래로 다시 만듭니다.

```bash
python -c "from pathlib import Path; from saerok_interview import terms; d=Path('../17-saerok-dictionary/data'); terms.LITE.write_text(terms.dump(terms.build(d/'terms.json', d/'catalog.json')), encoding='utf-8')"
```
