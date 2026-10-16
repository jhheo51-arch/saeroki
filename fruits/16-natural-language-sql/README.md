# 🌸 16 새록 SQL

우리말로 물으면 서울 생활 공공 데이터에 맞는 SQL을 만들어 실행하고, 결과표와 쉬운 풀이를 함께 보여 주는 터미널 에이전트입니다. 받은 SQL을 붙여 넣으면 무엇을 하는 쿼리인지 풀어 줍니다.

- 설계: [PRD v1.8](../../docs/PRD-v1.8.md)
- 공통 원칙: [AGENT-SPEC.md](../../AGENT-SPEC.md)
- 두뇌: Claude API(기본 Claude Sonnet 5.5). 질문할 때마다 API 사용량만큼 요금이 듭니다.

```text
PS> saerok-sql
╭─ 새록 SQL ─────────────────────────────────────────────╮
│ 서울 생활 데이터 묶음 13개 표 · 모델 claude-sonnet-5-5 · 읽기 전용 │
╰────────────────────────────────────────────────────────╯
> 2025년 2분기 평일에 따릉이를 가장 많이 탄 동 3곳은?
```

## 설치

Python 3.10 이상에서 저장소 루트에 서서 한 번만 실행합니다.

```powershell
python -m pip install -e fruits/16-natural-language-sql
```

이제 어느 폴더에서든 `saerok-sql`로 엽니다. 처음 열 때 데이터 파일을 한 번 묶느라 몇 초 걸립니다.

## API 키

처음 질문하면 Claude API 키를 묻습니다. https://console.anthropic.com 의 API Keys에서 만든 `sk-ant-…` 키를 붙여 넣으면 Windows 자격 증명 관리자에 저장되고, 파일·기록·화면에는 남지 않습니다. 다시 등록하려면 `/key`를 입력합니다.

## 쓰는 법

| 입력 | 동작 |
|---|---|
| 우리말 질문 | 가정 → SQL → 결과표(최대 1,000행, 화면에는 앞 20행) → 풀이 → 한계·주의 |
| `SELECT`·`WITH`로 시작하는 SQL | 무엇을 하는 SQL인지 풀이하고 실행 결과를 보여 줌 |
| 그 밖의 SQL(`DELETE` 등) | 풀이만 하고 실행은 막음 |
| `/tables`, `/describe 표이름` | 표 목록, 컬럼·기간·출처·주의점 |
| `/explain 파일.sql` | 파일의 SQL 풀이 |
| `/history`, `/export 파일`, `/import 파일` | 기록 보기, 다른 PC로 옮기기 |
| `/model sonnet\|opus\|haiku`, `/key`, `/exit` | 모델 바꾸기, 키 다시 등록, 끝내기 |

한 번만 묻고 끝내려면 `saerok-sql -q "질문"` 또는 `saerok-sql --explain 파일.sql`을 씁니다.

## 안전

- 데이터베이스를 읽기 전용, 외부 파일·네트워크 접근 차단으로 엽니다.
- 실행 전에 SQL을 검사해 문장 하나의 `SELECT`·`WITH` 조회만 통과시킵니다.
- SQL 실행 오류는 AI가 오류를 보고 최대 2번 고칩니다. 그래도 안 되면 실패를 그대로 보여 줍니다.
- 결과가 0행이거나 1,000행을 넘거나 값이 모두 비면 `검토 필요`로 표시하고 고치지 않습니다.
- 기록(`%LOCALAPPDATA%\saerok-sql\history.jsonl`)에는 질문·SQL·행 수·상태만 남고 결과 값은 남지 않습니다.

## 데이터

서울 생활 데이터 13개 표(지하철, 따릉이, 날씨, 배달, 카페·상가, 행정동)를 Parquet으로 압축해 [`data/`](data)에 넣었습니다(약 14MB). 표·컬럼 설명은 [`data/dictionary.json`](data/dictionary.json), 출처와 이용 조건은 [`data/SOURCES.md`](data/SOURCES.md)에 있습니다. AI는 데이터 사전만 보고 SQL을 씁니다.

## 검사

```powershell
python -m unittest -v                # API 없이 도는 자동 검사
python eval/run_eval.py              # 예시 질문 20개 채점(API 비용 발생)
```

채점은 [`eval/questions.json`](eval/questions.json)의 정답 SQL 결과와 새록 SQL이 만든 결과를 비교합니다. 정답 SQL은 Claude가 작성하고 실행해 결과를 확인한 초안이라, 사람이 한 번 더 검토해야 합니다.

## 파일

| 위치 | 내용 |
|---|---|
| [`saerok_sql/cli.py`](saerok_sql/cli.py) | 대화형 화면과 `/명령` |
| [`saerok_sql/agent.py`](saerok_sql/agent.py) | 질문 → SQL → 안전 검사 → 실행 → 자기 검토 |
| [`saerok_sql/llm.py`](saerok_sql/llm.py) | Claude API 호출과 응답 형식 |
| [`saerok_sql/safety.py`](saerok_sql/safety.py) | 실행 전 SQL 안전 검사 |
| [`saerok_sql/db.py`](saerok_sql/db.py) | 데이터 준비와 읽기 전용 실행 |
| [`saerok_sql/dictionary.py`](saerok_sql/dictionary.py) | 데이터 사전 읽기·검사·프롬프트용 글 |
| [`saerok_sql/history.py`](saerok_sql/history.py), [`keystore.py`](saerok_sql/keystore.py) | 기록, API 키 보관 |
| [`scripts/build_data.py`](scripts/build_data.py) | 태블로 프로젝트 정제 CSV를 Parquet으로 다시 만들기 |
| [`test_saerok_sql.py`](test_saerok_sql.py) | 자동 검사 |
