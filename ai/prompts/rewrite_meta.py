"""
ai/prompts/rewrite_meta.py - Dựng prompt cho tính năng gợi ý viết lại Title và Meta Description (F11).
"""

from typing import Any, Dict, Optional
from ai.guard import generate_delimiter_tokens, wrap_page_data
from ai.prompts.common import build_system_prompt


def build_rewrite_meta_prompt(
    page_data: Dict[str, Any],
    keyword: Optional[str] = None,
    style: Optional[str] = None,
    brand: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Tạo system_prompt và user_prompt cho việc viết lại Title & Meta Description.
    """
    start_tag, end_tag = generate_delimiter_tokens()
    lang = page_data.get("lang") or "vi"

    task_instructions = """
NHIỆM VỤ CỦA BẠN:
Đề xuất ĐÚNG 3 Tiêu đề (Title) và ĐÚNG 3 Đoạn mô tả (Meta Description) tối ưu chuẩn SEO cho trang web.

YÊU CẦU ĐẶC TẢ KỸ THUẬT:
1. Độ dài:
   - Mỗi Title: Tối đa 60 ký tự. Không được vượt quá 60 ký tự.
   - Mỗi Meta Description: Nằm trong khoảng 70 đến 160 ký tự.
2. Góc tiếp cận (angle): Mỗi gợi ý phải dùng 1 góc khác nhau trong danh sách sau:
   - 'curiosity_gap' (Tạo khoảng trống tò mò dựa trên sự thật)
   - 'number' (Quy trình, con số, bước thực hiện có trong nội dung)
   - 'contrast' (Đối chiếu trước/sau, vấn đề/giải pháp)
   - 'question' (Câu hỏi đánh trúng nỗi đau khách hàng)
   - 'stakes' (Rủi ro nếu bỏ qua hoặc lợi ích lớn đạt được)
3. Chân thực tuyệt đối:
   - KHÔNG bịa đặt số liệu, giải thưởng, cam kết nếu không có trong dữ liệu trang.
   - Không nhồi nhét từ khoá; câu văn tự nhiên, thuyết phục.
4. Mỗi gợi ý kèm 1 câu 'why' giải thích lý do viết như vậy.

CẤU TRÚC JSON ĐẦU RA BẮT BUỘC:
{
  "summary": "Tóm tắt ngắn gọn 1 câu về chủ đề trang",
  "titles": [
    {"text": "Tiêu đề 1", "angle": "curiosity_gap", "why": "Lý do"},
    {"text": "Tiêu đề 2", "angle": "number", "why": "Lý do"},
    {"text": "Tiêu đề 3", "angle": "question", "why": "Lý do"}
  ],
  "descriptions": [
    {"text": "Mô tả 1 (70-160 ký tự)", "angle": "curiosity_gap", "why": "Lý do"},
    {"text": "Mô tả 2 (70-160 ký tự)", "angle": "number", "why": "Lý do"},
    {"text": "Mô tả 3 (70-160 ký tự)", "angle": "stakes", "why": "Lý do"}
  ]
}
"""

    system_prompt = build_system_prompt(start_tag, end_tag, task_instructions, lang=lang)

    # Dựng nội dung trang đưa vào user prompt
    page_content_str = f"""URL: {page_data.get('url', '')}
Tiêu đề hiện tại: {page_data.get('title', '')}
Meta description hiện tại: {page_data.get('description', '')}
Thẻ H1: {page_data.get('h1', '')}
Các đề mục chính: {', '.join(page_data.get('headings', []))}
Đoạn trích nội dung trang:
{page_data.get('text_excerpt', '')[:2500]}
"""

    wrapped_content = wrap_page_data(page_content_str, start_tag, end_tag)

    user_instructions = []
    if keyword and keyword.strip():
        user_instructions.append(f"- Từ khoá trọng tâm: '{keyword.strip()}'")
    if brand and brand.strip():
        user_instructions.append(f"- Tên thương hiệu nên xuất hiện: '{brand.strip()}'")
    if style and style.strip():
        style_map = {
            "ban_hang": "Thương mại, tập trung lợi ích bán hàng",
            "thong_tin": "Cung cấp thông tin, kiến thức chuyên sâu",
            "dich_vu": "Dịch vụ chuyên nghiệp, giải pháp",
            "tin_tuc": "Tin tức thời sự, cập nhật",
        }
        user_instructions.append(f"- Phong cách giọng điệu: {style_map.get(style, style)}")

    options_text = "\n".join(user_instructions) if user_instructions else "Không có yêu cầu tuỳ chọn bổ sung."

    user_prompt = f"""Dưới đây là dữ liệu của trang web được phân tích:
{wrapped_content}

Yêu cầu tuỳ chọn của người dùng:
{options_text}

Hãy tạo 3 Title và 3 Meta Description theo đúng cấu trúc JSON yêu cầu."""

    return {
        "system_prompt": system_prompt,
        "user_prompt": user_prompt,
    }
