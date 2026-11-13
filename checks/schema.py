"""
checks/schema.py - Nhóm 3: Dữ liệu cấu trúc (15 điểm)
"""

from typing import Any, Dict

ALLOWED_TYPES = {
    "organization",
    "website",
    "article",
    "product",
    "localbusiness",
    "breadcrumblist",
}


def check_schema_present(data: Dict[str, Any]) -> Dict[str, Any]:
    schema_blocks = data.get("details", {}).get("schema", [])
    count = len(schema_blocks)

    if count >= 1:
        return {
            "status": "pass",
            "value": f"Có {count} khối JSON-LD",
        }
    return {
        "status": "fail",
        "value": "Không tìm thấy dữ liệu cấu trúc Schema (JSON-LD)",
    }


def check_schema_valid(data: Dict[str, Any]) -> Dict[str, Any]:
    schema_blocks = data.get("details", {}).get("schema", [])
    if not schema_blocks:
        return {
            "status": "fail",
            "value": "Không có khối Schema nào để kiểm tra tính hợp lệ",
        }

    invalid_blocks = [b for b in schema_blocks if not b.get("valid", False)]
    if not invalid_blocks:
        return {
            "status": "pass",
            "value": f"Tất cả {len(schema_blocks)} khối JSON-LD đều hợp lệ",
        }

    err_msgs = []
    for b in invalid_blocks:
        err_msgs.extend(b.get("errors", ["Không hợp lệ"]))

    return {
        "status": "fail",
        "value": f"Có {len(invalid_blocks)} khối lỗi: {'; '.join(err_msgs[:2])}",
    }


def check_schema_type(data: Dict[str, Any]) -> Dict[str, Any]:
    schema_blocks = data.get("details", {}).get("schema", [])
    if not schema_blocks:
        return {
            "status": "fail",
            "value": "Không có Schema nào",
        }

    found_types = set()
    for b in schema_blocks:
        for t in b.get("types", []):
            found_types.add(t.strip().lower())

    matching = [t for t in found_types if t in ALLOWED_TYPES]
    if matching:
        return {
            "status": "pass",
            "value": f"Loại schema phù hợp: {', '.join(matching)}",
        }

    all_found_str = ", ".join(found_types) if found_types else "không xác định"
    return {
        "status": "warn",
        "value": f"Loại hiện tại ({all_found_str}) chưa thuộc các loại phổ biến (Organization, WebSite, Article, Product...)",
    }
