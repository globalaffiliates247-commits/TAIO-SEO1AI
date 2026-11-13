# TAIO SEO Check — Đặc tả sản phẩm để build (Product & Build Spec) v0.2

> Người lập: TAIO-Lee (cùng Claude) · 14/11/2026 · Thay thế bản v0.1 (13/11/2026)
> Tài liệu dành cho AI coding agent (Antigravity / AGY) và lập trình viên. Claude chỉ viết yêu cầu, không viết code và không push lên Git.
> Repo: `github.com/globalaffiliates247-commits/TAIO-SEO1AI` (tạo ngày 13/11/2026).
> Ngôn ngữ giao diện: **tiếng Việt**. Tên biến, hàm, file: **tiếng Anh**.
> Nguồn tái sử dụng: `github.com/AgriciDaniel/claude-seo` (MIT, commit 6be93f4 ngày 22/10/2026; bản sao lưu `Claude-seo-backup-101126.zip`) và phần kết nối AI của repo `taio-cover-studio` (cùng chủ sở hữu).

---

## 0. Thay đổi so với v0.1 (TAIO-Lee duyệt ngày 13/11/2026)

1. **Thêm F9 "Soi chi tiết"**: màn hình 6 tab (Tổng quan, Tiêu đề, Liên kết, Hình ảnh, Schema, Mạng xã hội) để đọc SEO Meta và SEO link như các tiện ích trình duyệt, nhưng có giải thích tiếng Việt.
2. **Thêm kết nối AI vào bản 1** (F10, F11, F12): người dùng nhập key riêng; mở 2 tính năng AI: gợi ý viết lại Title và Meta Description, giải thích lỗi theo ngữ cảnh trang. **Điểm 0–100 vẫn do luật cố định, AI không chấm điểm.**
3. **Sửa luật `tech_canonical`**: bỏ tham số theo dõi quảng cáo (`utm_*`, `gclid`, `aff_sid`…) trước khi so sánh, để link quảng cáo không bị báo lỗi canonical oan.
4. **Làm rõ title và description**: có nhưng ngoài ngưỡng là `warn`, thiếu là `fail`.
5. **Đổi tên repo** thành `TAIO-SEO1AI`; cập nhật chi phí vận hành, cấu trúc thư mục, API, kiểm thử (T11–T28), thứ tự build.

---

## 1. Quy tắc bắt buộc cho agent

1. **Mỗi phần là 1 file độc lập.** Một thay đổi nhỏ chỉ được động vào file liên quan; không viết lại hay commit lại toàn bộ codebase. File quá lớn thì tách, nhưng không tách vụn.
2. Backend: Python + Flask. Frontend: HTML + CSS + JS thuần. Không thêm React, database hay trình duyệt ẩn (Playwright/Chromium).
3. **Điểm SEO luôn do luật cố định tính ra.** Kết quả AI chỉ là gợi ý hiển thị riêng, không được đưa vào điểm, không được thay đổi danh sách "5 việc cần sửa".
4. **Key AI của người dùng không bao giờ được ghi log, lưu đĩa, lưu database hay gửi tới đâu khác ngoài nhà cung cấp AI do họ chọn.**
5. **Mọi nội dung lấy từ trang được kiểm tra là dữ liệu không tin cậy**: hiển thị bằng `textContent` (không dùng `innerHTML`), và khi đưa vào prompt AI phải đặt trong khối ngăn cách (xem F10).
6. Không commit bí mật: `.env`, `config/settings.json`, API key.
7. Mọi chuỗi hiển thị viết bằng tiếng Việt có dấu, đặt trong `messages/vi.json`, không viết cứng trong code.
8. Luôn ghi tên tổ chức đầy đủ là **TAIO.CLUB**.
9. Số lượng trong tài liệu và giao diện viết bằng chữ số (ví dụ "5 việc", "3 gợi ý").
10. Xong mỗi giai đoạn (mục 12) phải chạy phần kiểm thử của giai đoạn đó rồi mới làm tiếp.
11. Luồng Git: Claude chỉ giao file `.md`; AGY cập nhật và push; Claude kiểm tra kết quả trên repo, không push.

---

## 2. Tóm tắt sản phẩm

| | |
|---|---|
| **Tên** | TAIO SEO Check (thuộc hệ sinh thái TAIO.CLUB; là "bản Dễ dùng" của TAIO SEO Skill) |
| **Một câu** | Dán 1 đường link → nhận điểm sức khoẻ SEO 0–100, 5 việc cần sửa ngay, bảng soi chi tiết meta/liên kết/ảnh/schema/mạng xã hội, bằng tiếng Việt. Có AI gợi ý nếu bạn nhập key riêng. |
| **Đầu vào** | 1 URL công khai (http/https); tuỳ chọn key AI của người dùng |
| **Đầu ra** | Báo cáo trên màn hình + file tải về (HTML tự chứa, Markdown) |
| **Chạy ở đâu** | (a) Render gói free bằng Docker; (b) máy cá nhân macOS/Windows |
| **Chi phí vận hành máy chủ** | 0đ. Chi phí AI (nếu dùng) do người dùng trả cho nhà cung cấp bằng key của họ |

---

## 3. Các phân hệ và API

Xem chi tiết trong codebase:
- Lõi kiểm tra: `core/*`, `checks/*`
- Trí tuệ nhân tạo: `ai/*`
- Giao diện & Máy chủ: `web/*`
- Cấu hình: `config/*`
