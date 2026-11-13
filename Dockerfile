FROM python:3.12-slim

# Thiết lập thư mục làm việc
WORKDIR /app

# Cài đặt thư viện hệ thống cần thiết (nếu có)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Cài đặt thư viện Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép toàn bộ mã nguồn
COPY . .

# Biến môi trường mặc định cho Docker/Render
ENV PORT=8770
ENV LOCAL_MODE=0
ENV PYTHONUNBUFFERED=1

# Kiểm tra sức khoẻ container
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:${PORT}/healthz || exit 1

# Khởi chạy bằng Gunicorn: 1 worker, 4 threads, timeout 120s
CMD exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 120 wsgi:app
