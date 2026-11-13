"""
web/routes_ai.py - Các HTTP API liên quan tới AI (F10, F11, F12).
- Key truyền qua header X-AI-Key, không lưu lại máy chủ.
- Chặn SSRF, kiểm tra payload tối đa (12 KB), rate limit riêng biệt.
"""

import os
from typing import Any, Dict
from flask import Blueprint, jsonify, request

from ai.guard import censor_key
from ai.service import (
    service_explain_fixes,
    service_rewrite_meta,
    test_ai_connection,
)
from web.ratelimit import limiter
from web.security import get_client_ip

routes_ai = Blueprint("routes_ai", __name__)


def _is_local_mode() -> bool:
    return os.environ.get("LOCAL_MODE", "0").lower() in ("1", "true", "yes")


def _get_api_key_from_header() -> str:
    key = request.headers.get("X-AI-Key", "")
    return key.strip() if key else ""


def _handle_ai_error(e: Exception, api_key: str):
    safe_msg = censor_key(str(e), api_key)
    if "Chưa có key AI" in safe_msg:
        status_code = 400
    elif any(w in safe_msg for w in ("401", "403", "hết hạn", "Invalid authentication", "Key không đúng")):
        status_code = 401
    elif "429" in safe_msg or "quá giới hạn" in safe_msg:
        status_code = 429
    elif "quá lâu" in safe_msg or "timeout" in safe_msg.lower():
        status_code = 504
    else:
        status_code = 502
    return jsonify({"error": safe_msg}), status_code


@routes_ai.before_request
def check_payload_size():
    """Kiểm tra giới hạn dung lượng payload (AI_MAX_PAYLOAD_KB = 12 KB)."""
    max_kb = int(os.environ.get("AI_MAX_PAYLOAD_KB", "12"))
    content_len = request.content_length
    if content_len and content_len > max_kb * 1024:
        return jsonify({"error": f"Dữ liệu gửi lên AI vượt quá dung lượng cho phép ({max_kb} KB)."}), 400


@routes_ai.route("/api/ai/test", methods=["POST"])
def route_ai_test():
    """POST /api/ai/test - Thử kết nối tới nhà cung cấp AI."""
    ip = get_client_ip(request)
    allowed, err_msg, _ = limiter.check_ai_limit(ip)
    if not allowed:
        return jsonify({"error": err_msg}), 429

    acquired, slot_err = limiter.acquire_ai_slot()
    if not acquired:
        return jsonify({"error": slot_err}), 429

    api_key = _get_api_key_from_header()
    body = request.get_json(silent=True) or {}
    provider_id = body.get("provider", "openai")
    model = body.get("model")
    base_url = body.get("base_url")

    try:
        res = test_ai_connection(
            provider_id=provider_id,
            api_key=api_key,
            model=model,
            base_url=base_url,
            local_mode=_is_local_mode(),
        )
        limiter.increment_ai_count(ip)
        return jsonify(res)
    except Exception as e:
        return _handle_ai_error(e, api_key)
    finally:
        limiter.release_ai_slot()


@routes_ai.route("/api/ai/rewrite_meta", methods=["POST"])
def route_ai_rewrite_meta():
    """POST /api/ai/rewrite_meta - Gợi ý viết lại Title và Meta Description."""
    ip = get_client_ip(request)
    allowed, err_msg, _ = limiter.check_ai_limit(ip)
    if not allowed:
        return jsonify({"error": err_msg}), 429

    acquired, slot_err = limiter.acquire_ai_slot()
    if not acquired:
        return jsonify({"error": slot_err}), 429

    api_key = _get_api_key_from_header()
    body = request.get_json(silent=True) or {}
    provider_id = body.get("provider", "openai")
    model = body.get("model")
    base_url = body.get("base_url")
    page_data = body.get("page") or {}
    keyword = body.get("keyword")
    style = body.get("style")
    brand = body.get("brand")

    try:
        res = service_rewrite_meta(
            provider_id=provider_id,
            api_key=api_key,
            model=model,
            base_url=base_url,
            page_data=page_data,
            keyword=keyword,
            style=style,
            brand=brand,
            local_mode=_is_local_mode(),
        )
        limiter.increment_ai_count(ip)
        return jsonify(res)
    except Exception as e:
        return _handle_ai_error(e, api_key)
    finally:
        limiter.release_ai_slot()


@routes_ai.route("/api/ai/explain", methods=["POST"])
def route_ai_explain():
    """POST /api/ai/explain - Giải thích lỗi theo ngữ cảnh trang."""
    ip = get_client_ip(request)
    allowed, err_msg, _ = limiter.check_ai_limit(ip)
    if not allowed:
        return jsonify({"error": err_msg}), 429

    acquired, slot_err = limiter.acquire_ai_slot()
    if not acquired:
        return jsonify({"error": slot_err}), 429

    api_key = _get_api_key_from_header()
    body = request.get_json(silent=True) or {}
    provider_id = body.get("provider", "openai")
    model = body.get("model")
    base_url = body.get("base_url")
    url = body.get("url", "")
    lang = body.get("lang", "vi")
    cms = body.get("cms", "unknown")
    items = body.get("items") or []

    try:
        res = service_explain_fixes(
            provider_id=provider_id,
            api_key=api_key,
            model=model,
            base_url=base_url,
            url=url,
            lang=lang,
            cms=cms,
            items=items,
            local_mode=_is_local_mode(),
        )
        limiter.increment_ai_count(ip)
        return jsonify(res)
    except Exception as e:
        return _handle_ai_error(e, api_key)
    finally:
        limiter.release_ai_slot()
