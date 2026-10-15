<p align="center">
  <img src="assets/saeroki-hero.svg" alt="새록이, 취향을 따라 자라나는 새로운 발견" width="100%">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/PRD-v1.5-40916C" alt="PRD v1.5">
  <img src="https://img.shields.io/badge/Agent_Ideas-17-90A955" alt="에이전트 후보 17개">
  <img src="https://img.shields.io/badge/Tests-28_passing-31572C" alt="자동 검사 28개 통과">
  <img src="https://img.shields.io/badge/Claude_%2B_Codex-shared_rules-40916C" alt="Claude와 Codex 공통 규칙">
</p>

<p align="center">
  <strong>새록이는 관심 분야에서 아직 알지 못한 항목을 발견하고,<br>근거와 함께 소수만 추천하는 개인 AI 에이전트 프로젝트입니다.</strong>
</p>

<p align="center">
  <img src="assets/saeroki-tree.svg" alt="지금까지 자란 새록이 묘목" width="100%">
</p>

## 새로운 발견부터

> `새`는 새로운 발견, `록`은 초록과 기록을 뜻합니다.
>
> **새록이, 취향을 따라 자라나는 새로운 발견**

새록이는 많이 보여 주는 대신 지금 확인할 가치가 있는 낯선 항목을 1개에서 3개까지 건넵니다. 출처와 추천 이유를 함께 보여 주며, 적절한 후보가 없으면 억지로 추천하지 않습니다.

## 자라는 새록이

새록이는 작은 묘목입니다. 작업을 이어 가고, 사람들이 이 페이지를 찾아오고 스타를 누를수록 Lv.1 새싹에서 Lv.100 세계수까지 자랍니다. 생김새는 레벨마다 모두 다르고, 10레벨마다 새 특징이 하나씩 생깁니다.

<p align="center">
  <img src="assets/saeroki-stages.svg" alt="Lv.1 새싹부터 Lv.100 세계수까지 10레벨마다 달라지는 모습" width="100%">
</p>

| 레벨 | 이름 | 새로 생기는 모습 |
|---:|---|---|
| 1~9 | 새싹 | 떡잎이 커지고 줄기가 올라옵니다 |
| 10~19 | 묘목 | 줄기를 따라 잎이 번갈아 납니다 |
| 20~29 | 어린 나무 | 둥근 잎 덩어리가 생깁니다 |
| 30~39 | 가지 뻗는 나무 | 잎 사이로 가지가 보입니다 |
| 40~49 | 꽃 피는 나무 | 분홍 꽃이 핍니다 |
| 50~59 | 열매 맺는 나무 | 주황 열매가 열리고 빛 입자가 떠오릅니다 |
| 60~69 | 새가 쉬는 나무 | 파랑새가 앉고 줄기가 굵어집니다 |
| 70~79 | 층층이 자라는 나무 | 잎이 두 층으로 쌓이고 뿌리가 땅으로 퍼지며 후광이 비칩니다 |
| 80~89 | 덩굴 드리운 고목 | 덩굴이 늘어지고 몸통에 이끼가 낍니다 |
| 90~99 | 빛을 품은 나무 | 잎이 세 층이 되고 빛나는 잎과 발치의 새싹이 생깁니다 |
| 100 | 세계수 | 밤하늘 아래 빛의 씨앗과 금빛 열매, 빛줄기가 생깁니다 |

### 성장 점수

`성장 점수 = 순방문자 + 스타 × 10 + 작업량`

| 항목 | 세는 방법 |
|---|---|
| 순방문자 | GitHub traffic의 날짜별 순방문자를 더합니다. 한 사람은 새로고침을 여러 번 해도 하루 1점입니다. 저장소 주인의 방문도 포함됩니다. |
| 스타 | 저장소 주인을 뺀 스타 1개당 10점입니다. |
| 작업량 | 사람이 한 커밋마다 1점, 바뀐 줄 50줄마다 1점(커밋당 최대 4점), 작업한 날마다 3점입니다. 봇 커밋, 자동 생성 그림(`assets/`)과 `data/growth.json`은 세지 않습니다. |

- 레벨이 오를수록 필요한 점수가 커집니다. Lv.10은 130점, Lv.20은 501점, Lv.50은 2,756점, Lv.100은 9,774점부터입니다.
- 2026-10-14~15 이틀 동안 커밋 37개로 작업량 79점, Lv.7이 되었습니다. 지금처럼 꾸준히 작업하면 몇 달 안에 Lv.20~30, 해를 넘기면서 Lv.50 근처에 닿도록 맞췄습니다.
- 100레벨 전체 모습은 `python growth.py --preview all-levels.svg`로 한 장에 모아 볼 수 있습니다.
- GitHub Actions가 매일 서울 자정과 `main`에 push할 때 [`growth.py`](growth.py)를 실행해 그림을 다시 그립니다. 점수가 그대로면 기록을 바꾸지 않아 봇 커밋이 생기지 않습니다.
- 순방문자는 GitHub가 최근 14일만 알려 주므로 날짜별로 [`data/growth.json`](data/growth.json)에 쌓아 둡니다. 불러오지 못한 값은 0으로 바꾸지 않고 `확인 전`으로 남깁니다.
- 순방문자를 반영하려면 아래처럼 토큰을 한 번 등록합니다. 등록 전에는 스타와 작업량으로만 자랍니다.
  1. GitHub `Settings` → `Developer settings` → `Fine-grained tokens`에서 새 토큰을 만듭니다. 저장소는 `saeroki`만 고르고 권한은 `Administration: Read-only`만 줍니다.
  2. 저장소 `Settings` → `Secrets and variables` → `Actions`에 `TRAFFIC_TOKEN`이라는 이름으로 저장합니다.
  3. `Actions` 탭의 `새록이 성장`에서 `Run workflow`를 누르거나 다음 자정 실행을 기다립니다.

