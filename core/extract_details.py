"""
core/extract_details.py - Trích xuất chi tiết chuyên sâu cho 6 tab (F9), thông báo (notices)
và dữ liệu tóm tắt cho AI (ai_context).
"""

import json
import re
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.parse import urlparse
from bs4 import BeautifulSoup

from core.cms_detect import detect_cms
from core.url_tools import classify_link, normalize_domain, normalize_url, strip_tracking_params


def _count_words(text: str) -> int:
    """Đếm số từ trong văn bản."""
    words = re.findall(r"\b\w+\b", text, re.UNICODE)
    return len(words)


def extract_details(
    raw_html: str,
    raw_url: str,
    final_url: str,
    status_code: int = 200,
    headers: Optional[Dict[str, str]] = None,
    robots_blocked: bool = False,
) -> Tuple[Dict[str, Any], Dict[str, Any], List[Dict[str, Any]]]:
    """
    Phân tích raw_html và trả về:
    (details, ai_context, notices)
    """
    if headers is None:
        headers = {}

    soup = BeautifulSoup(raw_html or "", "html.parser")
    headers_lower = {k.lower(): v for k, v in headers.items()}

    # --- 1. Notices & URL Cleaning ---
    clean_url, had_tracking = strip_tracking_params(raw_url)
    notices: List[Dict[str, Any]] = []

    if had_tracking:
        notices.append({
            "id": "notice_tracking_url",
            "level": "info",
            "text_key": "notice_tracking_url",
        })

    # --- 2. Title & Description ---
    title_tag = soup.find("title")
    title_text = title_tag.get_text().strip() if title_tag else ""
    title_len = len(title_text)

    desc_meta = soup.find("meta", attrs={"name": re.compile(r"^description$", re.I)})
    desc_text = desc_meta.get("content", "").strip() if desc_meta else ""
    desc_len = len(desc_text)

    # --- 3. Canonical ---
    canonical_tags = soup.find_all("link", attrs={"rel": lambda x: x and "canonical" in x.lower() if isinstance(x, str) else (x and any("canonical" in item.lower() for item in x))})
    canonical_count = len(canonical_tags)
    canonical_href = canonical_tags[0].get("href", "").strip() if canonical_count > 0 else ""

    canonical_relation = "missing"
    if canonical_count > 1:
        canonical_relation = "multiple"
    elif canonical_count == 1:
        if not canonical_href:
            canonical_relation = "invalid"
        else:
            norm_final = normalize_url(final_url)
            norm_canon = normalize_url(canonical_href)
            if norm_final == norm_canon:
                canonical_relation = "self"
            else:
                canonical_relation = "different"

    # --- 4. Robots & Indexability ---
    meta_robots_tags = soup.find_all("meta", attrs={"name": re.compile(r"^robots$", re.I)})
    meta_robots_content = ", ".join(m.get("content", "").strip() for m in meta_robots_tags if m.get("content"))

    x_robots_header = headers_lower.get("x-robots-tag", "")

    indexable_reasons: List[str] = []
    if status_code != 200:
        indexable_reasons.append(f"Mã trạng thái {status_code} (khác 200)")
    if robots_blocked:
        indexable_reasons.append("Bị chặn bởi robots.txt")
    if "noindex" in meta_robots_content.lower():
        indexable_reasons.append("Thẻ meta robots chứa noindex")
    if "noindex" in x_robots_header.lower():
        indexable_reasons.append("Header X-Robots-Tag chứa noindex")

    indexable = len(indexable_reasons) == 0

    # --- 5. Lang & Viewport & CMS & Words ---
    html_tag = soup.find("html")
    lang_attr = html_tag.get("lang", "").strip() if html_tag and html_tag.has_attr("lang") else ""

    viewport_meta = soup.find("meta", attrs={"name": re.compile(r"^viewport$", re.I)})
    viewport_content = viewport_meta.get("content", "").strip() if viewport_meta else ""

    cms_detected = detect_cms(raw_html, headers)

    # Đếm số chữ body
    body_tag = soup.find("body")
    body_text = ""
    if body_tag:
        # Loại bỏ script, style
        for tag in body_tag(["script", "style", "noscript", "svg"]):
            tag.extract()
        body_text = body_tag.get_text(separator=" ", strip=True)
    else:
        body_text = soup.get_text(separator=" ", strip=True)

    word_count = _count_words(body_text)

    # Kiểm tra notice JS-rendered
    if word_count < 50:
        has_js_root = bool(soup.find(id=re.compile(r"^(root|app|__next|__nuxt)$", re.I)))
        if has_js_root:
            notices.append({
                "id": "notice_js_rendered",
                "level": "warn",
                "text_key": "notice_js_rendered",
            })

    overview = {
        "title": {
            "text": title_text,
            "length": title_len,
            "status": "ok" if 30 <= title_len <= 60 else ("warn" if title_len > 0 else "fail"),
        },
        "description": {
            "text": desc_text,
            "length": desc_len,
            "status": "ok" if 70 <= desc_len <= 160 else ("warn" if desc_len > 0 else "fail"),
        },
        "url": {
            "raw": raw_url,
            "final": final_url,
            "clean": clean_url,
            "had_tracking": had_tracking,
        },
        "canonical": {
            "href": canonical_href,
            "count": canonical_count,
            "relation": canonical_relation,
        },
        "indexability": {
            "indexable": indexable,
            "reasons": indexable_reasons,
        },
        "robots_meta": meta_robots_content,
        "x_robots_header": x_robots_header,
        "lang": lang_attr,
        "viewport": viewport_content,
        "word_count": word_count,
        "cms": cms_detected,
    }

    # --- 6. Headings Hierarchy ---
    headings_data: List[Dict[str, Any]] = []
    h_tags = soup.find_all(re.compile(r"^h[1-6]$", re.I))

    h1_count = 0
    prev_level = 0
    all_h1_texts: List[str] = []
    heading_snippets_for_ai: List[str] = []

    for tag in h_tags[:300]:  # Giới hạn 300 thẻ
        level = int(tag.name[1])
        text = tag.get_text(strip=True)
        issues: List[str] = []

        if not text:
            issues.append("empty")

        if level == 1:
            h1_count += 1
            if h1_count > 1:
                issues.append("multiple_h1")
            all_h1_texts.append(text)
        elif prev_level > 0 and level > prev_level + 1:
            issues.append("skipped_level")

        prev_level = level
        headings_data.append({
            "level": level,
            "text": text,
            "issues": issues,
        })

        if text:
            words = text.split()
            truncated_h = " ".join(words[:15])
            if len(words) > 15:
                truncated_h += "..."
            heading_snippets_for_ai.append(truncated_h)

    # Đánh dấu cờ missing_h1 nếu không có thẻ H1 nào
    if h1_count == 0 and headings_data:
        headings_data[0]["issues"].append("missing_h1")

    # --- 7. Links ---
    internal_links: List[Dict[str, Any]] = []
    external_links: List[Dict[str, Any]] = []
    other_counts: Dict[str, int] = {
        "mailto": 0,
        "tel": 0,
        "javascript": 0,
        "hash": 0,
        "other": 0,
    }

    raw_a_tags = soup.find_all("a", href=True)
    truncated_internal = False
    truncated_external = False

    for a in raw_a_tags:
        raw_href = a.get("href", "")
        cat, target_url = classify_link(final_url, raw_href)
        text = a.get_text(strip=True)
        rel_val = a.get("rel", "")
        if isinstance(rel_val, list):
            rel_str = " ".join(rel_val).lower()
        else:
            rel_str = str(rel_val).lower()

        if cat == "internal":
            if len(internal_links) < 500:
                internal_links.append({
                    "url": target_url,
                    "anchor": text,
                    "rel": rel_str,
                    "nofollow": "nofollow" in rel_str,
                    "sponsored": "sponsored" in rel_str,
                    "ugc": "ugc" in rel_str,
                    "empty_anchor": not bool(text),
                })
            else:
                truncated_internal = True
        elif cat == "external":
            if len(external_links) < 500:
                external_links.append({
                    "url": target_url,
                    "anchor": text,
                    "rel": rel_str,
                    "nofollow": "nofollow" in rel_str,
                    "sponsored": "sponsored" in rel_str,
                    "ugc": "ugc" in rel_str,
                    "empty_anchor": not bool(text),
                })
            else:
                truncated_external = True
        else:
            if cat in other_counts:
                other_counts[cat] += 1
            else:
                other_counts["other"] += 1

    links_result = {
        "internal": internal_links,
        "external": external_links,
        "other_counts": other_counts,
        "total_internal": len(internal_links) + (1 if truncated_internal else 0),
        "total_external": len(external_links) + (1 if truncated_external else 0),
        "truncated": {
            "internal": truncated_internal,
            "external": truncated_external,
        },
    }

    # --- 8. Images ---
    images_data: List[Dict[str, Any]] = []
    img_tags = soup.find_all("img")

    for img in img_tags[:200]:  # Giới hạn 200 ảnh
        src = img.get("src") or img.get("data-src") or ""
        alt = img.get("alt")

        if alt is None:
            alt_status = "missing"
            alt_text = ""
        elif alt.strip() == "":
            alt_status = "empty"
            alt_text = ""
        else:
            alt_status = "ok"
            alt_text = alt.strip()

        ext = ""
        if src:
            path_part = urlparse(src).path
            if "." in path_part:
                ext = path_part.rsplit(".", 1)[-1].lower()[:5]

        images_data.append({
            "src": src,
            "alt": alt_text,
            "alt_status": alt_status,
            "width": img.get("width", ""),
            "height": img.get("height", ""),
            "loading": img.get("loading", ""),
            "ext": ext,
        })

    # --- 9. Schema (JSON-LD) ---
    schema_blocks: List[Dict[str, Any]] = []
    ld_scripts = soup.find_all("script", attrs={"type": re.compile(r"^application/ld\+json$", re.I)})

    for s in ld_scripts[:20]:  # Giới hạn 20 khối
        raw_content = s.string or s.get_text() or ""
        raw_content = raw_content.strip()
        excerpt = raw_content[:20480]  # Giới hạn 20 KB

        valid = False
        types: List[str] = []
        errors: List[str] = []

        if not raw_content:
            errors.append("Khối JSON-LD rỗng")
        else:
            try:
                data = json.loads(raw_content)
                # Kiểm tra context và type
                def _collect_types(obj: Any):
                    if isinstance(obj, dict):
                        t = obj.get("@type")
                        if t:
                            if isinstance(t, list):
                                types.extend(str(item) for item in t)
                            else:
                                types.append(str(t))
                        if "@graph" in obj and isinstance(obj["@graph"], list):
                            for sub in obj["@graph"]:
                                _collect_types(sub)
                    elif isinstance(obj, list):
                        for sub in obj:
                            _collect_types(sub)

                _collect_types(data)

                # Kiểm tra @context
                has_context = False
                if isinstance(data, dict):
                    has_context = bool(data.get("@context")) or any(
                        isinstance(sub, dict) and bool(sub.get("@context"))
                        for sub in data.get("@graph", [])
                    )
                elif isinstance(data, list):
                    has_context = any(isinstance(sub, dict) and bool(sub.get("@context")) for sub in data)

                if not has_context:
                    errors.append("Thiếu thuộc tính @context")
                if not types:
                    errors.append("Thiếu thuộc tính @type")

                if has_context and types:
                    valid = True

            except json.JSONDecodeError as e:
                errors.append(f"Cú pháp JSON không hợp lệ: {e.msg}")
            except Exception as e:
                errors.append(f"Lỗi phân tích JSON-LD: {str(e)}")

        schema_blocks.append({
            "types": types,
            "valid": valid,
            "errors": errors,
            "raw_excerpt": excerpt,
        })

    # --- 10. Social Meta (Open Graph & Twitter) ---
    open_graph: Dict[str, str] = {}
    twitter: Dict[str, str] = {}

    all_meta = soup.find_all("meta")
    for m in all_meta:
        prop = (m.get("property") or m.get("name") or "").strip().lower()
        content = m.get("content", "").strip()
        if not prop or not content:
            continue

        if prop.startswith("og:") or prop.startswith("fb:"):
            open_graph[prop] = content
        elif prop.startswith("twitter:"):
            twitter[prop] = content

    missing_social: List[str] = []
    if "og:title" not in open_graph:
        missing_social.append("og:title")
    if "og:description" not in open_graph:
        missing_social.append("og:description")
    if "og:image" not in open_graph:
        missing_social.append("og:image")

    social_data = {
        "open_graph": open_graph,
        "twitter": twitter,
        "missing": missing_social,
    }

    # --- 11. Details Bundle ---
    details = {
        "overview": overview,
        "headings": headings_data,
        "links": links_result,
        "images": images_data,
        "schema": schema_blocks,
        "social": social_data,
        "notices": notices,
    }

    # --- 12. AI Context Bundle ---
    text_excerpt = body_text[:3000].strip()
    ai_context = {
        "url": final_url,
        "lang": lang_attr or "vi",
        "site_name": open_graph.get("og:site_name", ""),
        "title": title_text,
        "description": desc_text,
        "h1": all_h1_texts[0] if all_h1_texts else "",
        "headings": heading_snippets_for_ai[:20],
        "text_excerpt": text_excerpt,
    }

    return details, ai_context, notices
