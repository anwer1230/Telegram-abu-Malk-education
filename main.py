"""Entry point - runs the Abu_Malk-Services app."""
import os
import sys
import subprocess
import signal
import logging

# التأكد التلقائي من توفر الحزم الأساسية لمنع أي عطل عند إعادة تشغيل البيئة
try:
    import requests
    import flask
    import flask_socketio
except ImportError:
    print("⏳ جارٍ تهيئة وتثبيت حزم بايثون الأساسية تلقائياً...")
    try:
        subprocess.run(["pip", "install", "--break-system-packages", "-r", "requirements.txt"], check=True)
    except Exception:
        subprocess.run(["sh", "-c", "curl -sS https://bootstrap.pypa.io/get-pip.py | python3 - --break-system-packages && pip install --break-system-packages -r requirements.txt"], check=True)

from config import IS_RENDER, resolve_app_port
from app import app, socketio

def free_port(port):
    """تحرير المنفذ إذا كان مشغولاً بإنهاء أي عملية سابقة"""
    try:
        if IS_RENDER:
            return
            
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        result = s.connect_ex(('127.0.0.1', port))
        s.close()
        if result == 0:
            import os, signal, time
            my_pid = os.getpid()
            parent_pid = os.getppid()
            for pid_dir in os.listdir('/proc'):
                if not pid_dir.isdigit():
                    continue
                pid = int(pid_dir)
                if pid == my_pid or pid == parent_pid:
                    continue
                try:
                    with open(f'/proc/{pid}/cmdline', 'rb') as f:
                        cmd = f.read().replace(b'\x00', b' ').decode('utf-8', 'ignore')
                    if 'python' in cmd and 'main.py' in cmd:
                        try:
                            os.kill(pid, signal.SIGKILL)
                        except ProcessLookupError:
                            pass
                except Exception:
                    pass
            time.sleep(0.5)
    except Exception:
        pass

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    port = resolve_app_port()
    if IS_RENDER:
        print(f"🌐 تشغيل Abu_Malk-Services على المنفذ {port} في بيئة Render")
        socketio.run(app, host='0.0.0.0', port=port, allow_unsafe_werkzeug=True)
    else:
        free_port(port)
        print(f"🌐 تشغيل Abu_Malk-Services على المنفذ {port}")
        socketio.run(app, host='0.0.0.0', port=port, debug=False, allow_unsafe_werkzeug=True)
