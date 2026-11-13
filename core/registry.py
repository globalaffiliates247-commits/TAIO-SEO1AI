"""
core/registry.py - Danh mục định nghĩa toàn bộ 24 luật kiểm tra SEO và trọng số.
Để thêm 1 luật mới: chỉ cần thêm hàm trong checks/<nhóm>.py + 1 dòng tại REGISTRY + 1 mục trong vi.json.
"""

from typing import Any, Callable, Dict, List

from checks.content import (
    check_content_alt,
    check_content_description,
    check_content_h1,
    check_content_headings,
    check_content_links,
    check_content_og,
    check_content_title,
    check_content_words,
)
from checks.schema import (
    check_schema_present,
    check_schema_type,
    check_schema_valid,
)
from checks.speed import (
    check_speed_cls,
    check_speed_inp,
    check_speed_lcp,
    check_speed_score,
)
from checks.technical import (
    check_tech_canonical,
    check_tech_https,
    check_tech_lang,
    check_tech_noindex,
    check_tech_redirects,
    check_tech_robots,
    check_tech_sitemap,
    check_tech_status,
    check_tech_viewport,
)

GROUPS = {
    "technical": {"id": "technical", "weight": 30, "name_key": "group_technical"},
    "content": {"id": "content", "weight": 30, "name_key": "group_content"},
    "schema": {"id": "schema", "weight": 15, "name_key": "group_schema"},
    "speed": {"id": "speed", "weight": 25, "name_key": "group_speed"},
}

REGISTRY: List[Dict[str, Any]] = [
    # Nhóm 1 - Kỹ thuật (30 điểm)
    {"id": "tech_https", "group": "technical", "weight": 4, "fn": check_tech_https},
    {"id": "tech_status", "group": "technical", "weight": 4, "fn": check_tech_status},
    {"id": "tech_redirects", "group": "technical", "weight": 3, "fn": check_tech_redirects},
    {"id": "tech_robots", "group": "technical", "weight": 4, "fn": check_tech_robots},
    {"id": "tech_noindex", "group": "technical", "weight": 4, "fn": check_tech_noindex},
    {"id": "tech_sitemap", "group": "technical", "weight": 3, "fn": check_tech_sitemap},
    {"id": "tech_canonical", "group": "technical", "weight": 4, "fn": check_tech_canonical},
    {"id": "tech_viewport", "group": "technical", "weight": 2, "fn": check_tech_viewport},
    {"id": "tech_lang", "group": "technical", "weight": 2, "fn": check_tech_lang},

    # Nhóm 2 - Nội dung cơ bản (30 điểm)
    {"id": "content_title", "group": "content", "weight": 5, "fn": check_content_title},
    {"id": "content_description", "group": "content", "weight": 4, "fn": check_content_description},
    {"id": "content_h1", "group": "content", "weight": 5, "fn": check_content_h1},
    {"id": "content_headings", "group": "content", "weight": 3, "fn": check_content_headings},
    {"id": "content_words", "group": "content", "weight": 4, "fn": check_content_words},
    {"id": "content_alt", "group": "content", "weight": 4, "fn": check_content_alt},
    {"id": "content_links", "group": "content", "weight": 2, "fn": check_content_links},
    {"id": "content_og", "group": "content", "weight": 3, "fn": check_content_og},

    # Nhóm 3 - Dữ liệu cấu trúc (15 điểm)
    {"id": "schema_present", "group": "schema", "weight": 5, "fn": check_schema_present},
    {"id": "schema_valid", "group": "schema", "weight": 5, "fn": check_schema_valid},
    {"id": "schema_type", "group": "schema", "weight": 5, "fn": check_schema_type},

    # Nhóm 4 - Tốc độ (25 điểm)
    {"id": "speed_score", "group": "speed", "weight": 10, "fn": check_speed_score},
    {"id": "speed_lcp", "group": "speed", "weight": 6, "fn": check_speed_lcp},
    {"id": "speed_inp", "group": "speed", "weight": 5, "fn": check_speed_inp},
    {"id": "speed_cls", "group": "speed", "weight": 4, "fn": check_speed_cls},
]


def run_checks(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Chạy tất cả các luật trong registry trên dữ liệu đã thu thập.
    """
    results: List[Dict[str, Any]] = []
    for item in REGISTRY:
        check_id = item["id"]
        group = item["group"]
        weight = item["weight"]
        fn: Callable[[Dict[str, Any]], Dict[str, Any]] = item["fn"]

        try:
            res = fn(data)
        except Exception as e:
            res = {
                "status": "warn",
                "value": f"Lỗi thực thi luật kiểm tra: {e}",
            }

        results.append({
            "id": check_id,
            "group": group,
            "weight": weight,
            "status": res.get("status", "na"),
            "value": res.get("value", ""),
            "note": res.get("note"),
        })

    return results
