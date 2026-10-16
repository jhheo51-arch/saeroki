"""Windows 알림(토스트). 파수꾼 새록이 그림을 곁들여 화면 오른쪽 아래에 띄웁니다.

추가 설치 없이 Windows PowerShell의 WinRT 알림 기능을 씁니다. 훅을 붙잡지 않도록
PowerShell을 따로 띄우고 바로 돌아옵니다.
"""

import base64
import os
import subprocess
import sys

from . import character
from .paths import data_home

TEST = ("파수꾼 새록이 · 알림 시험", "기준을 넘으면 이렇게 알려 드릴게요. 충성!")
# Windows PowerShell이 알림을 보낼 때 쓰는 앱 ID(시작 메뉴에 등록되어 있어 별도 등록이 필요 없음)
APP_ID = r"{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}\WindowsPowerShell\v1.0\powershell.exe"

SCRIPT = r"""
$ErrorActionPreference = 'Stop'
[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
[Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null
$e = [System.Security.SecurityElement]
$t = $e::Escape($env:SAEROK_TOAST_TITLE)
$b = $e::Escape($env:SAEROK_TOAST_BODY)
$i = $e::Escape($env:SAEROK_TOAST_IMAGE)
$xml = "<toast><visual><binding template='ToastGeneric'><text>$t</text><text>$b</text><image placement='appLogoOverride' src='$i'/></binding></visual></toast>"
$doc = New-Object Windows.Data.Xml.Dom.XmlDocument
$doc.LoadXml($xml)
[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier($env:SAEROK_TOAST_APP).Show([Windows.UI.Notifications.ToastNotification]::new($doc))
"""


def sentry_png() -> str:
    """지금 레벨의 파수꾼 새록이 PNG 경로. 레벨이 바뀌면 새로 그립니다."""
    level = character.current_level()
    path = data_home() / f"sentry-lv{level}.png"
    if not path.exists():
        path.write_bytes(character.render_png(level))
    return str(path)


def command(title: str, body: str) -> tuple[list[str], dict]:
    encoded = base64.b64encode(SCRIPT.encode("utf-16-le")).decode("ascii")
    env = {
        **os.environ,
        "SAEROK_TOAST_TITLE": title,
        "SAEROK_TOAST_BODY": body,
        "SAEROK_TOAST_IMAGE": sentry_png(),
        "SAEROK_TOAST_APP": APP_ID,
    }
    args = ["powershell.exe", "-NoProfile", "-NonInteractive", "-WindowStyle", "Hidden", "-EncodedCommand", encoded]
    return args, env


def toast(title: str, body: str, wait: bool = False) -> bool:
    """알림을 띄웁니다. Windows가 아니면 아무것도 하지 않고 False."""
    if sys.platform != "win32":
        return False
    args, env = command(title, body)
    flags = subprocess.CREATE_NO_WINDOW | (0 if wait else subprocess.DETACHED_PROCESS)
    proc = subprocess.Popen(args, env=env, creationflags=flags,
                            stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                            stderr=subprocess.PIPE if wait else subprocess.DEVNULL)
    if not wait:
        return True
    _, err = proc.communicate(timeout=30)
    if proc.returncode:
        raise RuntimeError(err.decode("utf-8", errors="replace").strip() or "알림 실패")
    return True
