"""
core/collect.py - Thu thập dữ liệu từ 4 nguồn song song (HTML, robots.txt, sitemap, PageSpeed).
Giữ HTML thô trong bộ nhớ, không ghi đĩa.
Bao gồm cơ chế phục hồi tự động khi chứng chỉ SSL của website thiếu chuỗi trung gian.
"""

import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

# Thêm vendor vào path
VENDOR_DIR = Path(__file__).resolve().parent.parent / "vendor" / "claude_seo"
if str(VENDOR_DIR) not in sys.path:
    sys.path.insert(0, str(VENDOR_DIR))

import fetch_page
import pagespeed_check
import sitemap_discovery
import url_safety
import urllib3

# Tắt cảnh báo InsecureRequestWarning khi phải fallback SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def normalize_input_url(url: str) -> str:
    """
    Chuẩn hoá URL người dùng nhập:
    - Bỏ khoảng trắng
    - Tự thêm https:// nếu thiếu scheme
    """
    u = (url or "").strip()
    if not u:
        raise ValueError("Vui lòng nhập đường link.")

    if not (u.startswith("http://") or u.startswith("https://")):
        u = f"https://{u}"

    return u


def validate_user_url(url: str) -> str:
    """
    Kiểm tra tính an toàn SSRF qua url_safety:
    Chỉ nhận http/https, chặn localhost, IP nội bộ, IP cloud metadata.
    """
    norm_url = normalize_input_url(url)
    try:
        url_safety.validate_url_strict(norm_url)
    except Exception:
        raise ValueError("Đường link không hợp lệ hoặc không được phép kiểm tra")

    return norm_url


