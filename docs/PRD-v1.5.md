# 새록이 AI 에이전트 PRD v1.5

- 작성일: 2026-10-14
- 상태: 공통 기반과 첫 콘텐츠 수집 흐름 구현 완료
- 공개 범위: 공개 저장소(2026-10-15 비공개에서 전환)
- 기준 문서: [PRD v01](PRD-v01.md)의 방향을 유지하고, 이 문서는 현재 구현 상태를 기록함

## 1. 현재 제품 정의

새록이는 사용자가 지정한 관심 영역에서 공개 콘텐츠 후보를 찾고, 출처와 확인 정보를 붙여 소수의 항목을 추천하는 개인 AI 에이전트입니다.

현재 구현 대상은 1번 `Content Personalization Agent`입니다. 기술 블로그와 뉴스레터를 먼저 다루며, 사용자가 필요할 때 실행할 수 있는 수동 추천 흐름을 갖춥니다. 정기 실행, 날씨 기반 음악 추천과 외부 모델 연결은 아직 구현하지 않았습니다.

## 2. 지금 실제로 작동하는 흐름

`출처 JSON 읽기 → 공개 상태 확인 → 웹 메타데이터 또는 공개 JSON 수집 → 후보 JSON 만들기 → 취향과 제외 조건으로 추천 → 사용자 반응 기록`

### 구현된 기능

- 관심 키워드, 제외 키워드, 상황과 최대 인기도 기준을 로컬 JSON에 저장
- 후보의 제목, 원문 주소, 출처, 확인 시각, 게시 시각, 작성자와 인기도 저장
- 추적 매개변수를 제외한 URL 중복 제거
- 이미 본 항목, 제외 태그와 최대 인기도 기준 필터
- 추천 이유와 인기도 자료가 없을 때의 주의 문구 생성
- 최대 3개 추천
- `저장`, `이미 알고 있음`, `관심 없음`, `너무 유명함` 반응 기록
- 계획 수립, 단계별 실행, 결과 자기 검토와 실행 기록
- 확인 전 주소와 로그인, 구독 전용 주소 건너뛰기
- 공개 HTML의 제목, 설명과 게시 시각 메타데이터 읽기
- 공개 목록 링크 추출 시 공통 메뉴 링크 제외
- 뉴닉 주간 에디터 픽 공개 JSON에서 아티클 후보 생성
- Claude와 Codex가 함께 읽는 공통 행동 원칙 문서

### 현재 확인 결과

- Python 자동 검사 18개 통과
- 뉴닉 주간 에디터 픽 1페이지에서 공개 아티클 16개 수집
- 홈 후보 1개를 포함한 로컬 후보 JSON 17개 생성
- 로그인이나 구독 전용 원문은 수집하지 않음
- 수집 결과 파일은 `.local.json`으로 관리해 저장소에 올리지 않음

## 3. 파일 구조와 실행 방법

| 파일 | 역할 |
|---|---|
| `fruits/01-content-personalization/saeroki.py` | 취향, 후보, 추천, 피드백과 자기 검토 공통 로직 |
| `fruits/01-content-personalization/saeroki_cli.py` | 취향 초기화, 추천, 피드백과 출처 수집 명령 |
| `fruits/01-content-personalization/source_collector.py` | 공개 HTML, 공개 링크와 공개 JSON을 후보로 변환 |
| `fruits/01-content-personalization/data/sources.example.json` | 수집할 공개 출처와 수집 방식 |
| `fruits/01-content-personalization/data/candidates.example.json` | 기능 확인용 가상 후보 |
| `fruits/01-content-personalization/data/insight-bookmarks.example.json` | 이미지에서 옮긴 INSIGHT 북마크와 주소 상태 |
| `fruits/01-content-personalization/test_saeroki.py` | 공통 로직과 수집 흐름 자동 검사 |
| `fruits/17-saerok-dictionary/glossary.py` | 새록 사전 용어집 형식 검사와 화면용 `web/data.js` 생성 |
| `fruits/17-saerok-dictionary/data/catalog.json`, `fruits/17-saerok-dictionary/data/terms.json` | 새록 사전 산업·직무·목적 목록과 출처를 붙인 용어집 |
| `fruits/17-saerok-dictionary/web/index.html`, `fruits/17-saerok-dictionary/web/saerok-core.js` | 브라우저로 여는 새록 사전 화면과 검색·뜻 순서·오늘의 용어 로직 |
| `fruits/17-saerok-dictionary/test_glossary.py` | 새록 사전 데이터 형식과 화면 로직 자동 검사 |
| `AGENT-SPEC.md` | Claude와 Codex가 공유하는 판단 원칙 |

```powershell
python -m unittest -v
cd fruits/01-content-personalization
python saeroki_cli.py collect --sources data/sources.example.json --output data/candidates.collected.local.json
python saeroki_cli.py init-profile --output data/profile.local.json --interest AI --interest 데이터 --exclude 광고
python saeroki_cli.py recommend --profile data/profile.local.json --candidates data/candidates.collected.local.json --log data/run-log.jsonl
```

