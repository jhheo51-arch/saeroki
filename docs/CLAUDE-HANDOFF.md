# Codex에서 Claude로 넘기는 방법

## Claude Code를 사용할 때

Codex가 GitHub에 push한 뒤 Claude Code의 저장소 터미널에서 다음을 실행합니다.

```powershell
git pull origin main
```

그다음 Claude Code에 아래 파일을 먼저 읽도록 요청합니다.

- `claude/PROJECT-INSTRUCTIONS.md`
- `docs/PRD-v1.6.md`
- `docs/PRD-v1.5.md`
- `AGENT-SPEC.md`
- `claude/session-input.template.json`

## Claude 웹앱 프로젝트를 사용할 때

Claude 웹앱 프로젝트는 이 저장소의 Git 브랜치를 자동으로 당겨오는 환경으로 가정하지 않습니다. Codex가 push한 뒤 다음 파일을 Claude 프로젝트에 최신본으로 업로드합니다.

- `claude/PROJECT-INSTRUCTIONS.md`
- `docs/PRD-v1.6.md`
- `docs/PRD-v1.5.md`
- `AGENT-SPEC.md`
- 최신 후보 JSON
- 사용자 취향과 피드백 파일

업로드 후 Claude에게 다음 문장을 보냅니다.

```text
업로드한 PROJECT-INSTRUCTIONS.md를 최우선 작업 지침으로 읽고, PRD v1.6의 시간대와 콘텐츠 구성에 따라 후보 JSON에서만 추천해 주세요. 후보를 새로 만들지 말고 제목, 한 문장 추천 이유, 원문 링크만 출력해 주세요.
```

## 반영 순서

1. Codex에서 문서와 코드를 수정합니다.
2. 자동 검사를 실행합니다.
3. GitHub `main`에 push합니다.
4. Claude Code는 `git pull origin main`을 실행합니다.
5. Claude 웹앱 프로젝트는 변경된 문서를 다시 업로드합니다.

Claude에서 읽은 결과나 사용자 피드백을 저장소에 반영할 때는 원본 문서를 덮어쓰지 않고 새 결과 파일로 저장합니다.
