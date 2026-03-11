import webview
import os
import platform
import threading
from app.api import Api

api  = Api()

BASE_DIR  = os.path.dirname(os.path.abspath(__file__))

# ── Icon path: .ico for Windows, .icns for macOS ──────────────────────
if platform.system() == "Darwin":
    ICON_PATH = os.path.join(BASE_DIR, "visara-logo.icns")
else:
    ICON_PATH = os.path.join(BASE_DIR, "visara-logo.ico")


def set_window_icon(window):
    # Windows-only: use Win32 API to set icon
    # On macOS this is handled by pywebview natively via the .icns file
    if platform.system() != "Windows":
        return
    try:
        import ctypes
        WM_SETICON      = 0x0080
        ICON_SMALL      = 0
        ICON_BIG        = 1
        LR_LOADFROMFILE = 0x0010

        user32 = ctypes.windll.user32

        hicon_small = user32.LoadImageW(None, ICON_PATH, 1, 16, 16, LR_LOADFROMFILE)
        hicon_big   = user32.LoadImageW(None, ICON_PATH, 1, 48, 48, LR_LOADFROMFILE)

        if hicon_small == 0 or hicon_big == 0:
            return

        hwnd = user32.FindWindowW(None, "Visara")
        if hwnd == 0:
            hwnd = user32.GetForegroundWindow()
        if hwnd == 0:
            return

        user32.SendMessageW(hwnd, WM_SETICON, ICON_SMALL, hicon_small)
        user32.SendMessageW(hwnd, WM_SETICON, ICON_BIG,   hicon_big)
        user32.SetClassLongPtrW(hwnd, -14, hicon_big)  # GCL_HICON = -14

    except Exception as e:
        print(f"[icon] ❌ Exception: {e}")


def on_loaded():
    threading.Timer(1.5, lambda: set_window_icon(window)).start()


window = webview.create_window(
    "Visara",
    "http://localhost:4200/",
    js_api=api
)

# Hook into the page-loaded event so the Win32 handle exists by the time we run
window.events.loaded += on_loaded

# ── GUI engine: edgechromium is Windows-only; macOS uses WebKit automatically ──
if platform.system() == "Windows":
    webview.start(
        gui="edgechromium",
        debug=True,
        http_server=True,
        private_mode=False,
        args=["--allow-file-access-from-files", "--disable-web-security"]
    )
else:
    # macOS: do NOT pass gui= or args= — pywebview uses native WebKit
    webview.start(
        debug=True,
        http_server=True,
        private_mode=False,
    )