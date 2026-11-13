"""
tests/test_web.py - Bộ kiểm thử tự động cho Giai đoạn 4 (Web API & UI Security)
Bao gồm: T6, T7, T9, T10, T18, T24, T25, T27
"""

import json
import os
import unittest
from unittest.mock import patch

from web.ratelimit import RateLimiter, limiter
from web.server import create_app


class TestWeb(unittest.TestCase):

    def setUp(self):
        # Đặt môi trường kiểm thử
        os.environ["LOCAL_MODE"] = "1"
        os.environ["DAILY_LIMIT"] = "5"
        os.environ["MAX_PARALLEL_CHECKS"] = "2"
        os.environ["AI_DAILY_LIMIT"] = "20"
        os.environ["MAX_PARALLEL_AI"] = "2"

        # Khởi tạo app & client
        self.app = create_app()
        self.client = self.app.test_client()

        # Reset limiter
        limiter.daily_seo_counts.clear()
        limiter.daily_ai_counts.clear()
        limiter.active_seo_slots = 0
        limiter.active_ai_slots = 0

    def test_t9_healthz_and_index(self):
        """T9: Endpoint / và /healthz phản hồi chuẩn xác."""
        res_h = self.client.get("/healthz")
        self.assertEqual(res_h.status_code, 200)
        self.assertEqual(res_h.data.decode("utf-8"), "ok")

        res_root = self.client.get("/")
        self.assertEqual(res_root.status_code, 200)
        self.assertIn("TAIO.CLUB", res_root.data.decode("utf-8"))
        # Kiểm tra security headers
        self.assertIn("Content-Security-Policy", res_root.headers)
        self.assertEqual(res_root.headers["X-Frame-Options"], "DENY")

    def test_t10_config_version(self):
        """T10: Dòng phiên bản đọc từ version.json và trả về qua /api/config."""
        res = self.client.get("/api/config")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["version"], "0.1.0")
        self.assertEqual(data["stamp"], "14112600")
        self.assertEqual(data["daily_limit"], 5)
        self.assertIn("ai", data)
        self.assertGreaterEqual(len(data["ai"]["providers"]), 1)

    def test_t6_daily_seo_limit_429(self):
        """T6: Lượt kiểm tra thứ 6 cùng IP trả về mã 429."""
        ip = "192.168.1.100"
        headers = {"X-Forwarded-For": ip}

        mock_collected = {
            "raw_url": "https://taio.club",
            "validated_url": "https://taio.club",
            "final_url": "https://taio.club",
            "status_code": 200,
            "raw_html": "<html><head><title>Test</title></head><body><h1>H1</h1></body></html>",
            "headers": {},
            "redirect_chain": [],
            "robots": {"exists": True, "blocked": False},
            "sitemap": {"found": True, "url_count": 1},
            "pagespeed": {"success": False},
        }

        with patch("web.server.collect_all_data", return_value=mock_collected):
            # 5 lượt đầu tiên thành công
            for i in range(5):
                res = self.client.post("/api/check", json={"url": "https://taio.club"}, headers=headers)
                self.assertEqual(res.status_code, 200)

            # Lượt thứ 6 bị chặn 429
            res6 = self.client.post("/api/check", json={"url": "https://taio.club"}, headers=headers)
            self.assertEqual(res6.status_code, 429)
            err_data = res6.get_json()
            self.assertIn("Hôm nay bạn đã dùng hết 5 lượt", err_data["error"])

    def test_t7_parallel_seo_limit(self):
        """T7: 3 lượt kiểm tra cùng lúc -> lượt thứ 3 nhận thông báo đông người dùng."""
        # Giả lập 2 slot đang bận
        limiter.active_seo_slots = 2
        res = self.client.post("/api/check", json={"url": "https://taio.club"})
        self.assertEqual(res.status_code, 429)
        self.assertIn("Đang đông người dùng", res.get_json()["error"])

    def test_t18_xss_safety_in_json(self):
        """T18: XSS trong title và JSON-LD được trích xuất an toàn trong payload JSON."""
        malicious_html = """<!DOCTYPE html>
<html>
<head>
  <title>&lt;img src=x onerror=alert(1)&gt;</title>
  <script type="application/ld+json">
  {"@context": "https://schema.org", "@type": "Thing", "name": "</script><script>alert('xss')</script>"}
  </script>
</head>
<body>
  <h1>Heading</h1>
</body>
</html>"""
        mock_collected = {
            "raw_url": "https://taio.club",
            "validated_url": "https://taio.club",
            "final_url": "https://taio.club",
            "status_code": 200,
            "raw_html": malicious_html,
            "headers": {},
            "redirect_chain": [],
            "robots": {"exists": True, "blocked": False},
            "sitemap": {"found": True, "url_count": 1},
            "pagespeed": {"success": False},
        }

        with patch("web.server.collect_all_data", return_value=mock_collected):
            res = self.client.post("/api/check", json={"url": "https://taio.club"})
            self.assertEqual(res.status_code, 200)
            data = res.get_json()
            # Dữ liệu nằm nguyên trong JSON string, không thực thi mã
            self.assertIn("<img src=x", data["details"]["overview"]["title"]["text"])

    def test_t24_ai_limit_separate_from_seo(self):
        """T24: Lệnh gọi AI thứ 21 -> 429; kiểm tra SEO vẫn chạy bình thường; 2 bộ đếm độc lập."""
        ip = "192.168.1.50"
        headers = {"X-Forwarded-For": ip, "X-AI-Key": "sk-test"}

        # Đặt AI limit đã dùng 20 lượt
        limiter.daily_ai_counts[ip] = 20

        # Lệnh gọi AI thứ 21 -> 429
        res_ai = self.client.post("/api/ai/test", json={"provider": "openai"}, headers=headers)
        self.assertEqual(res_ai.status_code, 429)
        self.assertIn("hết lượt AI miễn phí", res_ai.get_json()["error"])

        # Kiểm tra SEO vẫn dùng được bình thường (SEO count vẫn = 0)
        self.assertEqual(limiter.daily_seo_counts.get(ip, 0), 0)

    def test_t25_missing_ai_key(self):
        """T25: Chưa có key AI -> lỗi tiếng Việt 400 chỉ nơi nhập key."""
        res = self.client.post("/api/ai/test", json={"provider": "openai"})
        self.assertEqual(res.status_code, 400)
        self.assertIn("Chưa có key AI", res.get_json()["error"])

    def test_t8_page_too_large_5mb(self):
        """T8: Trang nặng hơn 5 MB -> báo lỗi rõ ràng."""
        with patch("core.collect.fetch_page.fetch_page", return_value={"too_large": True, "error": "Response body too large"}):
            res = self.client.post("/api/check", json={"url": "https://taio.club"})
            self.assertEqual(res.status_code, 502)
            self.assertIn("vượt quá kích thước cho phép", res.get_json()["error"])

    def test_t27_payload_size_limit(self):
        """T27: Trang 5.000 liên kết, 1.000 ảnh -> payload phản hồi /api/check dưới 1 MB."""
        many_links = "".join([f'<a href="https://taio.club/page/{i}">Liên kết {i}</a>\n' for i in range(5000)])
        many_images = "".join([f'<img src="https://taio.club/img/{i}.jpg" alt="Ảnh {i}">\n' for i in range(1000)])
        large_html = f"<html><head><title>Trang lớn</title></head><body><h1>Test</h1>{many_links}{many_images}</body></html>"

        mock_collected = {
            "raw_url": "https://taio.club",
            "validated_url": "https://taio.club",
            "final_url": "https://taio.club",
            "status_code": 200,
            "raw_html": large_html,
            "headers": {},
            "redirect_chain": [],
            "robots": {"exists": True, "blocked": False},
            "sitemap": {"found": True, "url_count": 1},
            "pagespeed": {"success": False},
        }

        with patch("web.server.collect_all_data", return_value=mock_collected):
            res = self.client.post("/api/check", json={"url": "https://taio.club"})
            self.assertEqual(res.status_code, 200)
            raw_json_len = len(res.data)
            # Giới hạn dưới 1 MB (1024 * 1024 bytes)
            self.assertLess(raw_json_len, 1024 * 1024)

            data = res.get_json()
            # Giới hạn nội bộ 500 links, 200 images
            self.assertLessEqual(len(data["details"]["links"]["internal"]), 500)
            self.assertLessEqual(len(data["details"]["images"]), 200)


if __name__ == "__main__":
    unittest.main()
