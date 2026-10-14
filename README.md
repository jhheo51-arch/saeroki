<p align="center">
  <img src="assets/saeroki-hero.svg" alt="새록이, 취향을 따라 자라나는 새로운 발견" width="100%">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/PRD-v0.1-40916C" alt="PRD v0.1">
  <img src="https://img.shields.io/badge/Agent_Ideas-16-90A955" alt="에이전트 후보 16개">
  <img src="https://img.shields.io/badge/Tests-3_passing-31572C" alt="자동 검사 3개 통과">
  <img src="https://img.shields.io/badge/Claude_%2B_Codex-shared_rules-40916C" alt="Claude와 Codex 공통 규칙">
</p>

<p align="center">
  <strong>새록이는 관심 분야에서 아직 알지 못한 항목을 발견하고,<br>근거와 함께 소수만 추천하는 개인 AI 에이전트 프로젝트입니다.</strong>
</p>

<p align="center">
  <img src="assets/saeroki-motion.svg" alt="새록이 캐릭터가 초록 들판을 천천히 왔다 갔다 하는 모습" width="100%">
</p>

## 새로운 발견부터

> `새`는 새로운 발견, `록`은 초록과 기록을 뜻합니다.
>
> **새록이, 취향을 따라 자라나는 새로운 발견**

새록이는 많이 보여 주는 대신 지금 확인할 가치가 있는 낯선 항목을 1개에서 3개까지 건넵니다. 출처와 추천 이유를 함께 보여 주며, 적절한 후보가 없으면 억지로 추천하지 않습니다.

## 지금의 새록이

| 발견 | 기록 | 확인 |
|---|---|---|
| 관심사와 현재 상황에 맞는 후보를 찾습니다. | 저장, 이미 앎, 관심 없음과 너무 유명함을 기록합니다. | 출처, 날짜와 추천 이유가 없으면 결과를 확정하지 않습니다. |

## 16개 에이전트 지도

| 제품군 | 포함 항목 |
|---|---|
| 추천 | 콘텐츠 개인화, 레시피, 도서 |
| 기획 | 마케팅 전략, PRD 설계 지원 |
| 조사와 분석 | 금융, 미디어 트렌드, 법률 문서, 심층 연구 |
| 데이터 | 데이터 시각화, 자연어 SQL |
| 공통 기반 | 정보 수집, 계획 후 실행, 결과 자기 검토, Agno 검토 |

상세 범위와 1번부터 16번까지의 원래 목록은 [제품군 PRD](docs/PRD-v01.md)에 보관합니다.

## 프로젝트 지도

| 위치 | 내용 |
|---|---|
| [`docs/PRD-v01.md`](docs/PRD-v01.md) | 제품 방향, 16개 후보, 위험과 개발 순서 |
| [`AGENT-SPEC.md`](AGENT-SPEC.md) | 모든 에이전트가 함께 지킬 판단 원칙 |
| [`AGENTS.md`](AGENTS.md) | Codex 작업 안내 |
| [`CLAUDE.md`](CLAUDE.md) | Claude 작업 안내 |
| [`saeroki.py`](saeroki.py) | 첫 번째 모델 독립 추천 흐름 |

## 직접 확인하기

Python이 설치된 터미널에서 다음 명령을 실행합니다.

```powershell
python -m unittest -v
```

검사는 이미 아는 항목과 제외 태그를 거르는지, 인기도 자료가 없을 때 덜 유명하다고 단정하지 않는지 확인합니다.

## 다음 잎사귀

- [x] 제품군과 16개 후보를 정리한 PRD v01
- [x] Claude와 Codex가 함께 읽는 공통 행동 원칙
- [x] 콘텐츠 개인화 추천의 최소 코드와 자동 검사
- [ ] 기술 블로그와 뉴스레터 RSS 연결
- [ ] 사용자 취향과 추천 반응 저장
- [ ] 날씨 기반 음악 추천 실험
- [ ] Claude 또는 OpenAI API 연결

공통 기반이 실제 첫 추천 흐름에서 부족할 때만 다음 기술을 추가합니다.

---

<p align="center"><sub>Palette: #FAF9F6 / #ECF39E / #90A955 / #40916C / #31572C</sub></p>
