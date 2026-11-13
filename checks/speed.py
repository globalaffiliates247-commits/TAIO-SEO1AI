"""
checks/speed.py - Nhóm 4: Tốc độ trang (25 điểm)
"""

from typing import Any, Dict


def check_speed_score(data: Dict[str, Any]) -> Dict[str, Any]:
    pagespeed = data.get("pagespeed", {})
    if not pagespeed or not pagespeed.get("success", False):
        return {
            "status": "na",
            "value": "Không đo được (PageSpeed không khả dụng hoặc quá hạn)",
        }

    score = pagespeed.get("performance_score")
    if score is None:
        return {
            "status": "na",
            "value": "Không đo được",
        }

    if score >= 90:
        status = "pass"
    elif score >= 50:
        status = "warn"
    else:
        status = "fail"

    return {
        "status": status,
        "value": f"{score}/100",
    }


def check_speed_lcp(data: Dict[str, Any]) -> Dict[str, Any]:
    pagespeed = data.get("pagespeed", {})
    if not pagespeed or not pagespeed.get("success", False):
        return {
            "status": "na",
            "value": "Không đo được",
        }

    # lcp_seconds
    lcp = pagespeed.get("lcp_seconds")
    if lcp is None:
        return {
            "status": "na",
            "value": "Không có dữ liệu LCP",
        }

    if lcp <= 2.5:
        status = "pass"
    elif lcp <= 4.0:
        status = "warn"
    else:
        status = "fail"

    return {
        "status": status,
        "value": f"{lcp:.2f} giây",
    }


def check_speed_inp(data: Dict[str, Any]) -> Dict[str, Any]:
    pagespeed = data.get("pagespeed", {})
    if not pagespeed or not pagespeed.get("success", False):
        return {
            "status": "na",
            "value": "Không đo được",
        }

    # inp_ms (field data). Nếu không có dữ liệu thực tế -> 'na'
    inp = pagespeed.get("inp_ms")
    if inp is None:
        return {
            "status": "na",
            "value": "Chưa có dữ liệu người dùng thực tế (CrUX)",
        }

    if inp <= 200:
        status = "pass"
    elif inp <= 500:
        status = "warn"
    else:
        status = "fail"

    return {
        "status": status,
        "value": f"{inp} ms",
    }


def check_speed_cls(data: Dict[str, Any]) -> Dict[str, Any]:
    pagespeed = data.get("pagespeed", {})
    if not pagespeed or not pagespeed.get("success", False):
        return {
            "status": "na",
            "value": "Không đo được",
        }

    cls = pagespeed.get("cls")
    if cls is None:
        return {
            "status": "na",
            "value": "Không có dữ liệu CLS",
        }

    if cls <= 0.1:
        status = "pass"
    elif cls <= 0.25:
        status = "warn"
    else:
        status = "fail"

    return {
        "status": status,
        "value": f"{cls:.3f}",
    }