## 4. 열매와 뿌리 현재 상태

열매 12개와 뿌리 4개의 진행 상태입니다. 🌱 씨앗은 기획만 저장, 🌸 꽃은 만드는 중, 🍎 열매는 첫 버전 완성입니다. 아직 열매 상태에 닿은 항목은 없습니다.

| 번호 | 에이전트 | 구분 | 상태 | v1.5 메모 |
|---:|---|---|---|---|
| 1 | Content Personalization Agent | 열매 | 🌸 꽃 | 공통 기반과 뉴닉 공개 아티클 수집 구현 중 |
| 2 | Agno | 뿌리 | 🌱 씨앗 | 별도 제품이 아닌 전체 에이전트 운영 기반으로 설계, 미도입 |
| 3 | Marketing Strategy Generator | 열매 | 🌱 씨앗 | 기획만 저장 |
| 4 | PRD 설계 지원 에이전트 | 열매 | 🌱 씨앗 | 기획만 저장 |
| 5 | Data Visualization Group Chat | 열매 | 🌱 씨앗 | 기획만 저장 |
| 6 | Recipe Creator | 열매 | 🌱 씨앗 | 기획만 저장 |
| 7 | Finance Agent (고급) | 열매 | 🌱 씨앗 | 기획만 저장, 금융 판단 보호 기준만 기록 |
| 8 | Media Trend Analysis Agent | 열매 | 🌱 씨앗 | 기획만 저장 |
| 9 | Legal Document Analysis | 열매 | 🌱 씨앗 | 10번과 통합한 하나의 제품으로 기획만 저장 |
| 10 | Legal Document Analysis | 9번 열매에 통합 | 9번에 통합 | 9번과 중복되어 별도 구현하지 않음 |
| 11 | Book Recommendation Agent | 열매 | 🌱 씨앗 | 기획만 저장 |
| 12 | Information Gathering Prompting | 뿌리 | 🌸 꽃 | 공개 출처 수집 기능 일부 구현 |
| 13 | Plan-and-Execute Agent | 뿌리 | 🌸 꽃 | 추천 실행 계획과 단계 기록 일부 구현 |
| 14 | Reflection Agent | 뿌리 | 🌸 꽃 | 결과 자기 검토 일부 구현 |
| 15 | Research Agent | 열매 | 🌱 씨앗 | 기획만 저장 |
| 16 | SQL 관련 Agent | 열매 | 🌸 꽃 | 이름 새록 SQL, [PRD v1.8](PRD-v1.8.md) 첫 버전 구현 중: `saerok-sql` 대화형 터미널, Claude API, DuckDB 읽기 전용, 서울 생활 데이터 13개 표 |
| 17 | 산업별 용어 정리 사전 | 열매 | 🌸 꽃 | 이름 새록 사전, [PRD v1.7](PRD-v1.7.md) 첫 버전 구현 중: 산업 3개(금융·증권 포함) 용어 178개, 사전 웹 화면(GitHub Pages 배포), 자동 검사 |

17개 목록과 원래 목적은 축약하지 않고 [PRD v01](PRD-v01.md)에 보존합니다. 실제 독립 제품 수를 셀 때는 9번과 10번을 하나로 관리합니다.

## 5. Claude에서 이어서 작업하는 방법

Claude는 작업 전에 아래 순서로 읽습니다.

1. `README.md`
2. `docs/PRD-v1.5.md`
3. `docs/PRD-v01.md`
4. `AGENT-SPEC.md`

제품 규칙은 특정 AI 서비스의 기억이나 설정에 두지 않고 Markdown, Python과 JSON 파일에 보관합니다. 따라서 Claude에서는 `CLAUDE.md`의 안내에 따라 v1.5와 공통 원칙을 읽고, 같은 명령으로 검사할 수 있습니다.

## 6. 아직 결정하거나 구현하지 않은 것

- 뉴닉 공개 JSON의 다음 페이지 자동 순회
- INSIGHT 목록에 기록한 기술 블로그의 RSS 또는 공개 글 목록 연결
- 정기 추천과 알림
- 날씨 기반 음악 추천과 숨은 명곡 판단 기준
- 도서와 레시피 추천
- Claude와 OpenAI 모델 연결 교체
- 외부 데이터베이스와 장기 사용자 계정
- 금융, 법률과 SQL 기능의 실제 안전장치

## 7. 완료 기준

v1.5는 현재 작동 범위를 기록한 문서입니다. 다음 버전으로 넘어가려면 뉴닉 다음 페이지 수집, INSIGHT 출처 한 곳 이상의 개별 글 수집, 추천 화면 확인과 사용자의 실제 피드백 기록이 필요합니다.
