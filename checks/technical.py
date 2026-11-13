"""
checks/technical.py - Nhóm 1: Kiểm tra Kỹ thuật (30 điểm)
"""

from typing import Any, Dict
from core.url_tools import normalize_url


def check_tech_https(data: Dict[str, Any]) -> Dict[str, Any]:
    final_url = data.get("final_url", "")
    is_https = final_url.lower().startswith("https://")
    ssl_cert_issue = data.get("ssl_cert_issue", False)

    if not is_https:
        return {
            "status": "fail",
            "value": "HTTP (không an toàn, thiếu mã hoá SSL)",
        }

    if ssl_cert_issue:
        return {
            "status": "warn",
            "value": "HTTPS (chứng chỉ SSL thiếu chứng chỉ trung gian hoặc lỗi xác thực)",
            "note": "Cần cấu hình đầy đủ chuỗi chứng chỉ SSL fullchain.",
        }

    return {
        "status": "pass",
        "value": "HTTPS",
    }


def check_tech_status(data: Dict[str, Any]) -> Dict[str, Any]:
    status_code = data.get("status_code", 0)
    return {
        "status": "pass" if status_code == 200 else "fail",
        "value": status_code,
    }


def check_tech_redirects(data: Dict[str, Any]) -> Dict[str, Any]:
    redirects = data.get("redirect_chain", [])
    count = len(redirects)
    # redirect_chain có thể chứa URL ban đầu, số lần chuyển hướng = len - 1 nếu > 0
    redirect_count = count - 1 if count > 0 else 0
    if redirect_count < 0:
        redirect_count = 0

    if redirect_count <= 1:
        status = "pass"
    elif redirect_count <= 3:
        status = "warn"
    else:
        status = "fail"

    return {
        "status": status,
        "value": f"{redirect_count} lần chuyển hướng",
    }


def check_tech_robots(data: Dict[str, Any]) -> Dict[str, Any]:
    robots_data = data.get("robots", {})
    exists = robots_data.get("exists", False)
    blocked = robots_data.get("blocked", False)

    if not exists:
        return {
            "status": "warn",
            "value": "Không tìm thấy file robots.txt",
        }
    if blocked:
        return {
            "status": "fail",
            "value": "robots.txt chặn thu thập URL này",
        }
    return {
        "status": "pass",
        "value": "robots.txt hợp lệ và cho phép truy cập",
    }


def check_tech_noindex(data: Dict[str, Any]) -> Dict[str, Any]:
    details = data.get("details", {}).get("overview", {})
    meta_robots = (details.get("robots_meta") or "").lower()
    x_robots = (details.get("x_robots_header") or "").lower()

    reasons = []
    if "noindex" in meta_robots:
        reasons.append("meta robots chứa noindex")
    if "noindex" in x_robots:
        reasons.append("header X-Robots-Tag chứa noindex")

    if reasons:
        return {
            "status": "fail",
            "value": ", ".join(reasons),
        }
    return {
        "status": "pass",
        "value": "Không bị chặn index (indexable)",
    }


def check_tech_sitemap(data: Dict[str, Any]) -> Dict[str, Any]:
    sitemap_data = data.get("sitemap", {})
    found = sitemap_data.get("found", False)
    count = sitemap_data.get("url_count", 0)

    if found:
        return {
            "status": "pass",
            "value": f"Có sitemap ({count} URL)",
        }
    return {
        "status": "warn",
        "value": "Không tìm thấy sitemap.xml",
    }


def check_tech_canonical(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Quy tắc tech_canonical F3:
    1. Chuẩn hoá cả URL cuối cùng và canonical: hạ chữ thường, bỏ fragment, bỏ trailing slash, bỏ tham số theo dõi.
    2. pass: có đúng 1 canonical hợp lệ và sau chuẩn hoá trùng với chính trang này.
       Nếu URL gốc có tham số theo dõi, kèm ghi chú.
    3. warn: canonical trỏ sang URL khác, hoặc có nhiều hơn 1 thẻ.
    4. fail: thiếu canonical hoặc URL trong canonical không hợp lệ.
    """
    details = data.get("details", {}).get("overview", {})
    canon_info = details.get("canonical", {})
    count = canon_info.get("count", 0)
    href = canon_info.get("href", "")
    had_tracking = details.get("url", {}).get("had_tracking", False)
    final_url = data.get("final_url", "")

    if count == 0:
        return {
            "status": "fail",
            "value": "Thiếu thẻ canonical",
        }
    if count > 1:
        return {
            "status": "warn",
            "value": f"Có {count} thẻ canonical",
            "note": "Hãy kiểm tra đây có phải chủ đích không.",
        }
    if not href:
        return {
            "status": "fail",
            "value": "Thẻ canonical có href rỗng",
        }

    norm_final = normalize_url(final_url, strip_tracking=True)
    norm_canon = normalize_url(href, strip_tracking=True)

    if norm_final == norm_canon:
        note = None
        if had_tracking:
            note = "Link có tham số quảng cáo; canonical trỏ về trang gốc là bình thường, không cần sửa."
        return {
            "status": "pass",
            "value": "Trỏ về chính trang này (tự tham chiếu)",
            "note": note,
        }
    else:
        return {
            "status": "warn",
            "value": f"Canonical trỏ sang: {href}",
            "note": "Hãy kiểm tra đây có phải chủ đích không.",
        }


def check_tech_viewport(data: Dict[str, Any]) -> Dict[str, Any]:
    details = data.get("details", {}).get("overview", {})
    viewport = details.get("viewport", "")
    if viewport:
        return {
            "status": "pass",
            "value": viewport,
        }
    return {
        "status": "fail",
        "value": "Thiếu thẻ meta viewport cho di động",
    }


def check_tech_lang(data: Dict[str, Any]) -> Dict[str, Any]:
    details = data.get("details", {}).get("overview", {})
    lang = details.get("lang", "")
    if lang:
        return {
            "status": "pass",
            "value": lang,
        }
    return {
        "status": "warn",
        "value": "Thiếu thuộc tính lang trên thẻ <html>",
    }
