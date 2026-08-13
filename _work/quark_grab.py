# -*- coding: utf-8 -*-
"""在【前台夸克窗口】执行 ctrl+t -> ctrl+l -> 输入网址 -> 回车 -> 等待 -> ctrl+a -> ctrl+c -> 落盘。

用法:
    python quark_grab.py nav   <url> <outfile> [wait_sec]   # 新标签页打开并抓取
    python quark_grab.py grab  <outfile> [wait_sec]         # 只重新 ctrl+a/ctrl+c 抓取当前页
    python quark_grab.py close                              # ctrl+w 关掉当前(自己开的)标签页
    python quark_grab.py title                               # 打印当前前台窗口标题
    python quark_grab.py scroll <n>                          # 向下滚 n 屏(PageDown)

安全保证:
  1) 发送任何按键前校验前台进程必须是 quark.exe, 否则直接报错退出(绝不会把网址打进钉钉/Chrome)。
  2) ctrl+c 之前先把剪贴板写入哨兵值, 若抓取后剪贴板仍是哨兵值则判定为"没抓到",
     绝不会把上一个站点的残留内容误当成本站正文落盘。
"""
import ctypes
import ctypes.wintypes as w
import os
import sys
import time

u = ctypes.windll.user32
k = ctypes.windll.kernel32

CF_UNICODETEXT = 13
GMEM_MOVEABLE = 0x0002
KEYEVENTF_KEYUP = 0x0002
SENTINEL = "\u0001__QUARK_GRAB_SENTINEL__\u0001"

k.GlobalAlloc.restype = w.HANDLE
k.GlobalLock.argtypes = [w.HANDLE]
k.GlobalLock.restype = ctypes.c_void_p
k.GlobalUnlock.argtypes = [w.HANDLE]
u.GetClipboardData.argtypes = [w.UINT]
u.GetClipboardData.restype = w.HANDLE
u.SetClipboardData.argtypes = [w.UINT, w.HANDLE]
u.SetClipboardData.restype = w.HANDLE

VK = {
    "ctrl": 0x11, "shift": 0x10, "alt": 0x12,
    "t": 0x54, "l": 0x4C, "a": 0x41, "c": 0x43, "v": 0x56, "w": 0x57,
    "enter": 0x0D, "esc": 0x1B, "pagedown": 0x22, "end": 0x23, "home": 0x24,
}


# ---------------- clipboard ----------------
def _open_clip():
    for _ in range(60):
        if u.OpenClipboard(None):
            return
        k.Sleep(100)
    raise RuntimeError("OpenClipboard 失败")


def clip_get():
    _open_clip()
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


def clip_set(text):
    _open_clip()
    try:
        u.EmptyClipboard()
        buf = ctypes.create_unicode_buffer(text)
        size = ctypes.sizeof(buf)
        h = k.GlobalAlloc(GMEM_MOVEABLE, size)
        p = k.GlobalLock(h)
        ctypes.memmove(p, buf, size)
        k.GlobalUnlock(h)
        u.SetClipboardData(CF_UNICODETEXT, h)
    finally:
        u.CloseClipboard()


# ---------------- foreground guard ----------------
def fg_info():
    h = u.GetForegroundWindow()
    pid = w.DWORD()
    u.GetWindowThreadProcessId(h, ctypes.byref(pid))
    name = "?"
    hp = k.OpenProcess(0x1000, False, pid.value)  # QUERY_LIMITED_INFORMATION
    if hp:
        buf = ctypes.create_unicode_buffer(1024)
        n = w.DWORD(1024)
        if k.QueryFullProcessImageNameW(hp, 0, buf, ctypes.byref(n)):
            name = os.path.basename(buf.value)
        k.CloseHandle(hp)
    ln = u.GetWindowTextLengthW(h) + 1
    tb = ctypes.create_unicode_buffer(ln)
    u.GetWindowTextW(h, tb, ln)
    return name, tb.value


def require_quark():
    name, title = fg_info()
    if "quark" not in name.lower():
        raise SystemExit("ABORT 前台窗口不是夸克, 拒绝发送按键. process=%s title=%s" % (name, title))
    return name, title


# ---------------- keys ----------------
def release_mods():
    """强制松开 ctrl/shift/alt, 防止残留修饰键把 pagedown 变成 ctrl+pagedown(切标签页)。"""
    for c in (VK["ctrl"], VK["shift"], VK["alt"]):
        u.keybd_event(c, KEYEVENTF_KEYUP, 0, 0)
    time.sleep(0.05)


def key(*names, **kw):
    require_quark()
    release_mods()
    codes = [VK[n] for n in names]
    for c in codes:
        u.keybd_event(c, 0, 0, 0)
    time.sleep(0.06)
    for c in reversed(codes):
        u.keybd_event(c, KEYEVENTF_KEYUP, 0, 0)
    time.sleep(kw.get("after", 0.35))


def type_text(text):
    """用剪贴板粘贴输入(URL 全 ASCII, 稳定且快)。"""
    clip_set(text)
    key("ctrl", "v")


def capture(outfile, wait=0.0, tag=""):
    if wait:
        time.sleep(wait)
    clip_set(SENTINEL)          # 哨兵: 防止把上一站残留当成本站正文
    time.sleep(0.2)
    key("ctrl", "a", after=0.5)
    key("ctrl", "c", after=1.2)
    t = clip_get()
    if t == SENTINEL:
        t = ""                  # 复制失败
    d = os.path.dirname(outfile)
    if d and not os.path.isdir(d):
        os.makedirs(d)
    with open(outfile, "w", encoding="utf-8", newline="\n") as f:
        f.write(t)
    name, title = fg_info()
    print("LEN=%d | TITLE=%s | %s -> %s" % (len(t), title, tag, outfile))
    return len(t)


def main():
    cmd = sys.argv[1]
    if cmd == "title":
        name, title = fg_info()
        print("PROC=%s | TITLE=%s" % (name, title))
        return
    if cmd == "close":
        key("ctrl", "w", after=0.8)
        name, title = fg_info()
        print("CLOSED | now TITLE=%s" % title)
        return
    if cmd == "scroll":
        n = int(sys.argv[2])
        for _ in range(n):
            key("pagedown", after=0.6)
        print("SCROLLED %d" % n)
        return
    if cmd == "grab":
        out = sys.argv[2]
        wait = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0
        capture(out, wait, tag="regrab")
        return
    if cmd == "nav":
        url, out = sys.argv[2], sys.argv[3]
        wait = float(sys.argv[4]) if len(sys.argv) > 4 else 6.0
        require_quark()
        key("ctrl", "t", after=1.0)
        key("ctrl", "l", after=0.5)
        type_text(url)
        time.sleep(0.4)
        key("enter", after=1.0)
        capture(out, wait, tag=url)
        return
    raise SystemExit("unknown cmd %s" % cmd)


if __name__ == "__main__":
    main()
