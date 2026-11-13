"""
core/top_fixes.py - Lựa chọn 5 việc cần sửa ngay theo nguyên lý Pareto 80/20.
Sắp xếp theo: fail trước, warn sau; cùng trạng thái thì sắp theo trọng số giảm dần.
"""

from typing import Any, Dict, List


def select_top_fixes(checks: List[Dict[str, Any]], max_items: int = 5) -> List[str]:
    """
    Trả về danh sách check_id của tối đa 5 việc cần khắc phục nhất.
    """
    candidates = [c for c in checks if c.get("status") in ("fail", "warn")]

    # Sắp xếp: fail (0) ưu tiên hơn warn (1), sau đó trọng số giảm dần (-weight)
    def _sort_key(c: Dict[str, Any]):
        status_prio = 0 if c.get("status") == "fail" else 1
        weight = float(c.get("weight", 0))
        return (status_prio, -weight)

    candidates.sort(key=_sort_key)
    top = [c["id"] for c in candidates[:max_items]]
    return top
