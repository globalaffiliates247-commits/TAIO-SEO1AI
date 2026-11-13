@echo off
REM ==============================================================================
REM start.bat - Khoi dong 1 cham cho TAIO SEO Check tren Windows
REM ==============================================================================

chcp 65001 >nul
echo ================================================================
echo           Khoi dong TAIO SEO Check (TAIO.CLUB)...
echo ================================================================

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [Loi] Khong tim thay Python tren he thong.
    echo Vui long truy cap https://www.python.org/downloads/ va cai dat Python 3.11 tro len.
    pause
    exit /b 1
)

python -c "import flask, bs4, lxml, requests" >nul 2>nul
if %errorlevel% neq 0 (
    echo Dang cai dat cac thu vien can thiet...
    python -m pip install -q -r requirements.txt
)

echo Dang khoi chay tai http://127.0.0.1:8770...
python app_web.py
pause