## 지금의 새록이

| 발견 | 기록 | 확인 |
|---|---|---|
| 관심사와 현재 상황에 맞는 후보를 찾습니다. | 저장, 이미 앎, 관심 없음과 너무 유명함을 기록합니다. | 출처, 날짜와 추천 이유가 없으면 결과를 확정하지 않습니다. |

## 17개 에이전트 지도

| 제품군 | 포함 항목 |
|---|---|
| 추천 | 콘텐츠 개인화, 레시피, 도서 |
| 기획 | 마케팅 전략, PRD 설계 지원 |
| 조사와 분석 | 금융, 미디어 트렌드, 법률 문서, 심층 연구 |
| 데이터 | 데이터 시각화, 자연어 SQL |
| 학습 | 산업별 용어 사전 |
| 공통 기반 | 정보 수집, 계획 후 실행, 결과 자기 검토, Agno 검토 |

초기 방향과 1번부터 16번까지의 원래 목록과 나중에 더한 17번은 [PRD v01](docs/PRD-v01.md)에, 현재 구현 상태는 [PRD v1.5](docs/PRD-v1.5.md)에 보관합니다.

## 프로젝트 지도

| 위치 | 내용 |
|---|---|
| [`docs/PRD-v01.md`](docs/PRD-v01.md) | 제품 방향, 17개 후보, 위험과 개발 순서 |
| [`docs/PRD-v1.5.md`](docs/PRD-v1.5.md) | 현재 구현 범위, 실행 방법, 17개 상태와 Claude 이어하기 안내 |
| [`docs/PRD-v1.6.md`](docs/PRD-v1.6.md) | 1번 콘텐츠 개인화 에이전트의 스무고개 확정 설계 |
| [`docs/CLAUDE-HANDOFF.md`](docs/CLAUDE-HANDOFF.md) | Codex push 후 Claude Code pull 또는 웹앱 프로젝트 업로드 절차 |
| [`claude/PROJECT-INSTRUCTIONS.md`](claude/PROJECT-INSTRUCTIONS.md) | Claude 프로젝트에서 사용할 새록이 지침 |
| [`claude/session-input.template.json`](claude/session-input.template.json) | 시간대, 날씨, 취향과 후보 입력 양식 |
| [`AGENT-SPEC.md`](AGENT-SPEC.md) | 모든 에이전트가 함께 지킬 판단 원칙 |
| [`AGENTS.md`](AGENTS.md) | Codex 작업 안내 |
| [`CLAUDE.md`](CLAUDE.md) | Claude 작업 안내 |
| [`saeroki.py`](saeroki.py) | 취향 저장부터 자기 검토까지의 공통 기반 |
| [`saeroki_cli.py`](saeroki_cli.py) | 터미널에서 전체 흐름을 실행하는 도구 |
| [`source_collector.py`](source_collector.py) | 공개 웹페이지 메타데이터 확인 |
| [`growth.py`](growth.py) | 성장 점수, 100레벨 계산과 픽셀 묘목 SVG 생성 |
| [`weather.py`](weather.py) | 서울 현재 날씨와 날씨 코드 확인 |
| [`data/candidates.example.json`](data/candidates.example.json) | 실제 자료가 아닌 기능 확인용 후보 |
| [`data/music-candidates.example.json`](data/music-candidates.example.json) | API 없이 직접 관리하는 YouTube Music 후보 양식 |
| [`data/sources.example.json`](data/sources.example.json) | 공개 출처와 수집 허용 범위 초안 |
| [`data/insight-bookmarks.example.json`](data/insight-bookmarks.example.json) | 이미지에서 옮긴 INSIGHT 북마크 이름 목록 |

## 직접 확인하기

Python이 설치된 터미널에서 다음 명령을 실행합니다.

```powershell
python -m unittest -v
```

검사는 이미 아는 항목과 제외 태그를 거르는지, 인기도 자료가 없을 때 덜 유명하다고 단정하지 않는지 확인합니다.

### 확인된 공개 출처에서 후보 만들기

출처 목록에서 `status`가 `confirmed_public`인 주소만 읽어 제목과 게시 시각을 후보 파일로 만듭니다. 로그인이나 구독이 필요한 주소, 아직 확인하지 않은 주소는 자동으로 건너뜁니다.

