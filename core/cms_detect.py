"""
core/cms_detect.py - Nhận diện nền tảng website (WordPress, Shopify, Wix, Webflow, Haravan, Sapo)
từ mã nguồn HTML và headers.
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional

_SIG_FILE = Path(__file__).resolve().parent.parent / "config" / "cms_signatures.json"
_SIGNATURES: Dict[str, Any] = {}

if _SIG_FILE.is_file():
    try:
        with open(_SIG_FILE, "r", encoding="utf-8") as f:
            _SIGNATURES = json.load(f)
    except Exception:
        pass


def detect_cms(html: str, headers: Optional[Dict[str, str]] = None) -> str:
    """
    Nhận diện CMS của trang web. Trả về tên hiển thị hoặc 'unknown'.
    """
    if not html:
        return "unknown"

    html_lower = html.lower()
    headers_str = ""
    if headers:
        headers_str = " ".join(f"{k}: {v}" for k, v in headers.items()).lower()

    combined = f"{headers_str}\n{html_lower}"

    for cms_id, info in _SIGNATURES.items():
        patterns = info.get("patterns", [])
        for pattern in patterns:
            if pattern.lower() in combined:
                return info.get("name", cms_id.capitalize())

    return "unknown"
