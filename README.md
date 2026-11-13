# TAIO SEO Check — Kiểm Tra Sức Khoẻ SEO Website Toàn Diện

<p align="center">
  <strong>Một sản phẩm thuộc hệ sinh thái <a href="https://digitalbusiness.taio.club" target="_blank">TAIO.CLUB</a></strong><br>
  <em>Dán 1 đường link → nhận điểm SEO 0–100, 5 việc cần sửa ngay, bảng soi chi tiết meta/liên kết/ảnh/schema/mạng xã hội, hoàn toàn bằng tiếng Việt. Có AI gợi ý nếu bạn nhập API Key riêng.</em>
</p>

---

## 🌟 Điểm Nổi Bật

- 🎯 **Đánh giá chuẩn xác bằng 24 luật cố định:** Phân tích toàn diện 4 nhóm: Kỹ thuật, Nội dung cơ bản, Dữ liệu cấu trúc Schema, và Tốc độ trải nghiệm thực tế (Google Core Web Vitals).
- ⚡ **Nguyên lý Pareto 80/20:** Chỉ ra đúng 5 việc quan trọng nhất cần sửa ngay để cải thiện thứ hạng tìm kiếm, kèm hướng dẫn cụ thể dễ hiểu.
- 🔍 **Bảng Soi chi tiết 6 Tab (F9):** Đọc trọn vẹn thông tin Meta, cây phân cấp tiêu đề H1–H6, danh sách liên kết nội bộ/ngoài, hình ảnh (kiểm tra thẻ alt), khối JSON-LD và xem trước bài đăng khi chia sẻ lên mạng xã hội.
- 🤖 **Kết nối Trí tuệ Nhân tạo Độc lập (BYOK):** Người dùng tự nhập API Key riêng (OpenAI, Claude, Gemini, DeepSeek, OpenRouter hoặc Ollama máy cá nhân). AI hỗ trợ viết lại Title/Meta Description tối ưu và giải thích lỗi theo ngữ cảnh nền tảng website (WordPress, Shopify, Haravan, Sapo...).
- 🔒 **Quyền riêng tư tối đa ("Key của bạn, bạn giữ"):** Key chỉ lưu trên trình duyệt của bạn (sessionStorage/localStorage). Hệ thống tuyệt đối không lưu trữ, không ghi log hay chia sẻ API Key. Điểm số SEO 100% độc lập, AI không tham gia chấm điểm.
- 📊 **Xuất báo cáo linh hoạt:** Tải báo cáo HTML tự chứa (sẵn sàng in ra PDF) hoặc tải file Markdown phục vụ công việc kỹ thuật.
- 💰 **Chi phí máy chủ 0đ:** Tối ưu hoá cực nhẹ, vận hành mượt mà trên gói Render Free hoặc máy tính cá nhân.

---

## 🚀 Hướng Dẫn Cài Đặt & Chạy Trên Máy Cá Nhân

