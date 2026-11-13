# Nhật Ký Thay Đổi — TAIO SEO Check (CHANGELOG.md)

Mọi thay đổi quan trọng của dự án được ghi lại tại đây theo chuẩn [Keep a Changelog](https://keepachangelog.com/).

---

## [0.2.0] - 2026-11-14

### Đã thêm (Added)
- **F9 Bảng Soi Chi Tiết (6 Tab):**
  - Tab 1: Tổng quan (Title, Description, Canonical, Indexability, Robots, Lang, Viewport, Word count, CMS, Notices).
  - Tab 2: Tiêu đề (Cây H1–H6 có thứ tự, gắn cờ multiple_h1, skipped_level, empty, missing_h1).
  - Tab 3: Liên kết (Phân tách nội bộ và bên ngoài, cờ rel nofollow/sponsored/ugc, bộ lọc tìm kiếm tức thì).
  - Tab 4: Hình ảnh (Danh sách ảnh, trạng thái thẻ alt, kích thước, ảnh thu nhỏ tối đa 30 ảnh đầu).
  - Tab 5: Schema JSON-LD (Kiểm tra hợp lệ @context, @type, xem mã JSON thô).
  - Tab 6: Mạng xã hội (Trích xuất đầy đủ thẻ Open Graph & Twitter Card, khung xem trước mô phỏng chia sẻ).
- **F10 Kết nối AI bảo mật bằng key riêng:**
  - Hỗ trợ Anthropic (Claude), Google Gemini, OpenAI (GPT-4o), OpenRouter, DeepSeek và Ollama cục bộ.
  - Chống Prompt Injection bằng khối ngăn cách có mã token ngẫu nhiên.
  - Chống SSRF bằng danh sách trắng Host trong chế độ máy chủ.
  - Tự động che giấu API key trong logs và thông báo lỗi.
- **F11 Gợi ý viết lại Title và Meta Description:**
  - Tạo 3 gợi ý Title (≤ 60 ký tự) và 3 gợi ý Description (70–160 ký tự) theo các góc tiếp cận đa dạng.
  - Tự động đếm ký tự Unicode NFC và cảnh báo mục ngoài ngưỡng.
- **F12 Giải thích lỗi theo ngữ cảnh trang:**
  - Nhận diện nền tảng CMS (WordPress, Shopify, Wix, Webflow, Haravan, Sapo).
  - AI giải thích cách sửa cụ thể và đưa ra ví dụ mẫu ngắn dưới 400 ký tự.
- **Xuất báo cáo đa định dạng:**
  - Tải file HTML tự chứa (in PDF tiện lợi).
  - Tải file Markdown cấu trúc chuẩn cho lập trình viên.
- **Hệ thống kiểm thử tự động toàn diện:** 26 bài test bao quát các trường hợp T1–T28.

### Đã sửa (Changed)
- Sửa luật `tech_canonical`: Tự động loại bỏ tham số theo dõi quảng cáo (`utm_*`, `gclid`, `aff_sid`...) trước khi so sánh canonical, tránh báo lỗi oan cho các chiến dịch marketing.
- Phân loại rõ ràng cho Title và Description: có nhưng ngoài ngưỡng là `warn`, thiếu là `fail`.
- Tách biệt hoàn toàn hai bộ đếm giới hạn: kiểm tra SEO (5 lượt/ngày) và gọi AI (20 lượt/ngày).

---

## [0.1.0] - 2026-11-13

### Đã thêm
- Khởi tạo kiến trúc nền tảng dựa trên mã nguồn mở Claude-seo (MIT).
- Tích hợp 24 luật kiểm tra thuộc 4 nhóm trọng tâm: Kỹ thuật, Nội dung, Schema, Tốc độ.
- Tính điểm sức khoẻ SEO 0–100 bằng luật cố định.
- Lọc top 5 việc cần khắc phục theo nguyên lý Pareto 80/20.
