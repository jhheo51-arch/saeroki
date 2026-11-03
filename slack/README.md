# 💬 새록 슬랙

새록이 열매를 내 슬랙 워크스페이스에서 슬래시 명령으로 부릅니다. 봇은 **내 PC에서 Socket Mode로** 돌아서 공개 주소나 서버가 필요 없고, PC에서 `saerok-slack`을 켜 둔 동안에만 답합니다.

| 명령 | 열매 | 하는 일 |
|---|---|---|
| `/saerok-dict 리텐션` | 🌸 17 새록 사전 | 용어집에서 바로 찾아 뜻·공식·예문·출처를 답합니다. AI를 부르지 않고, 없는 말은 짓지 않습니다. 누구나 쓸 수 있습니다. |
| `/saerok-sql 질문` | 🍎 16 새록 SQL | 서울 생활 데이터에 우리말로 묻습니다. |
| `/saerok-idea 아이디어 한 줄` | 🌸 20 새록 심사단 | 아이디어를 심사합니다. 검색어 확인 같은 질문은 스레드로 옵니다. |
| `/saerok-prd 만들 것` | 🍎 4 새록 검토관 | 설계 스무고개를 시작합니다. `/saerok-prd 검사` 뒤 스레드에 PRD 파일을 올리면 검사합니다. |
| `/saerok-interview` | 🌸 19 새록 면접관 | 스레드에 자기소개서(필요하면 공고·이력서도)를 올리면 심사합니다. |
| `/saerok-dict` (빈칸) | 📅 오늘의 용어 | 날짜로 용어 하나를 골라 보여 줍니다. 출처를 확인한 말을 먼저 고릅니다. 누구나, AI 없이. |
| `/saerok-word [첫 단어]` | 🎮 끝말잇기 | 스레드를 열고 답글로 잇습니다. 단어장 [`words.txt`](saerok_slack/words.txt)로만 돌고, 두음법칙을 받습니다. 누구나, AI 없이. |
| `/saerok-case [회차/목록]` | 🦉 숲속 추리 | 숲속 사건 시리즈. 스레드에서 `단서`, 용의자 이름, `범인 이름`, `포기`로 풉니다. 사건은 [`cases.json`](saerok_slack/cases.json)에 회차를 더하면 늘어납니다. 누구나, AI 없이. |
| `/saerok-master [명령]` | 🌳 마스터 | 주인 전용. `상태`, `점검`(AI가 답하는지), `쉬기`/`깨우기`(다른 사람 수다 끄고 켜기), `대화 켜기`/`대화 끄기`(지금 채널, 바로 적용). |

### 구독이 끊겼을 때
사전, 오늘의 용어, 끝말잇기, 숲속 추리는 Claude를 부르지 않아서 구독이나 사용 한도와 상관없이 돕니다. AI를 쓰는 명령이 로그인·구독·한도 오류로 실패하면 원래 오류 대신 "🌙 AI가 지금 답할 수 없어요"와 AI 없이 되는 명령을 안내합니다. 원인은 짧게 덧붙이고, `/saerok-master 상태`의 마지막 AI 오류에도 남습니다.

대화 채널로 정한 곳에서는 `@saeroki`로 불러 일상 대화도 합니다. 누구나 부를 수 있고, 새록이가 답한 스레드에서는 부르지 않아도 이어집니다. 이 대화는 도구, 파일, 인터넷, MCP, 스킬을 모두 끈 채로 돌아서 PC의 어떤 것에도 손대지 못합니다(모델 sonnet).

```powershell
saerok-slack chat C0CF57Y2E48         # 대화 채널로 정하기(봇을 다시 켜면 적용, 슬랙에서 /saerok-master 대화 켜기는 바로 적용)
saerok-slack chat --off C0CF57Y2E48   # 끄기
saerok-slack chat                     # 목록
```

명령 하나가 스레드 하나를 열고, 그 스레드에 답글을 달면 같은 대화로 이어집니다(스레드 하나 = Claude Code 세션 하나).

## 어떻게 도나

