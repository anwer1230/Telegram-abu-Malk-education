"""Entry point - runs the Abu_Malk-Services app."""
import os
import sys
import subprocess
import signal
import logging

# التأكد السريع من توفر الحزم الأساسية فقط دون حجب بدء التشغيل
def _ensure_core_packages():
    import importlib.util
    required = {
        "requests": "requests",
        "flask": "Flask",
        "flask_socketio": "Flask-SocketIO",
        "pptx": "python-pptx",
        "PIL": "Pillow",
        "bs4": "beautifulsoup4",
        "lxml": "lxml",
    }
    missing = [pkg for mod, pkg in required.items() if importlib.util.find_spec(mod) is None]
    if not missing:
        return
    print(f"⏳ جارٍ تثبيت الحزم الناقصة: {', '.join(missing)} ...", flush=True)
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "--break-system-packages", "--no-cache-dir", "-q", *missing],
            check=True,
        )
    except Exception:
        subprocess.run(
            ["sh", "-c", "curl -sS https://bootstrap.pypa.io/get-pip.py | python3 - --break-system-packages && python3 -m pip install --break-system-packages -q " + " ".join(missing)],
            check=True,
        )


_ensure_core_packages()

from config import IS_RENDER, resolve_app_port
from app import app, socketio


def _pids_listening_on_port(port: int) -> list[int]:
    """قراءة /proc/net/tcp لإيجاد جميع العمليات التي تشغل المنفذ المطلوب بدقة"""
    target_hex = f"{int(port):04X}"
    inodes = set()
    for tcp_file in ("/proc/net/tcp", "/proc/net/tcp6"):
        if not os.path.exists(tcp_file):
            continue
        try:
            with open(tcp_file, "r", encoding="utf-8", errors="ignore") as f:
                for line in f.read().splitlines()[1:]:
                    parts = line.split()
                    if len(parts) >= 10 and parts[3] == "0A":  # TCP_LISTEN
                        local_addr = parts[1]
                        if ":" in local_addr and local_addr.rsplit(":", 1)[1].upper() == target_hex:
                            inodes.add(parts[9])
        except Exception:
            pass

    pids = set()
    my_pid = os.getpid()
    parent_pid = os.getppid()
    for pid_dir in os.listdir("/proc"):
        if not pid_dir.isdigit():
            continue
        pid = int(pid_dir)
        if pid in (my_pid, parent_pid):
            continue
        matched = False
        if inodes:
            fd_dir = f"/proc/{pid}/fd"
            try:
                for fd_name in os.listdir(fd_dir):
                    try:
                        link = os.readlink(os.path.join(fd_dir, fd_name))
                        if link.startswith("socket:[") and link[8:-1] in inodes:
                            matched = True
                            break
                    except Exception:
                        pass
            except Exception:
                pass
        if not matched:
            try:
                with open(f"/proc/{pid}/cmdline", "rb") as f:
                    cmd = f.read().replace(b"\x00", b" ").decode("utf-8", "ignore")
                if "python" in cmd and "main.py" in cmd:
                    matched = True
            except Exception:
                pass
        if matched:
            pids.add(pid)
    return sorted(pids)


def _is_port_open(port: int) -> bool:
    import socket
    for host in ("127.0.0.1", "0.0.0.0"):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.3)
                if s.connect_ex(("127.0.0.1" if host == "0.0.0.0" else host, port)) == 0:
                    return True
        except Exception:
            pass
    return False


def free_port(port):
    """تحرير المنفذ إذا كان مشغولاً بإنهاء أي عملية سابقة والانتظار حتى يتفرغ فعلياً"""
    try:
        if IS_RENDER:
            return
        import time
        pids = _pids_listening_on_port(port)
        if not pids and not _is_port_open(port):
            return
        for sig in (signal.SIGTERM, signal.SIGKILL):
            pids = _pids_listening_on_port(port)
            for pid in pids:
                try:
                    os.kill(pid, sig)
                except ProcessLookupError:
                    pass
                except Exception:
                    pass
            deadline = time.time() + (1.5 if sig == signal.SIGTERM else 3.5)
            while time.time() < deadline:
                if not _is_port_open(port):
                    return
                time.sleep(0.15)
    except Exception:
        pass


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    port = resolve_app_port()
    if IS_RENDER:
        print(f"🌐 تشغيل Abu_Malk-Services على المنفذ {port} في بيئة Render", flush=True)
        socketio.run(app, host='0.0.0.0', port=port, debug=False, use_reloader=False, allow_unsafe_werkzeug=True)
    else:
        free_port(port)
        print(f"🌐 تشغيل Abu_Malk-Services على المنفذ {port}", flush=True)
        socketio.run(app, host='0.0.0.0', port=port, debug=False, use_reloader=False, allow_unsafe_werkzeug=True)