### Yêu cầu hệ thống:
- Hệ điều hành: macOS (tối ưu cho Apple Silicon M1/M2/M3 và Intel), Windows 10/11 hoặc Linux.
- **Python >= 3.11** (nếu máy chưa có, tải bản cài đặt chính thức tại [python.org/downloads](https://www.python.org/downloads/)).

### Cách 1: Khởi chạy nhanh bằng Script tự động

**Trên macOS / Linux:**
```bash
# Cấp quyền thực thi và khởi chạy
chmod +x start.sh
./start.sh
```

**Trên Windows:**
- Nhấp đúp chuột vào tệp `start.bat` (hoặc mở Command Prompt và gõ `start.bat`).

Script sẽ tự động kiểm tra phiên bản Python, khởi tạo môi trường ảo `.venv`, cài đặt các thư viện cần thiết và mở trình duyệt tại địa chỉ `http://127.0.0.1:8770`.

### Cách 2: Chạy thủ công bằng Terminal

```bash
# 1. Tạo môi trường ảo
python3 -m venv .venv
source .venv/bin/activate   # Trên Windows: .venv\Scripts\activate

# 2. Cài đặt thư viện
pip install -r requirements.txt

# 3. Chạy ứng dụng
python app_web.py
```

---

## ☁️ Hướng Dẫn Triển Khai Lên Render (Gói Free)

Dự án đã cấu hình sẵn sàng tệp `Dockerfile` và `render.yaml` để bạn đưa lên máy chủ Render miễn phí:

1. **Đưa mã nguồn lên GitHub:** Đẩy toàn bộ repo vào tài khoản GitHub của bạn.
2. **Tạo Web Service trên Render:**
   - Đăng nhập vào [Render.com](https://render.com/).
   - Chọn **New +** → **Blueprint** → Chọn repository GitHub của bạn.
   - Render sẽ tự động nhận diện cấu hình từ `render.yaml`.
3. **Cấu hình biến môi trường (Environment Variables):**
   - `PORT`: `10000` (Render tự cấu hình).
   - `LOCAL_MODE`: `0` (Chế độ máy chủ bảo mật).
   - `PAGESPEED_API_KEY`: *(Tuỳ chọn)* Nhập API Key miễn phí từ Google Cloud để đo tốc độ mượt mà không bị giới hạn.
4. **Health Check:** Đường dẫn kiểm tra trạng thái máy chủ là `/healthz`.

---

## 🔑 Hướng Dẫn Lấy API Key & Dự Toán Chi Phí AI

### 1. Google PageSpeed Insights API Key (Miễn phí 100%)
- **Mục đích:** Đo lường chỉ số Core Web Vitals (LCP, INP, CLS) và điểm hiệu năng mobile.
- **Cách lấy:** Truy cập [Google Cloud Console](https://console.cloud.google.com/), bật "PageSpeed Insights API" và tạo API Key. Đặt vào biến `PAGESPEED_API_KEY`. Nếu để trống, công cụ vẫn hoạt động nhưng có thể bị Google giới hạn số lượt kiểm tra mỗi phút.

### 2. API Key Trí Tuệ Nhân Tạo (Tuỳ chọn cho F10, F11, F12)
Công cụ hỗ trợ các nhà cung cấp AI phổ biến nhất:
- **Google Gemini:** Miễn phí hoặc chi phí cực thấp qua [Google AI Studio](https://aistudio.google.com/).
- **OpenAI (GPT-4o-mini):** Khoảng 0.15$ / 1 triệu tokens (khoảng 30–50 VNĐ cho mỗi lần tạo gợi ý).
- **Anthropic Claude (Claude 3.5 Sonnet / Haiku):** Đăng ký tại [console.anthropic.com](https://console.anthropic.com/).
- **DeepSeek:** Chi phí tiết kiệm qua [platform.deepseek.com](https://platform.deepseek.com/).
- **OpenRouter:** Dùng chung cho hàng chục mô hình khác nhau tại [openrouter.ai](https://openrouter.ai/).
- **Ollama / LM Studio (Chạy trên máy cá nhân):** Hoàn toàn miễn phí, không tốn chi phí API, hoạt động offline trên máy có `LOCAL_MODE=1`.

---

## 📁 Cấu Trúc Thư Mục Dự Án

```
TAIO-SEO1AI/
├─ app_web.py               # Điểm khởi chạy trên máy cá nhân (LOCAL_MODE=1)
├─ wsgi.py                  # Điểm khởi chạy máy chủ Gunicorn (LOCAL_MODE=0)
├─ version.json             # Phiên bản và build stamp
├─ core/
│  ├─ collect.py            # Thu thập 4 nguồn dữ liệu song song trong bộ nhớ
│  ├─ url_tools.py          # Chuẩn hoá URL, bóc tách tham số quảng cáo UTM/Gclid
│  ├─ tracking_params.json  # Danh sách tham số theo dõi (sửa không cần đụng code)
│  ├─ extract_details.py    # Dựng chi tiết 6 tab: Tiêu đề, Liên kết, Ảnh, Schema, MXH
│  ├─ cms_detect.py         # Nhận diện nền tảng website (WordPress, Shopify, Haravan...)
│  ├─ registry.py           # Danh mục 24 luật kiểm tra SEO và trọng số
│  ├─ score.py              # Thuật toán tính điểm nhóm và điểm tổng 0–100
│  └─ top_fixes.py          # Chọn lọc 5 việc cần sửa ngay (Pareto 80/20)
├─ checks/                  # Triển khai các hàm kiểm tra theo 4 nhóm
├─ ai/                      # Module điều phối AI, prompt isolation, chống Prompt Injection
├─ config/                  # Cấu hình providers.json, cms_signatures.json
├─ messages/vi.json         # Toàn bộ câu chữ hiển thị tiếng Việt
├─ vendor/claude_seo/       # Kế thừa từ mã nguồn mở Claude-seo (MIT)
├─ web/                     # Server Flask, middleware bảo mật CSP, rate limiting, UI static
├─ tests/                   # Bộ kiểm thử tự động toàn diện (T1–T28)
├─ Dockerfile, render.yaml  # Cấu hình container và triển khai cloud
├─ start.sh, start.bat      # Script khởi chạy 1-click
└─ README.md, PRODUCT.md, CHANGELOG.md, BUILD_SPEC.md
```

---

## 🛡️ Cam Kết Bảo Mật & Đạo Đức Dữ Liệu

1. **Không lưu trữ dữ liệu:** URL kiểm tra, nội dung HTML và báo cáo được phân tích trực tiếp trong RAM và giải phóng ngay sau khi phản hồi; không lưu trữ cơ sở dữ liệu.
2. **Bảo vệ API Key:** API Key của người dùng không bao giờ được ghi log hay chuyển tiếp đến bất kỳ máy chủ bên thứ ba nào ngoài nhà cung cấp AI do người dùng lựa chọn.
3. **Chống tấn công XSS & Prompt Injection:** Dữ liệu ngoại vi được kiểm soát nghiêm ngặt qua Content-Security-Policy, render an toàn qua `textContent` và cách ly dữ liệu trong các khối mã ngẫu nhiên khi gửi vào AI.

---

## 📜 Ghi Công & Bản Quyền

- Dự án được phát triển bởi **TAIO-Lee** cho hệ sinh thái **TAIO.CLUB** (`digitalbusiness.taio.club`).
- Phần lõi phân tích kế thừa và phát triển từ dự án mã nguồn mở **Claude-seo** của tác giả **Agrici Daniel** theo giấy phép MIT (kèm theo trong `vendor/claude_seo/LICENSE`).
- Bản quyền © 2026 TAIO.CLUB. Phát hành theo Giấy phép MIT.
