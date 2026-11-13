"""
ai/service.py - Bộ điều phối gọi AI trung tâm, kiểm tra an toàn và xử lý chuẩn hoá kết quả.
"""

import time
import unicodedata
from typing import Any, Dict, List, Optional

from ai.guard import censor_key, is_allowed_base_url
from ai.json_extract import extract_json_block
from ai.prompts.explain_fix import build_explain_fix_prompt
from ai.prompts.rewrite_meta import build_rewrite_meta_prompt
from ai.providers.anthropic_provider import call_anthropic
from ai.providers.openai_compat import call_openai_compat
from ai.settings import load_providers_config, resolve_api_key


def _count_nfc_chars(s: str) -> int:
    """Đếm số ký tự sau khi chuẩn hoá Unicode NFC."""
    if not s:
        return 0
    norm = unicodedata.normalize("NFC", s)
    return len(norm)


def _resolve_endpoint_and_type(
    provider_id: str,
    custom_base_url: Optional[str],
    local_mode: bool = False,
) -> Dict[str, Any]:
    """Tìm thông tin endpoint và kiểm tra base_url hợp lệ."""
    cfg = load_providers_config()
    providers = cfg.get("providers", [])
    allowed_hosts = cfg.get("allowed_hosts", [])

    info = next((p for p in providers if p["id"] == provider_id), None)
    if not info:
        raise ValueError(f"Nhà cung cấp AI '{provider_id}' không được hỗ trợ.")

    ptype = info.get("type", "openai_compat")
    endpoint = (custom_base_url or "").strip() or info.get("default_endpoint", "")

    # Kiểm tra SSRF
    if not is_allowed_base_url(endpoint, allowed_hosts, local_mode=local_mode):
        raise PermissionError(f"Endpoint AI '{endpoint}' không nằm trong danh sách được phép.")

    default_model = info.get("default_model", "")
    return {
        "type": ptype,
        "endpoint": endpoint,
        "default_model": default_model,
    }


def call_ai_text(
    provider_id: str,
    api_key: Optional[str],
    model: Optional[str],
    base_url: Optional[str],
    system_prompt: str,
    user_prompt: str,
    local_mode: bool = False,
    timeout: int = 60,
    max_tokens: int = 1500,
) -> str:
    """Điều phối gọi API tới nhà cung cấp tương ứng."""
    key = resolve_api_key(api_key, provider_id, local_mode=local_mode)
    if not key:
        raise PermissionError("Chưa có key AI. Mở Cài đặt AI để nhập key của bạn.")

    endpoint_info = _resolve_endpoint_and_type(provider_id, base_url, local_mode=local_mode)
    ptype = endpoint_info["type"]
    endpoint = endpoint_info["endpoint"]
    target_model = (model or "").strip() or endpoint_info["default_model"]

    if ptype == "anthropic":
        return call_anthropic(
            api_key=key,
            endpoint=endpoint,
            model=target_model,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            timeout=timeout,
            max_tokens=max_tokens,
        )
    else:
        return call_openai_compat(
            api_key=key,
            endpoint=endpoint,
            model=target_model,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            timeout=timeout,
            max_tokens=max_tokens,
        )


def test_ai_connection(
    provider_id: str,
    api_key: Optional[str],
    model: Optional[str] = None,
    base_url: Optional[str] = None,
    local_mode: bool = False,
) -> Dict[str, Any]:
    """Thử nghiệm kết nối tới nhà cung cấp AI."""
    start_time = time.time()
    system_prompt = "Bạn là trợ lý kiểm tra kết nối. Hãy trả lời JSON: {\"status\": \"ok\"}"
    user_prompt = "Kiểm tra kết nối."

    resp_text = call_ai_text(
        provider_id=provider_id,
        api_key=api_key,
        model=model,
        base_url=base_url,
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        local_mode=local_mode,
        timeout=30,
        max_tokens=50,
    )

    latency_ms = int((time.time() - start_time) * 1000)
    data = extract_json_block(resp_text)
    return {
        "ok": True,
        "latency_ms": latency_ms,
        "data": data,
    }