```powershell
python saeroki_cli.py collect --sources data/sources.example.json --output data/candidates.collected.local.json
```

`data/candidates.collected.local.json`은 실행 때 만들어지는 로컬 결과라 GitHub에 올리지 않습니다. 수집에 실패한 주소는 명령 결과의 `errors`에 남깁니다.

### 첫 추천 흐름 실행

아래 명령은 기능 확인용 취향 파일을 만들고 예시 후보를 추천합니다. `data/profile.local.json`과 실행 기록은 GitHub에 올라가지 않도록 제외했습니다.

```powershell
python saeroki_cli.py init-profile --output data/profile.local.json --interest AI --interest 데이터 --exclude 광고
python saeroki_cli.py recommend --profile data/profile.local.json --candidates data/candidates.example.json --log data/run-log.jsonl
python saeroki_cli.py feedback --profile data/profile.local.json --candidate example-data-story --action saved
```

시간대별 추천 구성은 서울 시간 기준으로 아래처럼 실행할 수 있습니다. `--at`을 생략하면 현재 시각을 사용합니다.

```powershell
python saeroki_cli.py scheduled-recommend --profile data/profile.local.json --candidates data/candidates.example.json --at 2026-10-15T08:00:00+09:00
python saeroki_cli.py scheduled-recommend --profile data/profile.local.json --candidates data/candidates.example.json --live-weather --at 2026-10-15T08:00:00+09:00
python saeroki_cli.py scheduled-recommend --profile data/profile.local.json --candidates data/candidates.example.json --music-candidates data/music-candidates.example.json --live-weather --at 2026-10-15T08:00:00+09:00
```

음악 후보는 `data/music-candidates.example.json`에 직접 추가합니다. 각 항목에는 `content_type`을 `music`으로 쓰고 `music.youtube.com` 또는 YouTube 주소를 넣어야 합니다. 후보를 새록이가 자동으로 검색하지 않으므로 API 키가 필요하지 않습니다.

```json
{
  "id": "artist-song",
  "title": "곡 제목",
  "url": "https://music.youtube.com/watch?v=VIDEO_ID",
  "tags": ["발라드", "비"],
  "source": "공식 아티스트 채널",
  "checked_at": "2026-10-15T08:00:00+09:00",
  "content_type": "music"
}
```

현재 후보 자료는 흐름을 확인하기 위한 가상 예시입니다. 실제 기술 블로그와 뉴스레터를 수집한 결과가 아닙니다.

## 다음 잎사귀

- [x] 제품군과 16개 후보를 정리한 PRD v01
- [x] 17번 산업별 용어 사전 에이전트 후보 추가
- [x] Claude와 Codex가 함께 읽는 공통 행동 원칙
- [x] 취향 저장, 출처 검사, 중복 제거와 추천 이유
- [x] 계획 후 실행, 결과 자기 검토와 실행 기록
- [x] 저장, 이미 앎, 관심 없음과 너무 유명함 피드백
- [x] 콘텐츠 개인화 공통 기반의 자동 검사 21개
- [x] 순방문자, 스타와 작업량으로 Lv.100 세계수까지 자라는 픽셀 묘목 새록이
- [x] 서울 시간대별 추천 구성
- [x] 서울 현재 날씨를 아침 음악 추천에 전달
- [x] API 없이 수동 YouTube Music 후보 목록 사용
- [x] 공개 웹페이지 메타데이터 파서
- [x] 확인된 공개 출처에서 후보 JSON 만들기
- [x] 공개 목록의 개별 링크를 후보로 바꾸는 기본 추출기
- [x] 뉴닉 공개 출처 후보와 수집 범위 기록
- [x] 뉴닉 주간 에디터 픽 공개 JSON에서 아티클 후보 만들기
- [x] INSIGHT 북마크 이름 59개 기록
- [x] RSS 2.0와 Atom 후보 변환기
- [x] AWS 한국 기술 블로그 RSS 주소 연결
- [x] 토스 테크, 카카오 테크, NAVER D2 RSS 주소 연결
- [ ] 추가 기술 블로그와 뉴스레터 RSS 주소 연결
- [x] 뉴닉 공개 목록에서 실제 아티클 링크 연결
- [ ] 날씨에 맞는 실제 음악 후보 출처 연결
- [ ] Claude 또는 OpenAI API 연결

현재 1번 콘텐츠 개인화 에이전트의 첫 작동 버전은 여기까지 구현했습니다. 서울 시간대별 추천, 날씨를 반영한 음악 후보, 출처가 확인된 글, 추천 이유, 피드백 저장과 다음 추천 반영을 포함합니다. 실제 RSS 자동 수집과 Claude API 연결은 다음 확장 범위입니다.

공통 기반이 실제 첫 추천 흐름에서 부족할 때만 다음 기술을 추가합니다.

---

<p align="center"><sub>Palette: #FAF9F6 / #ECF39E / #90A955 / #40916C / #31572C</sub></p>
