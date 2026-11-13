"""
ai/json_extract.py - Trích xuất dữ liệu JSON an toàn từ phản hồi của mô hình ngôn ngữ lớn (LLM).
Hỗ trợ phản hồi bọc trong khối markdown ```json ... ``` hoặc có văn bản thừa xung quanh.
"""

import json
import re
from typing import Any, Dict


def extract_json_block(text: str) -> Dict[str, Any]:
    """
    Trích xuất khối JSON đầu tiên từ chuỗi phản hồi của AI.
    Trả về dict parsed được hoặc ném ValueError.
    """
    if not text:
        raise ValueError("AI trả về phản hồi rỗng.")

    clean_text = text.strip()

    # 1. Thử phân tích trực tiếp
    try:
        data = json.loads(clean_text)
        if isinstance(data, dict):
            return data
    except Exception:
        pass

    # 2. Tìm khối markdown ```json ... ``` hoặc ``` ... ```
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", clean_text, re.IGNORECASE)
    if match:
        snippet = match.group(1).strip()
        try:
            data = json.loads(snippet)
            if isinstance(data, dict):
                return data
        except Exception:
            pass

    # 3. Tìm cặp dấu ngoặc nhọn ngoài cùng đầu tiên { ... }
    first_brace = clean_text.find("{")
    last_brace = clean_text.rfind("}")

    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        snippet = clean_text[first_brace : last_brace + 1]
        try:
            data = json.loads(snippet)
            if isinstance(data, dict):
                return data
        except Exception:
            pass

    raise ValueError("AI trả về định dạng không đọc được. Bấm thử lại.")
