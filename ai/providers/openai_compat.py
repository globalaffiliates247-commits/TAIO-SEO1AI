"""
ai/providers/openai_compat.py - Tích hợp các API theo chuẩn OpenAI Chat Completions:
(OpenAI, Google Gemini, OpenRouter, DeepSeek, Ollama, LM Studio).
"""

import json
from typing import Any, Dict
from ai.guard import censor_key
from ai.providers.http import post_json


def call_openai_compat(
    api_key: str,
    endpoint: str,
    model: str,
    system_prompt: str,
    user_prompt: str,
    timeout: int = 60,
    max_tokens: int = 1500,
) -> str:
    """Gọi OpenAI-compatible Chat Completions API và trả về chuỗi phản hồi thô."""
    headers = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    if "openrouter" in endpoint:
        headers["HTTP-Referer"] = "https://taio.club"
        headers["X-Title"] = "TAIO SEO Check"

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.5,
        "max_tokens": max_tokens,
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
        raise RuntimeError(f"API AI trả về lỗi {status}: {safe_body}")

    try:
        data = json.loads(resp_body)
        choices = data.get("choices", [])
        if choices and isinstance(choices, list):
            msg = choices[0].get("message", {})
            return msg.get("content", "")
        return ""
    except Exception as e:
        safe_msg = censor_key(str(e), api_key)
        raise RuntimeError(f"Không thể đọc phản hồi từ nhà cung cấp AI: {safe_msg}")
