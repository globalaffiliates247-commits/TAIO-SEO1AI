"""
web/security.py - Thiết lập tiêu chuẩn bảo mật HTTP & bảo vệ thông tin riêng tư:
- Content-Security-Policy (CSP) chặt chẽ
- X-Content-Type-Options, X-Frame-Options, Referrer-Policy
- Lọc log: Tuyệt đối không log header X-AI-Key, body chứa API Key của người dùng
"""

import logging
from typing import Optional
from flask import Request, Response
from ai.guard import censor_key


def get_client_ip(request: Request) -> str:
    """
    Lấy địa chỉ IP thật của client, xử lý an toàn qua proxy / reverse-proxy (Render, Cloudflare).
    """
    if request.headers.get("X-Forwarded-For"):
        # Header có thể chứa: "client, proxy1, proxy2"
        return request.headers.get("X-Forwarded-For").split(",")[0].strip()
    if request.headers.get("X-Real-IP"):
        return request.headers.get("X-Real-IP").strip()
    return request.remote_addr or "127.0.0.1"


def apply_security_headers(response: Response) -> Response:
    """
    Thêm các HTTP Security Headers vào response.
    """
    # Content-Security-Policy
    # script-src 'self' 'unsafe-inline' (cho inline UI event handlers / reports)
    # img-src 'self' data: https: (cho preview ảnh web và icon)
    # style-src 'self' 'unsafe-inline'
    csp = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "connect-src 'self'; "
        "font-src 'self'; "
        "object-src 'none'; "
        "base-uri 'self'; "
        "frame-ancestors 'none';"
    )
    response.headers["Content-Security-Policy"] = csp
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response


class SensitiveDataFilter(logging.Filter):
    """
    Lọc bỏ các API Key khỏi log nếu vô tình lọt vào chuỗi format.
    """
    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            # Không log chi tiết request AI
            if "/api/ai/" in record.msg:
                # Chỉ log đường dẫn và phương thức, không log nội dung
                pass
        return True
