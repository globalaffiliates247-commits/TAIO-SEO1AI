# TAIO SEO Check — Kiểm Tra Sức Khoẻ SEO Website Toàn Diện

> **TAIO SEO Check** là giải pháp phân tích và kiểm tra sức khoẻ SEO website 1 chạm, thiết kế thân thiện cho người không rành công nghệ, thuộc hệ sinh thái **TAIO.CLUB**.  
> Dán 1 đường link duy nhất → Nhận điểm SEO 0–100, 5 việc cần sửa ngay, và bảng soi chi tiết cấu trúc thẻ meta, liên kết, ảnh, schema, mạng xã hội — 100% bằng tiếng Việt.

---

## 🌟 Điểm nổi bật

1. **Điểm SEO 0–100 chuẩn mực:** Tính toán hoàn toàn bằng luật cố định trên 24 chỉ số thuộc 4 nhóm (Kỹ thuật, Nội dung, Schema, Tốc độ). AI không chấm điểm, đảm bảo tính khách quan và nhất quán.
2. **5 việc cần sửa ngay (Nguyên lý Pareto 80/20):** Tập trung vào những lỗi nghiêm trọng nhất mang lại 80% kết quả cải thiện thứ hạng.
3. **Bảng Soi Chi Tiết (6 Tab):** Đọc sâu toàn bộ thẻ Meta, cây tiêu đề H1–H6, phân loại liên kết nội bộ/bên ngoài, kiểm tra thẻ alt ảnh, dữ liệu cấu trúc Schema và mô phỏng hiển thị mạng xã hội.
4. **Không báo lỗi Canonical oan:** Tự động lọc bỏ các tham số theo dõi quảng cáo (`utm_*`, `gclid`, `fbclid`, `aff_sid`...) trước khi kiểm tra canonical.
5. **Trí tuệ Nhân tạo với "Key của bạn, bạn giữ":** Kết nối trực tiếp với Anthropic (Claude), Google Gemini, OpenAI (GPT-4o), OpenRouter, DeepSeek hoặc Ollama cục bộ. Máy chủ không lưu key và không lưu dữ liệu.
6. **Bảo mật tuyệt đối:** Chống SSRF, chống Prompt Injection bằng khối mã ngăn cách ngẫu nhiên, tự động che giấu key trong mọi thông báo lỗi và log.
7. **Xuất báo cáo 1 chạm:** Tải file HTML tự chứa hoặc file Markdown cấu trúc chuẩn cho đội ngũ lập trình viên.

---

## 🚀 Hướng dẫn cài đặt và chạy trên máy cá nhân

### Yêu cầu hệ thống
- Hệ điều hành: macOS (Apple Silicon M1/M2/M3 hoặc Intel) hoặc Windows 10/11.
- Python: Phiên bản từ **3.11 trở lên**.

### Khởi chạy 1 chạm

#### Trên macOS / Linux:
```bash
git clone https://github.com/globalaffiliates247-commits/TAIO-SEO1AI.git
cd TAIO-SEO1AI
chmod +x start.sh
./start.sh
```
Trình duyệt sẽ tự động mở tại địa chỉ: `http://127.0.0.1:8770`

#### Trên Windows:
Nhấp đúp vào file `start.bat` (hoặc mở Command Prompt và gõ `start.bat`).

---

## ☁️ Hướng dẫn triển khai miễn phí lên Render (Docker)

1. **Đăng nhập vào Render:** Truy cập [render.com](https://render.com).
2. **Tạo Web Service mới:** Chọn **New +** → **Web Service** → Chọn repository `TAIO-SEO1AI`.
3. **Cấu hình dịch vụ:**
   - **Name:** `taio-seo1ai`
   - **Region:** `Singapore` (độ trễ thấp nhất cho Việt Nam).
   - **Runtime:** `Docker`
   - **Instance Type:** `Free`
   - **Health Check Path:** `/healthz`
4. **Cấu hình Biến môi trường (Environment Variables):**
   - `LOCAL_MODE`: `0`
   - `DAILY_LIMIT`: `5`
   - `MAX_PARALLEL_CHECKS`: `2`
   - `AI_DAILY_LIMIT`: `20`
   - `MAX_PARALLEL_AI`: `2`
   - `PAGESPEED_API_KEY`: *(Nhập API Key miễn phí từ Google Cloud Console để tránh bị giới hạn lượt gọi Core Web Vitals)*.
5. **Bấm Deploy:** Sau khoảng 2–3 phút, dịch vụ sẽ hoạt động trực tiếp trên tên miền của Render.

---

## 🔑 Hướng dẫn lấy key AI và bảng ước tính chi phí

Người dùng tự mang API key cá nhân, chi phí thanh toán trực tiếp cho nhà cung cấp:

| Nhà cung cấp | Nơi lấy API Key | Model khuyến nghị | Chi phí ước tính mỗi lần gọi |
|---|---|---|---|
| **Google Gemini** | [aistudio.google.com](https://aistudio.google.com/) | `gemini-2.0-flash` hoặc `gemini-1.5-flash` | **Miễn phí** (hoặc ~10đ/lần) |
| **OpenAI** | [platform.openai.com](https://platform.openai.com/) | `gpt-4o-mini` | ~20đ – 50đ / lần |
| **Anthropic** | [console.anthropic.com](https://console.anthropic.com/) | `claude-3-5-sonnet-20241022` | ~100đ – 250đ / lần |
| **DeepSeek** | [platform.deepseek.com](https://platform.deepseek.com/) | `deepseek-chat` | ~10đ – 20đ / lần |
| **Ollama** | Cài đặt trên máy cá nhân | `llama3.2` | **Hoàn toàn miễn phí 0đ** |

---

## 🧪 Kiểm thử tự động (Unit Tests)

Bộ kiểm thử bao gồm 26 bài test tự động bao quát toàn bộ 28 tiêu chí nghiệm thu:
```bash
python3 -m unittest discover tests
```

---

## 📄 Giấy phép & Ghi công

- Phát triển và hoàn thiện bởi **TAIO-Lee** cho cộng đồng doanh nghiệp số **TAIO.CLUB** ([digitalbusiness.taio.club](https://digitalbusiness.taio.club)).
- Tái sử dụng và kế thừa từ mã nguồn mở `claude-seo` (Giấy phép MIT) của tác giả **Agrici Daniel** ([github.com/AgriciDaniel/claude-seo](https://github.com/AgriciDaniel/claude-seo)).
- Giấy phép phân phối: **MIT License**.
