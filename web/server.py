"""
web/server.py - Máy chủ Web Flask chính cho TAIO SEO Check.
- Cung cấp giao diện web và các API kiểm tra SEO (/api/check, /api/config, /healthz).
- Tích hợp bảo mật, giới hạn lượt dùng, tách bạch AI.
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from flask import Flask, jsonify, request, send_from_directory

from core.collect import collect_all_data, normalize_input_url
from core.extract_details import extract_details
from core.registry import GROUPS, run_checks
from core.score import calculate_group_scores, calculate_overall_score
from core.top_fixes import select_top_fixes
from web.ratelimit import limiter
from web.routes_ai import routes_ai
from web.security import apply_security_headers, get_client_ip

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "web" / "static"
MESSAGES_FILE = BASE_DIR / "messages" / "vi.json"
VERSION_FILE = BASE_DIR / "version.json"
PROVIDERS_FILE = BASE_DIR / "config" / "providers.json"


def load_json_file(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def create_app() -> Flask:
    app = Flask(__name__, static_folder=str(STATIC_DIR), static_url_path="/static")
    app.config["JSON_AS_ASCII"] = False

    # Đăng ký Blueprint AI
    app.register_blueprint(routes_ai)

    # Đăng ký middleware bảo mật
    @app.after_request
    def security_headers(response):
        return apply_security_headers(response)

    @app.route("/")
    def index():
        return send_from_directory(str(STATIC_DIR), "index.html")

    @app.route("/healthz")
    def healthz():
        return "ok", 200, {"Content-Type": "text/plain; charset=utf-8"}

    @app.route("/api/config", methods=["GET"])
    def get_config():
        ip = get_client_ip(request)
        limits = limiter.get_remaining(ip)
        version_data = load_json_file(VERSION_FILE)
        providers_data = load_json_file(PROVIDERS_FILE)

        daily_limit = int(os.environ.get("DAILY_LIMIT", "5"))
        ai_daily_limit = int(os.environ.get("AI_DAILY_LIMIT", "20"))
        local_mode = os.environ.get("LOCAL_MODE", "0").lower() in ("1", "true", "yes")

        # Rút gọn thông tin providers gửi về client
        client_providers = []
        for p in providers_data.get("providers", []):
            client_providers.append({
                "id": p["id"],
                "label": p["label"],
                "default_model": p.get("default_model", ""),
                "base_url_editable": p.get("base_url_editable", False),
                "default_endpoint": p.get("default_endpoint", ""),
            })

        return jsonify({
            "version": version_data.get("version", "0.1.0"),
            "stamp": version_data.get("stamp", "14112600"),
            "daily_limit": daily_limit,
            "remaining": limits["seo_remaining"],
            "local_mode": local_mode,
            "ai": {
                "providers": client_providers,
                "daily_limit": ai_daily_limit,
                "remaining": limits["ai_remaining"],
            },
        })

    @app.route("/api/check", methods=["POST"])
    def check_seo():
        ip = get_client_ip(request)
        allowed, err_msg, _ = limiter.check_seo_limit(ip)
        if not allowed:
            return jsonify({"error": err_msg}), 429

        acquired, slot_err = limiter.acquire_seo_slot()
        if not acquired:
            return jsonify({"error": slot_err}), 429

        try:
            body = request.get_json(silent=True) or {}
            raw_url = body.get("url", "")
            if not raw_url:
                return jsonify({"error": "Vui lòng nhập đường link cần kiểm tra."}), 400

            fetch_timeout = int(os.environ.get("FETCH_TIMEOUT_SEC", "15"))
            psi_timeout = int(os.environ.get("PSI_TIMEOUT_SEC", "60"))
            pagespeed_key = os.environ.get("PAGESPEED_API_KEY")

            # 1. Thu thập dữ liệu
            data = collect_all_data(
                raw_input_url=raw_url,
                fetch_timeout=fetch_timeout,
                psi_timeout=psi_timeout,
                pagespeed_key=pagespeed_key,
            )

            # 2. Chiết xuất Soi chi tiết (F9)
            details, ai_context, notices = extract_details(
                raw_html=data["raw_html"],
                raw_url=data["raw_url"],
                final_url=data["final_url"],
                status_code=data["status_code"],
                headers=data["headers"],
            )
            data["details"] = details

            # 3. Chạy 24 luật kiểm tra
            checks = run_checks(data)

            # 4. Tính điểm nhóm & điểm chung
            group_scores = calculate_group_scores(checks)
            overall_score, overall_band, _, _ = calculate_overall_score(group_scores)

            # 5. Chọn 5 việc cần sửa ngay
            top_fixes = select_top_fixes(checks)

            # 6. Gán nhãn tiếng Việt từ messages/vi.json
            vi_msgs = load_json_file(MESSAGES_FILE)
            checks_i18n = vi_msgs.get("checks", {})
            groups_i18n = vi_msgs.get("groups", {})
            bands_i18n = vi_msgs.get("bands", {})

            # Làm giàu checks
            enriched_checks = []
            for c in checks:
                cid = c["id"]
                info = checks_i18n.get(cid, {})
                enriched_checks.append({
                    "id": cid,
                    "group": c["group"],
                    "status": c["status"],
                    "weight": c["weight"],
                    "value": c["value"],
                    "note": c.get("note"),
                    "name": info.get("name", cid),
                    "why": info.get("why", ""),
                    "fix": info.get("fix", ""),
                    "verify": info.get("verify", ""),
                })

            # Làm giàu groups
            enriched_groups = []
            for gid, gdata in group_scores.items():
                g_cfg = GROUPS.get(gid, {})
                gname = groups_i18n.get(g_cfg.get("name_key", ""), gid)
                enriched_groups.append({
                    "id": gid,
                    "name": gname,
                    "score": gdata["score"],
                    "status": gdata["status"],
                    "weight": g_cfg.get("weight", 0),
                })

            # Tăng số lượt đã dùng của IP
            limiter.increment_seo_count(ip)

            return jsonify({
                "url": data["validated_url"],
                "final_url": data["final_url"],
                "checked_at": datetime.now(timezone.utc).isoformat(),
                "score": overall_score,
                "band": overall_band,
                "band_label": bands_i18n.get(overall_band, overall_band),
                "groups": enriched_groups,
                "checks": enriched_checks,
                "top_fixes": top_fixes,
                "details": details,
                "ai_context": ai_context,
                "notices": notices,
            })

        except ValueError as ve:
            return jsonify({"error": str(ve)}), 400
        except RuntimeError as re:
            return jsonify({"error": str(re)}), 502
        except Exception as e:
            return jsonify({"error": f"Lỗi hệ thống trong quá trình kiểm tra: {e}"}), 500
        finally:
            limiter.release_seo_slot()

    return app


if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", "8770"))
    app.run(host="0.0.0.0", port=port, debug=False)
