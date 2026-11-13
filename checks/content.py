"""
checks/content.py - Nhóm 2: Nội dung cơ bản (30 điểm)
"""

from typing import Any, Dict


def check_content_title(data: Dict[str, Any]) -> Dict[str, Any]:
    details = data.get("details", {}).get("overview", {})
    t_info = details.get("title", {})
    text = t_info.get("text", "")
    length = t_info.get("length", len(text))

    if not text:
        return {
            "status": "fail",
            "value": "Thiếu thẻ tiêu đề (title)",
        }
    if 30 <= length <= 60:
        return {
            "status": "pass",
            "value": f"{length} ký tự (đạt chuẩn 30–60)",
        }
    return {
        "status": "warn",
        "value": f"{length} ký tự ({'ngắn hơn' if length < 30 else 'dài hơn'} khuyến nghị 30–60)",
    }


def check_content_description(data: Dict[str, Any]) -> Dict[str, Any]:
    details = data.get("details", {}).get("overview", {})
    d_info = details.get("description", {})
    text = d_info.get("text", "")
    length = d_info.get("length", len(text))

    if not text:
        return {
            "status": "fail",
            "value": "Thiếu meta description",
        }
    if 70 <= length <= 160:
        return {
            "status": "pass",
            "value": f"{length} ký tự (đạt chuẩn 70–160)",
        }
    return {
        "status": "warn",
        "value": f"{length} ký tự ({'ngắn hơn' if length < 70 else 'dài hơn'} khuyến nghị 70–160)",
    }


def check_content_h1(data: Dict[str, Any]) -> Dict[str, Any]:
    details = data.get("details", {}).get("headings", [])
    h1_list = [h for h in details if h.get("level") == 1]
    count = len(h1_list)

    if count == 1:
        return {
            "status": "pass",
            "value": f"1 thẻ: {h1_list[0].get('text', '')[:60]}",
        }
    elif count == 0:
        return {
            "status": "fail",
            "value": "Không có thẻ H1 nào",
        }
    else:
        return {
            "status": "fail",
            "value": f"Có {count} thẻ H1 (quá nhiều)",
        }


def check_content_headings(data: Dict[str, Any]) -> Dict[str, Any]:
    details = data.get("details", {}).get("headings", [])
    h2_count = sum(1 for h in details if h.get("level") == 2)

    if h2_count >= 1:
        return {
            "status": "pass",
            "value": f"Có {h2_count} thẻ H2",
        }
    return {
        "status": "warn",
        "value": "Thiếu thẻ H2 phân đoạn nội dung",
    }


def check_content_words(data: Dict[str, Any]) -> Dict[str, Any]:
    details = data.get("details", {}).get("overview", {})
    words = details.get("word_count", 0)

    if words >= 300:
        return {
            "status": "pass",
            "value": f"{words} từ",
        }
    elif words >= 100:
        return {
            "status": "warn",
            "value": f"{words} từ (ít hơn 300 từ)",
        }
    else:
        return {
            "status": "fail",
            "value": f"{words} từ (quá mỏng)",
        }


def check_content_alt(data: Dict[str, Any]) -> Dict[str, Any]:
    images = data.get("details", {}).get("images", [])
    total = len(images)
    if total == 0:
        return {
            "status": "pass",
            "value": "Trang không có hình ảnh",
        }

    with_alt = sum(1 for img in images if img.get("alt_status") == "ok")
    rate = with_alt / total

    val_str = f"{with_alt}/{total} ảnh có mô tả ({rate*100:.0f}%)"
    if rate >= 0.8:
        return {
            "status": "pass",
            "value": val_str,
        }
    elif rate >= 0.5:
        return {
            "status": "warn",
            "value": val_str,
        }
    else:
        return {
            "status": "fail",
            "value": val_str,
        }


def check_content_links(data: Dict[str, Any]) -> Dict[str, Any]:
    links = data.get("details", {}).get("links", {})
    internal_list = links.get("internal", [])
    count = len(internal_list)

    if count >= 3:
        return {
            "status": "pass",
            "value": f"Có {count} liên kết nội bộ",
        }
    elif count >= 1:
        return {
            "status": "warn",
            "value": f"Chỉ có {count} liên kết nội bộ",
        }
    else:
        return {
            "status": "fail",
            "value": "Không có liên kết nội bộ nào",
        }


def check_content_og(data: Dict[str, Any]) -> Dict[str, Any]:
    social = data.get("details", {}).get("social", {})
    og = social.get("open_graph", {})
    missing = social.get("missing", [])

    if not missing:
        return {
            "status": "pass",
            "value": "Đầy đủ og:title, og:description, og:image",
        }
    elif len(missing) < 3:
        return {
            "status": "warn",
            "value": f"Thiếu: {', '.join(missing)}",
        }
    else:
        return {
            "status": "fail",
            "value": "Thiếu toàn bộ thẻ Open Graph cơ bản",
        }
