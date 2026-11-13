#!/usr/bin/env python3
"""
app_web.py - Điểm khởi chạy giao diện web cục bộ trên máy cá nhân (macOS, Windows, Linux).
Mặc định truy cập: http://127.0.0.1:8770
Tự động đặt LOCAL_MODE=1 để cho phép đọc key từ biến môi trường và sử dụng Ollama/local endpoints.
"""

import os
import sys
import webbrowser
from pathlib import Path

# Đặt cờ chế độ máy cá nhân
os.environ["LOCAL_MODE"] = "1"

# Thêm thư mục gốc vào sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from web.server import create_app

app = create_app()

def main():
    host = os.getenv("HOST", "127.0.0.1").strip()
    port = int(os.getenv("PORT", "8770").strip())

    url = f"http://{host}:{port}"
    print("=" * 64)
    print("  TAIO SEO Check — Kiểm tra sức khoẻ SEO website toàn diện")
    print(f"  Đang khởi chạy tại: {url}")
    print("  Chế độ: Máy cá nhân (LOCAL_MODE=1)")
    print("  Nhấn Ctrl+C để dừng máy chủ.")
    print("=" * 64)

    if os.getenv("NO_BROWSER", "").lower() not in ("1", "true"):
        def _open():
            import time
            time.sleep(1.0)
            webbrowser.open(url)
        import threading
        threading.Thread(target=_open, daemon=True).start()

    app.run(host=host, port=port, debug=False)

if __name__ == "__main__":
    main()
