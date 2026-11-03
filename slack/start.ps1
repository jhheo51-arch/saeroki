# 새록 슬랙 한 번에 켜기: 설치 → (처음이면) 토큰 등록 → 봇 실행
# 사용: powershell -ExecutionPolicy Bypass -File slack\start.ps1
$here = Split-Path -Parent $MyInvocation.MyCommand.Path

python -c "import saerok_slack" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "새록 슬랙을 설치합니다..."
    python -m pip install -q -e $here
}

python -c "from saerok_slack import config; import sys; sys.exit(0 if all(config.get(n) for n in config.FIELDS) else 1)"
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "토큰 두 개와 멤버 ID를 등록합니다. 토큰은 입력해도 화면에 보이지 않습니다(정상)."
    python -m saerok_slack setup
}

python -m saerok_slack
