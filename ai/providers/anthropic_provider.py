"""
ai/providers/anthropic_provider.py - Tích hợp Anthropic Claude Messages API (văn bản thuần).
"""

import json
from typing import Any, Dict
from ai.guard import censor_key
from ai.providers.http import post_json


def call_anthropic(
    api_key: str,
    endpoint: str,
    model: str,
    system_prompt: str,
    user_prompt: str,
    timeout: int = 60,
    max_tokens: int = 1500,
) -> str:
    """Gọi Claude Messages API và trả về chuỗi phản hồi thô."""
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
    }

    payload = {
        "model": model,
        "max_tokens": max_tokens,
        "system": system_prompt,
        "messages": [
            {
                "role": "user",
                "content": user_prompt,
            }
        ],
    }

    try:
        status, resp_body = post_json(endpoint, headers, payload, timeout=timeout)
    except Exception as e:
        safe_msg = censor_key(str(e), api_key)
        raise RuntimeError(safe_msg)

    if status == 401 or status == 403:
        raise PermissionError("Key không đúng hoặc đã hết hạn.")
    if status == 429:
        raise RuntimeError("Nhà cung cấp AI báo quá giới hạn sử dụng. Thử lại sau.")
    if status != 200:
        safe_body = censor_key(resp_body, api_key)
        raise RuntimeError(f"Anthropic API trả về lỗi {status}: {safe_body}")

    try:
        data = json.loads(resp_body)
        content_items = data.get("content", [])
        if content_items and isinstance(content_items, list):
            return content_items[0].get("text", "")
        return ""
    except Exception as e:
        safe_msg = censor_key(str(e), api_key)
        raise RuntimeError(f"Không thể đọc phản hồi từ Claude: {safe_msg}")
