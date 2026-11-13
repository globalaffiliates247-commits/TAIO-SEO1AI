"""
ai/settings.py - Cấu hình nhà cung cấp AI và chính sách xử lý khoá bí mật.
Chế độ host (LOCAL_MODE=0): bỏ qua mọi biến môi trường chứa API key của máy chủ.
Chế độ máy (LOCAL_MODE=1): cho phép đọc key từ biến môi trường hoặc config/settings.json.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

_PROVIDERS_FILE = Path(__file__).resolve().parent.parent / "config" / "providers.json"
_LOCAL_SETTINGS_FILE = Path(__file__).resolve().parent.parent / "config" / "settings.json"


def load_providers_config() -> Dict[str, Any]:
    """Tải cấu hình providers từ file JSON."""
    if _PROVIDERS_FILE.is_file():
        try:
            with open(_PROVIDERS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"providers": [], "allowed_hosts": []}


def get_public_providers(local_mode: bool = False) -> List[Dict[str, Any]]:
    """
    Trả về danh sách các nhà cung cấp hiển thị trên giao diện người dùng.
    Không để lộ API key hay thông tin bảo mật máy chủ.
    """
    cfg = load_providers_config()
    providers = cfg.get("providers", [])

    public_list = []
    for p in providers:
        if p.get("local_only") and not local_mode:
            continue

        public_list.append({
            "id": p["id"],
            "type": p.get("type", "openai_compat"),
            "label": p["label"],
            "default_model": p.get("default_model", ""),
            "base_url_editable": p.get("base_url_editable", False),
        })

    return public_list


def resolve_api_key(
    client_key: Optional[str],
    provider_id: str,
    local_mode: bool = False,
) -> Optional[str]:
    """
    Xác định API key được sử dụng:
    - Nếu người dùng truyền qua header X-AI-Key: luôn ưu tiên dùng client_key.
    - Ở chế độ Host (local_mode = False): BẮT BUỘC phải có client_key, không bao giờ dùng key máy chủ.
    - Ở chế độ máy cá nhân (local_mode = True): nếu client_key trống, cho phép lấy từ biến môi trường hoặc config/settings.json.
    """
    if client_key and client_key.strip():
        return client_key.strip()

    if not local_mode:
        return None

    # Tìm thông tin provider
    cfg = load_providers_config()
    provider_info = next((p for p in cfg.get("providers", []) if p["id"] == provider_id), None)
    if not provider_info:
        return None

    env_var = provider_info.get("env_key")
    if env_var and os.environ.get(env_var):
        return os.environ.get(env_var, "").strip()

    # Kiểm tra settings.json cục bộ
    if _LOCAL_SETTINGS_FILE.is_file():
        try:
            with open(_LOCAL_SETTINGS_FILE, "r", encoding="utf-8") as f:
                sdata = json.load(f)
                keys = sdata.get("api_keys", {})
                if provider_id in keys:
                    return str(keys[provider_id]).strip()
        except Exception:
            pass

    return None
