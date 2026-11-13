"""
core/score.py - Tính điểm nhóm, điểm chung 0-100 và xếp hạng màu sắc theo quy tắc cố định.
Quy tắc:
- pass = 100% trọng số, warn = 50%, fail = 0%, na = loại khỏi mẫu số.
- Điểm nhóm = tổng điểm đạt / tổng trọng số của các luật không na (thang 0-100).
- Điểm chung = trung bình có trọng số của 4 nhóm (30/30/15/25). Nếu nhóm không đo được -> chia lại tỉ lệ.
- Màu: 90-100 xanh 'Tốt', 50-89 cam 'Cần cải thiện', 0-49 đỏ 'Yếu'.
"""

from typing import Any, Dict, List, Tuple
from core.registry import GROUPS


def calculate_group_scores(checks: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    Tính điểm cho từng nhóm:
    Trả về dict: { group_id: { score, status, total_weight, achieved_points, measurable } }
    """
    group_data: Dict[str, Dict[str, Any]] = {
        gid: {
            "id": gid,
            "achieved": 0.0,
            "weight": 0.0,
            "all_na": True,
        }
        for gid in GROUPS
    }

    for c in checks:
        gid = c.get("group")
        if gid not in group_data:
            continue

        status = c.get("status", "na")
        weight = float(c.get("weight", 0))

        if status == "na":
            continue

        group_data[gid]["all_na"] = False
        group_data[gid]["weight"] += weight

        if status == "pass":
            group_data[gid]["achieved"] += weight
        elif status == "warn":
            group_data[gid]["achieved"] += weight * 0.5
        elif status == "fail":
            pass

    results: Dict[str, Dict[str, Any]] = {}
    for gid, ginfo in GROUPS.items():
        data = group_data[gid]
        if data["all_na"] or data["weight"] <= 0:
            results[gid] = {
                "id": gid,
                "score": None,
                "status": "unmeasurable",
                "label": "Không đo được",
                "color": "gray",
            }
        else:
            pct = (data["achieved"] / data["weight"]) * 100.0
            score_int = round(pct)
            band, label, color = get_band(score_int)
            results[gid] = {
                "id": gid,
                "score": score_int,
                "status": band,
                "label": label,
                "color": color,
            }

    return results


def get_band(score: int) -> Tuple[str, str, str]:
    """Trả về (band, nhãn tiếng Việt, mã màu): 'good' | 'needs_improvement' | 'poor'."""
    if score >= 90:
        return "good", "Tốt", "green"
    elif score >= 50:
        return "needs_improvement", "Cần cải thiện", "orange"
    else:
        return "poor", "Yếu", "red"


def calculate_overall_score(group_scores: Dict[str, Dict[str, Any]]) -> Tuple[int, str, str, str]:
    """
    Tính điểm chung trên thang 0-100 dựa vào trọng số 4 nhóm: 30 / 30 / 15 / 25.
    Nếu có nhóm không đo được -> loại khỏi mẫu số và tái phân bổ trọng số cho các nhóm còn lại.
    Trả về (score, band, label, color).
    """
    total_valid_weight = 0.0
    weighted_sum = 0.0

    for gid, gdef in GROUPS.items():
        g_res = group_scores.get(gid, {})
        g_score = g_res.get("score")
        if g_score is not None:
            w = float(gdef["weight"])
            total_valid_weight += w
            weighted_sum += (g_score * w)

    if total_valid_weight <= 0:
        return 0, "poor", "Không thể chấm điểm", "gray"

    final_score = round(weighted_sum / total_valid_weight)
    band, label, color = get_band(final_score)
    return final_score, band, label, color
