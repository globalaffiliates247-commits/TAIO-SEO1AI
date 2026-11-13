"""
core/url_tools.py - Tiện ích xử lý URL, chuẩn hoá, loại bỏ tham số theo dõi và phân loại liên kết.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from urllib.parse import parse_qsl, urlencode, urljoin, urlparse, urlunparse

# Tải danh sách tham số theo dõi từ core/tracking_params.json
_TRACKING_FILE = Path(__file__).parent / "tracking_params.json"
_EXACT_TRACKING: Set[str] = set()
_PREFIX_TRACKING: Tuple[str, ...] = ("utm_",)

if _TRACKING_FILE.is_file():
    try:
        with open(_TRACKING_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            _EXACT_TRACKING = set(data.get("exact_names", []))
            _PREFIX_TRACKING = tuple(data.get("prefixes", ["utm_"]))
    except Exception:
        pass


def is_tracking_param(param_name: str) -> bool:
    """Kiểm tra xem tên tham số truy vấn có phải là tham số theo dõi quảng cáo không."""
    low = param_name.lower()
    if low in _EXACT_TRACKING:
        return True
    for prefix in _PREFIX_TRACKING:
        if low.startswith(prefix.lower()):
            return True
    return False


def strip_tracking_params(url: str) -> Tuple[str, bool]:
    """
    Loại bỏ các tham số theo dõi khỏi URL.
    Trả về (url_sạch, co_tham_so_theo_doi_hay_khong).
    """
    if not url:
        return "", False

    parsed = urlparse(url)
    if not parsed.query:
        return url, False

    query_params = parse_qsl(parsed.query, keep_blank_values=True)
    clean_params = []
    has_tracking = False

    for k, v in query_params:
        if is_tracking_param(k):
            has_tracking = True
        else:
            clean_params.append((k, v))

    clean_query = urlencode(clean_params)
    clean_url = urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        clean_query,
        parsed.fragment,
    ))
    return clean_url, has_tracking


def normalize_domain(domain: str) -> str:
    """Chuẩn hoá tên miền: chữ thường, bỏ tiền tố 'www.' và cổng mặc định nếu có."""
    dom = (domain or "").lower().strip()
    if ":" in dom:
        host, port = dom.split(":", 1)
        if port in ("80", "443"):
            dom = host
    if dom.startswith("www."):
        dom = dom[4:]
    return dom


def normalize_url(url: str, strip_tracking: bool = True) -> str:
    """
    Chuẩn hoá URL phục vụ so sánh:
    - Bỏ khoảng trắng
    - Hạ chữ thường domain
    - Bỏ fragment (#...)
    - Bỏ tham số theo dõi (nếu strip_tracking=True)
    - Chuẩn hoá dấu gạch chéo cuối path (bỏ trailing slash nếu không phải trang gốc '/')
    """
    if not url:
        return ""

    url = url.strip()
    if strip_tracking:
        url, _ = strip_tracking_params(url)

    parsed = urlparse(url)
    netloc = normalize_domain(parsed.netloc)
    path = parsed.path or "/"

    # Chuẩn hoá dấu gạch chéo cuối
    if len(path) > 1 and path.endswith("/"):
        path = path.rstrip("/")

    # Sắp xếp query params để so sánh nhất quán
    query_parts = parse_qsl(parsed.query, keep_blank_values=True)
    query_parts.sort(key=lambda x: x[0])
    sorted_query = urlencode(query_parts)

    return urlunparse((
        parsed.scheme.lower(),
        netloc,
        path,
        parsed.params,
        sorted_query,
        "",  # luôn bỏ fragment
    ))


def same_domain(url1: str, url2: str) -> bool:
    """So sánh xem 2 URL có cùng tên miền không (bỏ qua 'www.' và chữ hoa/thường)."""
    p1 = urlparse(url1)
    p2 = urlparse(url2)
    return normalize_domain(p1.netloc) == normalize_domain(p2.netloc)


def resolve_absolute_url(base_url: str, link: str) -> str:
    """Chuyển link tương đối thành tuyệt đối dựa vào base_url."""
    if not link:
        return ""
    link = link.strip()
    return urljoin(base_url, link)


def classify_link(base_url: str, raw_href: str) -> Tuple[str, str]:
    """
    Phân loại liên kết:
    Trả về (loại, url_đích):
    - ('internal', abs_url)
    - ('external', abs_url)
    - ('mailto', raw_href)
    - ('tel', raw_href)
    - ('javascript', raw_href)
    - ('hash', raw_href)
    - ('other', raw_href)
    """
    href = (raw_href or "").strip()
    if not href:
        return "other", ""

    lower = href.lower()
    if lower.startswith("mailto:"):
        return "mailto", href
    if lower.startswith("tel:"):
        return "tel", href
    if lower.startswith("javascript:"):
        return "javascript", href
    if href.startswith("#"):
        return "hash", href

    abs_url = resolve_absolute_url(base_url, href)
    parsed = urlparse(abs_url)

    if parsed.scheme in ("http", "https"):
        if same_domain(base_url, abs_url):
            return "internal", abs_url
        return "external", abs_url

    return "other", href
