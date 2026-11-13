"""
ai/guard.py - Bảo vệ an toàn cho kết nối AI:
- Che giấu API key trong log và thông báo lỗi
- Kiểm tra danh sách trắng base_url (chống SSRF)
- Tạo khối ngăn cách dữ liệu với mã token ngẫu nhiên chống chèn lệnh (Prompt Injection)
"""

import ipaddress
import secrets
import string
from typing import List, Tuple
from urllib.parse import urlparse


def censor_key(text: str, api_key: str) -> str:
    """Che giấu chuỗi API key nếu xuất hiện trong văn bản hoặc thông báo lỗi."""
    if not text or not api_key:
        return text or ""
    clean_k = api_key.strip()
    if len(clean_k) < 6:
        return text.replace(clean_k, "***KEY***")
    return text.replace(clean_k, f"***KEY_{clean_k[:4]}...***")


def is_allowed_base_url(url: str, allowed_hosts: List[str], local_mode: bool = False) -> bool:
    """
    Kiểm tra xem base_url có được phép gọi hay không (chống SSRF).
    - Ở chế độ máy cá nhân (local_mode = True): cho phép URL tuỳ ý, kể cả localhost/127.0.0.1.
    - Ở chế độ máy chủ host (local_mode = False): chỉ cho phép HTTPS và host thuộc allowed_hosts.
      Từ chối tuyệt đối localhost, 127.0.0.1, 169.254.169.254 và dải IP riêng tư.
    """
    if not url:
        return False

    parsed = urlparse(url)
    scheme = parsed.scheme.lower()
    hostname = (parsed.hostname or "").lower()

    if local_mode:
        return scheme in ("http", "https") and bool(hostname)

    # Chế độ Host: chỉ HTTPS
    if scheme != "https":
        return False

    if not hostname:
        return False

    # Kiểm tra nếu hostname là IP
    try:
        ip_obj = ipaddress.ip_address(hostname)
        if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_reserved or ip_obj.is_link_local:
            return False
    except ValueError:
        pass

    # Chặn rõ ràng localhost
    if hostname == "localhost" or hostname.endswith(".local") or hostname.endswith(".internal"):
        return False

    # Phải nằm trong danh sách trắng allowed_hosts
    for allowed in allowed_hosts:
        if hostname == allowed.lower() or hostname.endswith(f".{allowed.lower()}"):
            return True

    return False


def generate_delimiter_tokens() -> Tuple[str, str]:
    """Tạo cặp thẻ ngăn cách ngẫu nhiên cho mỗi lượt gọi AI."""
    rand_suffix = "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))
    start_tag = f"<<<PAGE_DATA_{rand_suffix}>>>"
    end_tag = f"<<<END_{rand_suffix}>>>"
    return start_tag, end_tag


def wrap_page_data(content: str, start_tag: str, end_tag: str) -> str:
    """Bọc dữ liệu trang vào khối ngăn cách."""
    return f"{start_tag}\n{content}\n{end_tag}"
