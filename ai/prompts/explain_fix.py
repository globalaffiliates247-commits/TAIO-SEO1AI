"""
ai/prompts/explain_fix.py - Dựng prompt cho tính năng giải thích lỗi theo ngữ cảnh trang (F12).
"""

import json
from typing import Any, Dict, List
from ai.guard import generate_delimiter_tokens, wrap_page_data
from ai.prompts.common import build_system_prompt


def build_explain_fix_prompt(
    url: str,
    lang: str,
    cms: str,
    items: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Tạo prompt giải thích chi tiết cho các mục lỗi cần sửa.
    """
    start_tag, end_tag = generate_delimiter_tokens()

    task_instructions = f"""
NHIỆM VỤ CỦA BẠN:
Giải thích cách sửa chữa cụ thể, sát với ngữ cảnh thực tế của website cho các hạng mục SEO được yêu cầu.

THÔNG TIN TRANG WEB:
- URL: {url}
- Nền tảng CMS nhận diện: {cms}
- Ngôn ngữ: {lang}

RÀNG BUỘC KỸ THUẬT:
1. CHỈ giải thích đúng các mục có trong danh sách yêu cầu. Tuyệt đối KHÔNG tự ý thêm các id khác.
2. Hướng dẫn sửa chữa (trường 'fix') phải sát với website đang phân tích: nhắc lại giá trị thực tế đang có và đề xuất đổi thành giá trị gì.
3. Nếu nền tảng CMS là '{cms}' (khác 'unknown'), đưa ra gợi ý liên quan đến CMS đó nhưng KHÔNG bịa đường dẫn menu hay tên nút nếu không chắc chắn (hãy nói chung: 'trong phần chỉnh sửa SEO của trang').
4. Ví dụ mẫu (trường 'example') phải ngắn gọn, súc tích (dưới 400 ký tự) như thẻ HTML hoặc đoạn văn mẫu.

CẤU TRÚC JSON ĐẦU RA BẮT BUỘC:
{{
  "items": [
    {{
      "id": "tên_id_chính_xác",
      "fix": "Hướng dẫn sửa chi tiết...",
      "example": "Đoạn code hoặc câu mẫu..."
    }}
  ]
}}
"""

    system_prompt = build_system_prompt(start_tag, end_tag, task_instructions, lang=lang)

    items_summary = []
    for it in items[:5]:  # Tối đa 5 mục
        items_summary.append({
            "id": it.get("id"),
            "status": it.get("status"),
            "value_found": it.get("value"),
            "expected": it.get("expected"),
            "excerpt": it.get("excerpt"),
        })

    items_json_str = json.dumps(items_summary, ensure_ascii=False, indent=2)
    wrapped_data = wrap_page_data(items_json_str, start_tag, end_tag)

    user_prompt = f"""Dưới đây là danh sách các lỗi SEO cần được giải thích cho website:
{wrapped_data}

Hãy trả về JSON theo đúng định dạng được hướng dẫn."""

    return {
        "system_prompt": system_prompt,
        "user_prompt": user_prompt,
    }
