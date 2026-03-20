@echo off
chcp 65001 >nul
setlocal

cd /d "%~dp0"

REM 确保 MinIO 数据目录存在
if not exist "minio-data" mkdir minio-data

REM 启动 Redis（新窗口，需已安装并加入 PATH）
where redis-server >nul 2>nul
if %errorlevel% equ 0 (
    start "Redis" redis-server
    timeout /t 1 /nobreak >nul
) else (
    echo [提示] 未找到 redis-server，请确保已安装 Redis 并加入 PATH
)

REM 启动 MinIO（新窗口，需已安装并加入 PATH）
where minio >nul 2>nul
if %errorlevel% equ 0 (
    start "MinIO" minio server minio-data
    timeout /t 1 /nobreak >nul
) else (
    echo [提示] 未找到 minio，请确保已安装 MinIO 并加入 PATH
)

REM 启动应用
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
    python run.py
) else (
    echo [错误] 未找到虚拟环境 .venv，请先执行: python -m venv .venv
    pause
    exit /b 1
)

pause
