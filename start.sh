#!/usr/bin/env bash
# ==============================================================================
# start.sh - Khởi động 1 chạm cho TAIO SEO Check trên macOS và Linux
# ==============================================================================

set -e

echo "================================================================"
echo "          Khởi động TAIO SEO Check (TAIO.CLUB)...               "
echo "================================================================"

# 1. Kiểm tra sự tồn tại của python3
if ! command -v python3 &> /dev/null; then
    echo "❌ Lỗi: Không tìm thấy python3 trên máy tính của bạn."
    echo ""
    echo "Hướng dẫn cài đặt:"
    echo "1. Truy cập https://www.python.org/downloads/ để tải bản cài đặt Python 3.11 trở lên."
    echo "2. Chạy file cài đặt và nhớ tích chọn 'Add Python to PATH'."
    echo "3. Mở lại Terminal và chạy lại lệnh: ./start.sh"
    exit 1
fi

# 2. Kiểm tra phiên bản Python >= 3.11
PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)

if [ "$MAJOR" -lt 3 ] || { [ "$MAJOR" -eq 3 ] && [ "$MINOR" -lt 11 ]; }; then
    echo "❌ Lỗi: Phiên bản Python hiện tại ($PYTHON_VERSION) quá cũ."
    echo "Công cụ yêu cầu Python từ 3.11 trở lên để đảm bảo khả năng tương thích."
    echo ""
    echo "Hướng dẫn nâng cấp:"
    echo "1. Vào trang web chính thức: https://www.python.org/downloads/"
    echo "2. Tải phiên bản Python mới nhất cho hệ điều hành của bạn."
    echo "3. Cài đặt và chạy lại: ./start.sh"
    exit 1
fi

echo "✓ Đã tìm thấy Python $PYTHON_VERSION"

# 3. Kiểm tra và cài đặt thư viện cần thiết nếu thiếu
python3 -c "import flask, bs4, lxml, requests" 2>/dev/null || {
    echo "⏳ Đang cài đặt các thư viện cần thiết (Flask, BeautifulSoup4, lxml, requests)..."
    python3 -m pip install -q -r requirements.txt
}

# 4. Khởi chạy ứng dụng web
echo "🚀 Đang khởi động máy chủ tại http://127.0.0.1:8770..."
python3 app_web.py
