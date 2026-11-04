"""Windows 휴지통으로 보내기. 영구 삭제와 휴지통 비우기는 하지 않습니다."""

import os
import sys
from pathlib import Path

FO_DELETE = 0x0003
FOF_SILENT = 0x0004
FOF_NOCONFIRMATION = 0x0010
FOF_ALLOWUNDO = 0x0040
FOF_NOERRORUI = 0x0400


def send(path: Path) -> None:
    """파일이나 폴더 하나를 휴지통으로 보냅니다. 실패하면 RuntimeError."""
    if sys.platform != "win32":
        raise RuntimeError("휴지통 보내기는 Windows에서만 합니다.")
    if not path.exists():
        raise RuntimeError(f"이미 없는 파일입니다: {path}")
    import ctypes
    from ctypes import wintypes

    class SHFILEOPSTRUCTW(ctypes.Structure):
        _fields_ = [("hwnd", wintypes.HWND), ("wFunc", wintypes.UINT), ("pFrom", wintypes.LPCWSTR),
                    ("pTo", wintypes.LPCWSTR), ("fFlags", ctypes.c_ushort), ("fAnyOperationsAborted", wintypes.BOOL),
                    ("hNameMappings", ctypes.c_void_p), ("lpszProgressTitle", wintypes.LPCWSTR)]

    op = SHFILEOPSTRUCTW()
    op.wFunc = FO_DELETE
    op.pFrom = os.path.abspath(path) + "\0"  # 두 번 끝나는 문자열
    op.fFlags = FOF_ALLOWUNDO | FOF_NOCONFIRMATION | FOF_SILENT | FOF_NOERRORUI
    result = ctypes.windll.shell32.SHFileOperationW(ctypes.byref(op))
    if result != 0 or op.fAnyOperationsAborted or path.exists():
        raise RuntimeError(f"휴지통으로 보내지 못했습니다(코드 {result}): {path}")
