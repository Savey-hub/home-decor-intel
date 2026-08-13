# -*- coding: utf-8 -*-
"""读取 Windows 剪贴板 Unicode 文本并写入 UTF-8 文件。
用法: python clip2file.py <输出路径>
"""
import ctypes
import ctypes.wintypes as w
import os
import sys

CF_UNICODETEXT = 13
u = ctypes.windll.user32
k = ctypes.windll.kernel32

u.OpenClipboard.argtypes = [w.HWND]
u.OpenClipboard.restype = w.BOOL
u.GetClipboardData.argtypes = [w.UINT]
u.GetClipboardData.restype = w.HANDLE
k.GlobalLock.argtypes = [w.HANDLE]
k.GlobalLock.restype = ctypes.c_void_p
k.GlobalUnlock.argtypes = [w.HANDLE]


def get_text():
    for _ in range(30):
        if u.OpenClipboard(None):
            break
        ctypes.windll.kernel32.Sleep(100)
    else:
        raise RuntimeError("OpenClipboard 失败")
    try:
        h = u.GetClipboardData(CF_UNICODETEXT)
        if not h:
            return ""
        p = k.GlobalLock(h)
        if not p:
            return ""
        try:
            return ctypes.c_wchar_p(p).value or ""
        finally:
            k.GlobalUnlock(h)
    finally:
        u.CloseClipboard()


def main():
    out = sys.argv[1]
    t = get_text()
    d = os.path.dirname(out)
    if d and not os.path.isdir(d):
        os.makedirs(d)
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write(t)
    print("LEN=%d -> %s" % (len(t), out))


if __name__ == "__main__":
    main()