def fetch_robots_txt(base_url: str, timeout: int = 8) -> Dict[str, Any]:
    """
    Tải và kiểm tra file robots.txt.
    """
    parsed = urlparse(base_url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"

    try:
        res = fetch_page.fetch_page(
            robots_url,
            timeout=timeout,
            follow_redirects=True,
            max_redirects=3,
            max_bytes=512 * 1024,
        )
        if res.get("error") and "ssl error" in res["error"].lower():
            # Thử lại với session.verify = False nếu SSL lỗi
            with url_safety.safe_requests_session(robots_url) as session:
                session.verify = False
                resp = session.get(robots_url, timeout=timeout, allow_redirects=True)
                res = {"status_code": resp.status_code, "content": resp.text}

        status = res.get("status_code", 0)
        content = res.get("content", "")

        if status == 200 and content:
            rp = RobotFileParser()
            rp.parse(content.splitlines())
            blocked = not rp.can_fetch("*", base_url)
            return {
                "exists": True,
                "blocked": blocked,
                "url": robots_url,
            }
        else:
            return {
                "exists": False,
                "blocked": False,
                "url": robots_url,
            }
    except Exception:
        return {
            "exists": False,
            "blocked": False,
            "url": robots_url,
        }


def fetch_sitemap_info(url: str) -> Dict[str, Any]:
    """
    Khám phá sitemap bằng sitemap_discovery.
    """
    try:
        res = sitemap_discovery.discover_sitemaps(url)
        sitemaps = res.get("sitemaps", [])
        total_urls = 0
        for s in sitemaps:
            total_urls += s.get("url_count", 0)

        return {
            "found": len(sitemaps) > 0,
            "count": len(sitemaps),
            "url_count": total_urls,
            "sitemaps": sitemaps,
        }
    except Exception:
        return {
            "found": False,
            "count": 0,
            "url_count": 0,
            "sitemaps": [],
        }


def fetch_pagespeed_info(url: str, api_key: Optional[str] = None, timeout: int = 60) -> Dict[str, Any]:
    """
    Gọi PageSpeed Insights API mobile.
    """
    key = api_key or os.environ.get("PAGESPEED_API_KEY") or None

    try:
        raw_res = pagespeed_check.run_pagespeed(
            url=url,
            strategy="mobile",
            api_key=key,
        )

        if raw_res.get("error"):
            return {
                "success": False,
                "error": raw_res["error"],
            }

        scores = raw_res.get("lighthouse_scores", {})
        perf_score = scores.get("performance")

        lab = raw_res.get("lab_metrics", {})
        lcp_val = lab.get("largest-contentful-paint", {}).get("value")
        lcp_sec = (lcp_val / 1000.0) if lcp_val is not None else None

        cls_val = lab.get("cumulative-layout-shift", {}).get("value")

        # INP từ field_metrics
        field = raw_res.get("field_metrics", {})
        inp_val = None
        for k in ["url_interaction_to_next_paint", "origin_interaction_to_next_paint"]:
            if k in field and field[k].get("p75") is not None:
                inp_val = field[k]["p75"]
                break

        return {
            "success": True,
            "performance_score": perf_score,
            "lcp_seconds": lcp_sec,
            "cls": cls_val,
            "inp_ms": inp_val,
            "raw": raw_res,
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


def collect_all_data(
    raw_input_url: str,
    fetch_timeout: int = 15,
    psi_timeout: int = 60,
    pagespeed_key: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Thu thập toàn bộ dữ liệu từ 4 nguồn song song.
    """
    validated_url = validate_user_url(raw_input_url)

    # 1. Tải HTML trang web trước để có final_url (sau chuyển hướng)
    ssl_cert_issue = False
    try:
        page_res = fetch_page.fetch_page(
            validated_url,
            timeout=fetch_timeout,
            follow_redirects=True,
            max_redirects=5,
            max_bytes=5 * 1024 * 1024,  # Tối đa 5 MB
        )
    except url_safety.URLSafetyError:
        raise ValueError("Đường link không hợp lệ hoặc không được phép kiểm tra")
    except Exception as e:
        raise RuntimeError(f"Không truy cập được website này: {e}")

    # Xử lý lỗi tải trang
    if page_res.get("error"):
        err = page_res["error"]
        if "ssl error" in err.lower() or "certificate verify failed" in err.lower():
            # Thử lại với session.verify = False để phục hồi với các website thiếu cert trung gian (WR1, Let's Encrypt, Cloudflare)
            try:
                with url_safety.safe_requests_session(validated_url) as session:
                    session.verify = False
                    session.max_redirects = 5
                    headers = dict(fetch_page.DEFAULT_HEADERS)
                    resp = session.get(
                        validated_url,
                        headers=headers,
                        timeout=fetch_timeout,
                        allow_redirects=True,
                        stream=True,
                    )
                    raw, too_large = fetch_page.read_bounded(resp, 5 * 1024 * 1024)
                    resp.close()
                    page_res = {
                        "url": resp.url,
                        "status_code": resp.status_code,
                        "content": fetch_page.decode_body(raw, resp.headers.get("Content-Type", "")),
                        "headers": dict(resp.headers),
                        "redirect_chain": [r.url for r in resp.history] if resp.history else [],
                        "too_large": too_large,
                    }
                    ssl_cert_issue = True
            except Exception as ssl_fb_err:
                raise RuntimeError(f"Không truy cập được website này do lỗi chứng chỉ SSL: {ssl_fb_err}")
        elif "timeout" in err.lower():
            raise RuntimeError("Website phản hồi quá lâu (quá thời gian quy định)")
        elif "too large" in err.lower() or page_res.get("too_large"):
            raise RuntimeError("Trang web vượt quá kích thước cho phép (tối đa 5 MB)")
        else:
            raise RuntimeError(f"Không truy cập được website này: {err}")

    if page_res.get("too_large"):
        raise RuntimeError("Trang web vượt quá kích thước cho phép (tối đa 5 MB)")

    status_code = page_res.get("status_code", 0)
    raw_html = page_res.get("content", "")
    headers = page_res.get("headers", {})
    redirect_chain = page_res.get("redirect_chain", [])
    final_url = page_res.get("url") or validated_url

    # 2. Chạy 3 nguồn còn lại song song
    robots_res = {"exists": False, "blocked": False}
    sitemap_res = {"found": False, "count": 0, "url_count": 0}
    pagespeed_res = {"success": False, "error": "Not fetched"}

    with ThreadPoolExecutor(max_workers=3) as executor:
        f_robots = executor.submit(fetch_robots_txt, final_url, timeout=8)
        f_sitemap = executor.submit(fetch_sitemap_info, final_url)
        f_psi = executor.submit(fetch_pagespeed_info, final_url, pagespeed_key, psi_timeout)

        try:
            robots_res = f_robots.result(timeout=10)
        except Exception:
            pass

        try:
            sitemap_res = f_sitemap.result(timeout=15)
        except Exception:
            pass

        try:
            pagespeed_res = f_psi.result(timeout=psi_timeout + 5)
        except Exception:
            pagespeed_res = {"success": False, "error": "Timeout"}

    return {
        "raw_url": raw_input_url,
        "validated_url": validated_url,
        "final_url": final_url,
        "status_code": status_code,
        "raw_html": raw_html,
        "headers": headers,
        "redirect_chain": redirect_chain,
        "robots": robots_res,
        "sitemap": sitemap_res,
        "pagespeed": pagespeed_res,
        "ssl_cert_issue": ssl_cert_issue,
    }
