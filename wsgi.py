"""
wsgi.py - Điểm vào chuẩn WSGI cho Gunicorn khi triển khai máy chủ (Render / Docker).
Tự động đặt LOCAL_MODE=0 để áp dụng các chính sách bảo mật máy chủ nghiêm ngặt:
- Chống SSRF: chỉ cho phép HTTPS và whitelist endpoint AI
- Không chia sẻ key AI của máy chủ cho người dùng
"""

import os
import sys
from pathlib import Path

# Đặt cờ máy chủ host
os.environ["LOCAL_MODE"] = "0"

# Đảm bảo đường dẫn gốc có trong sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from web.server import create_app

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8770"))
    app.run(host="0.0.0.0", port=port, debug=False)
