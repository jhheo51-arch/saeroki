# 🌸 1 콘텐츠 개인화

새록이의 첫 열매입니다. 서울 시간대, 날씨와 취향에 맞춰 공개 출처에서 모은 기술 블로그·뉴스레터·음악 후보 가운데 1~3개를 추천 이유와 출처와 함께 고릅니다.

- 상태: 🌸 꽃(만드는 중)
- 설계: [PRD v1.6](../../docs/PRD-v1.6.md), 현재 구현 상태: [PRD v1.5](../../docs/PRD-v1.5.md)
- 공통 원칙: [AGENT-SPEC.md](../../AGENT-SPEC.md)
- 뿌리 12 정보 수집, 13 계획 후 실행, 14 결과 자기 검토는 아직 이 열매의 코드(`saeroki.py`, `source_collector.py`) 안에 들어 있습니다. 다른 열매가 함께 쓰게 되면 따로 떼어 냅니다.

## 파일

| 위치 | 내용 |
|---|---|
| [`saeroki.py`](saeroki.py) | 취향 저장, 출처 검사, 추천, 피드백, 계획 후 실행과 자기 검토 공통 기반 |
| [`saeroki_cli.py`](saeroki_cli.py) | 터미널에서 전체 흐름을 실행하는 도구 |
| [`source_collector.py`](source_collector.py) | 공개 웹페이지·목록·JSON·RSS에서 후보 만들기 |
| [`weather.py`](weather.py) | 서울 현재 날씨와 날씨 코드 확인 |
| [`music_candidates.py`](music_candidates.py) | 직접 관리하는 YouTube Music 후보 읽기 |
| [`test_saeroki.py`](test_saeroki.py) | 자동 검사 |
| [`data/candidates.example.json`](data/candidates.example.json) | 실제 자료가 아닌 기능 확인용 후보 |
| [`data/music-candidates.example.json`](data/music-candidates.example.json) | API 없이 직접 관리하는 YouTube Music 후보 양식 |
| [`data/sources.example.json`](data/sources.example.json) | 공개 출처와 수집 허용 범위 초안 |
| [`data/insight-bookmarks.example.json`](data/insight-bookmarks.example.json) | 이미지에서 옮긴 INSIGHT 북마크 이름 목록 |
| [`claude/PROJECT-INSTRUCTIONS.md`](claude/PROJECT-INSTRUCTIONS.md) | Claude 프로젝트에서 쓸 이 열매의 지침 |
| [`claude/session-input.template.json`](claude/session-input.template.json) | 시간대, 날씨, 취향과 후보 입력 양식 |

## 실행

아래 명령은 모두 이 폴더(`fruits/01-content-personalization`)에서 실행합니다.

```powershell
cd fruits/01-content-personalization
python -m unittest -v
```

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