- 사전은 [`fruits/17-saerok-dictionary/data/terms.json`](../fruits/17-saerok-dictionary/data/terms.json)을 직접 읽습니다.
- 나머지 열매는 이 PC의 Claude Code를 `claude -p`로 불러 기존 스킬을 그대로 씁니다. 지금 쓰는 Claude 요금제 안에서 돌고 API 키가 따로 필요 없습니다.
- Claude가 쓸 수 있는 도구는 열매마다 정해 둔 것뿐입니다(읽기, 그 열매의 명령, 필요한 열매만 웹 검색). 아무 셸 명령이나 실행할 수는 없습니다.
- 사전과 게임(끝말잇기, 숲속 추리)을 뺀 명령은 **등록한 주인 멤버 ID만** 부를 수 있습니다. 다른 사람이 부르면 거절합니다.
- 올린 파일은 `~/.saerok/slack/inbox`, 스레드와 세션 짝은 `~/.saerok/slack/threads.json`, 열매 기록은 각 열매의 기존 폴더에만 남습니다. 저장소에는 올라가지 않습니다.
- 대화 내용은 슬랙과 Claude를 거치므로 완전한 비공개는 아닙니다. 회사 기밀이나 개인 정보가 든 파일은 올리지 마세요.

## 설치

Python 3.10 이상과 Claude Code가 필요합니다. 16번 SQL을 쓰려면 [16번 설치](../fruits/16-natural-language-sql/README.md#설치)와 `saerok-sql --install-skill`도 먼저 해 둡니다.

```powershell
python -m pip install -e slack
```

## 슬랙 앱 만들기

1. https://api.slack.com/apps 에서 **Create New App → From a manifest**를 누르고 내 워크스페이스를 고릅니다.
2. `saerok-slack manifest`로 나온 JSON(원본: [`saerok_slack/manifest.json`](saerok_slack/manifest.json))을 붙여 넣고 만듭니다.
3. **Basic Information → App-Level Tokens → Generate Token and Scopes**에서 `connections:write`를 넣어 만들면 `xapp-…` 토큰이 나옵니다.
4. **Install App → Install to Workspace**를 누르면 `xoxb-…` Bot Token이 나옵니다.
5. 슬랙에서 내 프로필 → **⋮ → 멤버 ID 복사**로 `U…` 멤버 ID를 얻습니다.
6. **Basic Information → Display Information → App icon**에 [`icon.png`](icon.png)를 올립니다.

토큰은 비밀번호와 같습니다. 대화창, 파일, 커밋에 붙여 넣지 말고 아래 명령에만 입력합니다.

```powershell
saerok-slack setup    # 토큰 두 개와 멤버 ID 입력(토큰은 화면에 안 보임)
saerok-slack status   # 등록 상태 확인(토큰은 가려서 보임)
```

값은 Windows 자격 증명 관리자에만 저장됩니다. 지우려면 `saerok-slack forget`.

## 켜기

저장소 루트의 터미널(VS Code 포함)에 붙여 넣으면 설치, 처음 한 번 등록, 실행을 차례로 합니다.

```powershell
powershell -ExecutionPolicy Bypass -File slack\start.ps1
```

이미 설치하고 등록했다면 `saerok-slack`만 쳐도 됩니다.

"워크스페이스에 연결됐습니다"가 나오면 워크스페이스 어디서나 씁니다. 끄려면 Ctrl+C.

- 공개 채널: 새록이가 없으면 알아서 들어가 답합니다.
- 비공개 채널, 다른 사람과의 DM: 봇이 스스로 들어갈 수 없어서 새록이와의 DM으로 옮겨 이어 갑니다. 그 채널에서 답을 받고 싶으면 `/invite @saeroki`로 한 번 부릅니다.
- `/saerok-dict`는 어디서 치든 그 자리에 답합니다.

## 검사

```powershell
python -m unittest discover -s slack
```

슬랙과 Claude Code에는 접속하지 않습니다. 저장소 루트의 `python -m unittest`에도 포함됩니다.
