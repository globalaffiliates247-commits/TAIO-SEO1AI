"""
tests/test_core.py - Bộ kiểm thử tự động cho Giai đoạn 1 (Lõi)
Bao gồm: T1, T2, T3, T4, T5, T11, T12, T13, T14, T15, T16, T17
"""

import unittest
from core.collect import validate_user_url
from core.extract_details import extract_details
from core.registry import run_checks
from core.score import calculate_group_scores, calculate_overall_score
from core.top_fixes import select_top_fixes
from core.url_tools import normalize_url, strip_tracking_params


class TestCore(unittest.TestCase):

    def test_t1_good_page(self):
        """T1: Trang mẫu tốt -> Nhóm 1, 2, 3 đạt 100%."""
        html = """<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="utf-8">
  <title>TAIO.CLUB - Nền Tảng Tự Động Hoá Kinh Doanh Số Toàn Diện</title>
  <meta name="description" content="Khám phá các giải pháp công nghệ, tự động hoá quy trình và chiến lược SEO đột phá cùng cộng đồng doanh nhân số tại TAIO.CLUB ngay hôm nay.">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link rel="canonical" href="https://taio.club/bai-viet">
  <meta property="og:title" content="TAIO.CLUB">
  <meta property="og:description" content="Kinh doanh số thông minh">
  <meta property="og:image" content="https://taio.club/cover.jpg">
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "Organization",
    "name": "TAIO.CLUB",
    "url": "https://taio.club"
  }
  </script>
</head>
<body>
  <h1>Tự Động Hoá Doanh Nghiệp Với Trí Tuệ Nhân Tạo Hiện Đại</h1>
  <h2>Lợi ích của AI trong kinh doanh</h2>
  <p>""" + ("Nội dung bài viết chất lượng cao giúp tăng trưởng bền vững cho doanh nghiệp số. " * 30) + """</p>
  <a href="https://taio.club/dich-vu">Dịch vụ</a>
  <a href="https://taio.club/khoa-hoc">Khoá học</a>
  <a href="https://taio.club/lien-he">Liên hệ</a>
  <img src="https://taio.club/anh1.jpg" alt="Mô tả ảnh 1">
  <img src="https://taio.club/anh2.jpg" alt="Mô tả ảnh 2">
</body>
</html>"""

        details, ai_context, notices = extract_details(
            raw_html=html,
            raw_url="https://taio.club/bai-viet",
            final_url="https://taio.club/bai-viet",
            status_code=200,
            headers={"Content-Type": "text/html"},
        )

        data = {
            "final_url": "https://taio.club/bai-viet",
            "status_code": 200,
            "redirect_chain": ["https://taio.club/bai-viet"],
            "robots": {"exists": True, "blocked": False},
            "sitemap": {"found": True, "url_count": 10},
            "details": details,
            "pagespeed": {"success": False},  # Chưa tính tốc độ
        }

        checks = run_checks(data)
        group_scores = calculate_group_scores(checks)

        # Kiểm tra nhóm technical, content, schema đều đạt 100
        self.assertEqual(group_scores["technical"]["score"], 100)
        self.assertEqual(group_scores["content"]["score"], 100)
        self.assertEqual(group_scores["schema"]["score"], 100)

    def test_t2_bad_page(self):
        """T2: Trang lỗi (2 H1, thiếu alt, không canonical, không schema, title 5 ký tự)."""
        html = """<!DOCTYPE html>
<html>
<head>
  <title>Ngắn</title>
</head>
<body>
  <h1>H1 Thứ Nhất</h1>
  <h1>H1 Thứ Hai</h1>
  <img src="banner.jpg">
  <p>Văn bản rất ngắn</p>
</body>
</html>"""
        details, ai_context, notices = extract_details(
            raw_html=html,
            raw_url="http://badsite.com",
            final_url="http://badsite.com",
            status_code=200,
        )

        data = {
            "final_url": "http://badsite.com",
            "status_code": 200,
            "redirect_chain": [],
            "robots": {"exists": False, "blocked": False},
            "sitemap": {"found": False},
            "details": details,
            "pagespeed": {"success": False},
        }

        checks = run_checks(data)
        checks_by_id = {c["id"]: c for c in checks}

        self.assertEqual(checks_by_id["content_h1"]["status"], "fail")
        self.assertEqual(checks_by_id["content_alt"]["status"], "fail")
        self.assertEqual(checks_by_id["tech_canonical"]["status"], "fail")
        self.assertEqual(checks_by_id["schema_present"]["status"], "fail")
        self.assertEqual(checks_by_id["content_title"]["status"], "warn")  # Có nhưng ngoài ngưỡng là warn

        top_fixes = select_top_fixes(checks, max_items=5)
        self.assertLessEqual(len(top_fixes), 5)
        # Các mục fail phải nằm trước warn
        statuses = [checks_by_id[fid]["status"] for fid in top_fixes]
        if "warn" in statuses and "fail" in statuses:
            self.assertLess(statuses.index("fail"), statuses.index("warn"))

    def test_t3_pagespeed_levels(self):
        """T3: Dữ liệu PageSpeed giả lập 3 mức (tốt / cảnh báo / yếu)."""
        from checks.speed import check_speed_score, check_speed_lcp, check_speed_cls

        # Mức tốt
        good_data = {
            "pagespeed": {
                "success": True,
                "performance_score": 95,
                "lcp_seconds": 1.8,
                "cls": 0.05,
            }
        }
        self.assertEqual(check_speed_score(good_data)["status"], "pass")
        self.assertEqual(check_speed_lcp(good_data)["status"], "pass")
        self.assertEqual(check_speed_cls(good_data)["status"], "pass")

        # Mức cảnh báo
        warn_data = {
            "pagespeed": {
                "success": True,
                "performance_score": 75,
                "lcp_seconds": 3.2,
                "cls": 0.15,
            }
        }
        self.assertEqual(check_speed_score(warn_data)["status"], "warn")
        self.assertEqual(check_speed_lcp(warn_data)["status"], "warn")
        self.assertEqual(check_speed_cls(warn_data)["status"], "warn")

        # Mức yếu
        poor_data = {
            "pagespeed": {
                "success": True,
                "performance_score": 35,
                "lcp_seconds": 5.5,
                "cls": 0.35,
            }
        }
        self.assertEqual(check_speed_score(poor_data)["status"], "fail")
        self.assertEqual(check_speed_lcp(poor_data)["status"], "fail")
        self.assertEqual(check_speed_cls(poor_data)["status"], "fail")

    def test_t4_pagespeed_timeout_reweighting(self):
        """T4: PageSpeed quá thời gian -> Nhóm tốc độ 'không đo được', điểm chung chia lại tỉ lệ."""
        checks = [
            {"id": "tech_1", "group": "technical", "weight": 30, "status": "pass"},
            {"id": "content_1", "group": "content", "weight": 30, "status": "pass"},
            {"id": "schema_1", "group": "schema", "weight": 15, "status": "pass"},
            {"id": "speed_1", "group": "speed", "weight": 25, "status": "na"},
        ]
        g_scores = calculate_group_scores(checks)
        self.assertEqual(g_scores["speed"]["status"], "unmeasurable")

        score, band, label, color = calculate_overall_score(g_scores)
        # 3 nhóm kia đều đạt 100%, nhóm speed na -> điểm chung vẫn phải là 100!
        self.assertEqual(score, 100)
        self.assertEqual(band, "good")

    def test_t5_unsafe_urls(self):
        """T5: URL nội bộ và URL sai định dạng -> Bị chặn với thông báo tiếng Việt."""
        bad_urls = [
            "http://127.0.0.1",
            "http://localhost",
            "http://169.254.169.254",
            "file:///etc/passwd",
        ]
        for u in bad_urls:
            with self.assertRaises(ValueError) as ctx:
                validate_user_url(u)
            self.assertIn("Đường link không hợp lệ hoặc không được phép kiểm tra", str(ctx.exception))

    def test_t11_canonical_with_ad_tracking(self):
        """T11: Canonical với tham số quảng cáo:
        URL https://www.kidsplaza.vn/?utm_source=accesstrade&aff_sid=XXXX&gad_source=1&gclid=YYYY, canonical https://www.kidsplaza.vn
        -> tech_canonical = pass; có notice_tracking_url."""
        raw_url = "https://www.kidsplaza.vn/?utm_source=accesstrade&aff_sid=XXXX&gad_source=1&gclid=YYYY"
        final_url = "https://www.kidsplaza.vn/?utm_source=accesstrade&aff_sid=XXXX&gad_source=1&gclid=YYYY"

        html = """<!DOCTYPE html>
<html>
<head>
  <link rel="canonical" href="https://www.kidsplaza.vn">
</head>
<body><p>Nội dung</p></body>
</html>"""
        details, ai_context, notices = extract_details(
            raw_html=html,
            raw_url=raw_url,
            final_url=final_url,
        )

        data = {
            "final_url": final_url,
            "details": details,
        }
        from checks.technical import check_tech_canonical
        res = check_tech_canonical(data)
        self.assertEqual(res["status"], "pass")
        self.assertIsNotNone(res.get("note"))
        self.assertIn("quảng cáo", res["note"])

        # Kiểm tra notice_tracking_url
        notice_ids = [n["id"] for n in notices]
        self.assertIn("notice_tracking_url", notice_ids)

    def test_t12_canonical_variations(self):
        """T12: Canonical trỏ sang trang khác -> warn; thiếu -> fail; có 2 thẻ -> warn."""
        from checks.technical import check_tech_canonical

        # Trỏ sang trang khác
        d_diff = {"details": {"overview": {"canonical": {"count": 1, "href": "https://other.com"}, "url": {}}}}
        d_diff["final_url"] = "https://mysite.com"
        self.assertEqual(check_tech_canonical(d_diff)["status"], "warn")

        # Thiếu
        d_missing = {"details": {"overview": {"canonical": {"count": 0, "href": ""}, "url": {}}}}
        self.assertEqual(check_tech_canonical(d_missing)["status"], "fail")

        # Có 2 thẻ
        d_multi = {"details": {"overview": {"canonical": {"count": 2, "href": "https://mysite.com"}, "url": {}}}}
        self.assertEqual(check_tech_canonical(d_multi)["status"], "warn")

    def test_t13_heading_hierarchy(self):
        """T13: Cây tiêu đề: mẫu có 2 H1, H2 rồi H4, 1 H3 rỗng -> Đúng cờ multiple_h1, skipped_level, empty."""
        html = """
        <h1>H1 Thứ 1</h1>
        <h1>H1 Thứ 2</h1>
        <h2>H2 Bình Thường</h2>
        <h4>H4 Bị Nhảy Cấp</h4>
        <h3></h3>
        """
        details, _, _ = extract_details(html, "https://test.com", "https://test.com")
        headings = details["headings"]

        # H1 thứ hai có cờ multiple_h1
        self.assertIn("multiple_h1", headings[1]["issues"])
        # H4 có cờ skipped_level
        self.assertIn("skipped_level", headings[3]["issues"])
        # H3 có cờ empty
        self.assertIn("empty", headings[4]["issues"])

    def test_t14_links_classification_and_limits(self):
        """T14: Liên kết: giới hạn 500, rel tag, mailto, tel, javascript."""
        # Tạo trang có 520 liên kết nội bộ
        links_html = "".join([f'<a href="/trang-{i}">Trang {i}</a>' for i in range(520)])
        links_html += '<a href="https://other.com" rel="nofollow sponsored">Ngoại link</a>'
        links_html += '<a href="mailto:info@taio.club">Email</a>'
        links_html += '<a href="javascript:void(0)">JS</a>'

        html = f"<html><body>{links_html}</body></html>"
        details, _, _ = extract_details(html, "https://taio.club", "https://taio.club")
        links = details["links"]

        self.assertEqual(len(links["internal"]), 500)
        self.assertTrue(links["truncated"]["internal"])
        self.assertEqual(links["other_counts"]["mailto"], 1)
        self.assertEqual(links["other_counts"]["javascript"], 1)

        ext = links["external"][0]
        self.assertTrue(ext["nofollow"])
        self.assertTrue(ext["sponsored"])

    def test_t15_images_alt_status(self):
        """T15: 3 ảnh: alt có, alt rỗng, thiếu alt -> 3 trạng thái ok, empty, missing."""
        html = """<html><body>
        <img src="1.jpg" alt="Đầy đủ">
        <img src="2.jpg" alt="">
        <img src="3.jpg">
        </body></html>"""
        details, _, _ = extract_details(html, "https://test.com", "https://test.com")
        images = details["images"]

        self.assertEqual(images[0]["alt_status"], "ok")
        self.assertEqual(images[1]["alt_status"], "empty")
        self.assertEqual(images[2]["alt_status"], "missing")

    def test_t16_social_meta(self):
        """T16: Thẻ mạng xã hội Open Graph và Twitter."""
        html = """<html><head>
        <meta property="og:title" content="Tiêu đề FB">
        <meta property="og:site_name" content="TAIO">
        <meta name="twitter:card" content="summary_large_image">
        </head><body></body></html>"""
        details, _, _ = extract_details(html, "https://test.com", "https://test.com")
        social = details["social"]

        self.assertEqual(social["open_graph"].get("og:title"), "Tiêu đề FB")
        self.assertEqual(social["twitter"].get("twitter:card"), "summary_large_image")
        # Thiếu og:description và og:image
        self.assertIn("og:description", social["missing"])
        self.assertIn("og:image", social["missing"])

    def test_t17_js_rendered_notice(self):
        """T17: Trang JS rendered: số chữ < 50 và có div#root -> có notice_js_rendered."""
        html = """<html><head><title>SPA</title></head><body><div id="root"></div></body></html>"""
        details, _, notices = extract_details(html, "https://spa.com", "https://spa.com")
        notice_ids = [n["id"] for n in notices]
        self.assertIn("notice_js_rendered", notice_ids)


if __name__ == "__main__":
    unittest.main()