def service_rewrite_meta(
    provider_id: str,
    api_key: Optional[str],
    model: Optional[str],
    base_url: Optional[str],
    page_data: Dict[str, Any],
    keyword: Optional[str] = None,
    style: Optional[str] = None,
    brand: Optional[str] = None,
    local_mode: bool = False,
) -> Dict[str, Any]:
    """Tính năng F11: Gợi ý viết lại Title và Meta Description."""
    prompts = build_rewrite_meta_prompt(
        page_data=page_data,
        keyword=keyword,
        style=style,
        brand=brand,
    )

    raw_resp = call_ai_text(
        provider_id=provider_id,
        api_key=api_key,
        model=model,
        base_url=base_url,
        system_prompt=prompts["system_prompt"],
        user_prompt=prompts["user_prompt"],
        local_mode=local_mode,
        timeout=60,
        max_tokens=1500,
    )

    parsed = extract_json_block(raw_resp)

    # Chuẩn hoá danh sách titles
    raw_titles = parsed.get("titles", [])
    clean_titles = []
    for t in raw_titles[:3]:
        text = str(t.get("text", "")).strip()
        chars = _count_nfc_chars(text)
        clean_titles.append({
            "text": text,
            "chars": chars,
            "in_range": chars <= 60,
            "angle": str(t.get("angle", "curiosity_gap")),
            "why": str(t.get("why", "")).strip(),
        })

    # Chuẩn hoá danh sách descriptions
    raw_descs = parsed.get("descriptions", [])
    clean_descs = []
    for d in raw_descs[:3]:
        text = str(d.get("text", "")).strip()
        chars = _count_nfc_chars(text)
        clean_descs.append({
            "text": text,
            "chars": chars,
            "in_range": (70 <= chars <= 160),
            "angle": str(d.get("angle", "curiosity_gap")),
            "why": str(d.get("why", "")).strip(),
        })

    return {
        "summary": str(parsed.get("summary", "")).strip(),
        "titles": clean_titles,
        "descriptions": clean_descs,
        "provider": provider_id,
        "model": model or "default",
    }


def service_explain_fixes(
    provider_id: str,
    api_key: Optional[str],
    model: Optional[str],
    base_url: Optional[str],
    url: str,
    lang: str,
    cms: str,
    items: List[Dict[str, Any]],
    local_mode: bool = False,
) -> Dict[str, Any]:
    """Tính năng F12: Giải thích lỗi theo ngữ cảnh trang."""
    requested_ids = {it.get("id") for it in items if it.get("id")}

    prompts = build_explain_fix_prompt(
        url=url,
        lang=lang,
        cms=cms,
        items=items,
    )

    raw_resp = call_ai_text(
        provider_id=provider_id,
        api_key=api_key,
        model=model,
        base_url=base_url,
        system_prompt=prompts["system_prompt"],
        user_prompt=prompts["user_prompt"],
        local_mode=local_mode,
        timeout=60,
        max_tokens=1500,
    )

    parsed = extract_json_block(raw_resp)
    raw_items = parsed.get("items", [])

    # Chỉ giữ các id được yêu cầu (loại bỏ id thừa mà AI tự ý sinh ra)
    result_by_id: Dict[str, Dict[str, Any]] = {}
    for it in raw_items:
        cid = it.get("id")
        if cid in requested_ids:
            example_str = str(it.get("example", "")).strip()
            if len(example_str) > 400:
                example_str = example_str[:400] + "..."

            result_by_id[cid] = {
                "id": cid,
                "fix": str(it.get("fix", "")).strip(),
                "example": example_str,
            }

    # Bổ sung thông báo nếu có id bị thiếu
    final_items = []
    for req_id in requested_ids:
        if req_id in result_by_id:
            final_items.append(result_by_id[req_id])
        else:
            final_items.append({
                "id": req_id,
                "fix": "Chưa có giải thích cho mục này.",
                "example": "",
            })

    return {"items": final_items}
