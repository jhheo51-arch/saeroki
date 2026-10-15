# 🌸 17 새록 사전

산업과 직무를 고르고 단어나 목적을 입력하면, 그 산업과 직무에서 자주 쓰는 용어를 사전처럼 출처와 함께 풀어 주는 온보딩용 용어 사전입니다. 주 용도는 입사 후 온보딩, 보조 용도는 면접 준비입니다.

- 설계: [PRD v1.7](../../docs/PRD-v1.7.md)
- 공통 원칙: [AGENT-SPEC.md](../../AGENT-SPEC.md)
- 첫 버전은 AI 없이 검수한 용어집만 씁니다. Claude API 보충은 다음 단계입니다.

## 지금 용어집

- 산업 2개(이커머스·리테일, IT·플랫폼 서비스) × 직무 4개(기획 PM·PO, 데이터 분석, 마케팅·그로스, CX·운영)
- 용어 132개, 뜻 137개. 칸마다 39~57개
- 뜻마다 직접 확인한 출처와 확인 날짜를 붙였습니다. 113개 뜻은 공식 문서, 24개 뜻은 기업 자료 기준이며 화면에 그 사실을 표시합니다.

## 파일

| 위치 | 내용 |
|---|---|
| [`web/index.html`](web/index.html) | 사전 화면. 내려받은 저장소에서 브라우저로 바로 엽니다 |
| [`web/saerok-core.js`](web/saerok-core.js) | 검색, 뜻 순서, 오늘의 용어, 목적형 묶음 로직 |
| [`web/data.js`](web/data.js) | 화면용 데이터(자동 생성, 직접 고치지 않음) |
| [`data/catalog.json`](data/catalog.json) | 산업·직무·목적 목록. 코드 수정 없이 늘릴 수 있습니다 |
| [`data/terms.json`](data/terms.json) | 출처를 붙인 용어집 |
| [`glossary.py`](glossary.py) | 용어집 형식·출처·칸별 개수 검사와 `web/data.js` 생성 |
| [`test_glossary.py`](test_glossary.py) | 데이터 형식과 화면 로직 자동 검사 |

## 사전 열기

저장소를 내려받은 뒤 [`web/index.html`](web/index.html)을 브라우저로 엽니다. 서버가 필요 없습니다. 저장소가 비공개라 GitHub 웹에서는 화면이 아닌 소스 코드로 보입니다.

산업과 직무를 고르면 오늘의 용어, 목적 버튼(입사 첫 주·면접 준비·지표 이해)과 검색을 쓸 수 있습니다. 내 단어장과 아직 없는 용어 기록은 이 브라우저에만 저장됩니다.

## 용어 고치기

`data/terms.json`이나 `data/catalog.json`을 고친 뒤 이 폴더에서 검사하고 화면용 데이터를 다시 만듭니다.

```powershell
cd fruits/17-saerok-dictionary
python glossary.py check
python glossary.py build
python -m unittest -v
```

출처는 직접 열어 본 페이지만 붙입니다. 출처를 찾지 못한 뜻은 `status`를 `needs_check`로 두면 화면에 `확인 필요`로 표시됩니다.
