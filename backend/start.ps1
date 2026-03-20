# 启动脚本 - 启动 Redis、MinIO 后运行应用
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

# 确保 MinIO 数据目录存在
$minioData = Join-Path $PSScriptRoot "minio-data"
if (-not (Test-Path $minioData)) { New-Item -ItemType Directory -Path $minioData | Out-Null }

# 启动 Redis（新窗口，需已安装并加入 PATH）
$redis = Get-Command redis-server -ErrorAction SilentlyContinue
if ($redis) {
    Start-Process -FilePath "redis-server" -WindowStyle Normal
    Start-Sleep -Seconds 1
} else {
    Write-Host "[提示] 未找到 redis-server，请确保已安装 Redis 并加入 PATH" -ForegroundColor Yellow
}

# 启动 MinIO（新窗口，需已安装并加入 PATH）
$minio = Get-Command minio -ErrorAction SilentlyContinue
if ($minio) {
    Start-Process -FilePath "minio" -ArgumentList "server", (Resolve-Path $minioData).Path -WindowStyle Normal
    Start-Sleep -Seconds 1
} else {
    Write-Host "[提示] 未找到 minio，请确保已安装 MinIO 并加入 PATH" -ForegroundColor Yellow
}

# 启动应用
$venvPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
$runPy = Join-Path $PSScriptRoot "run.py"

if (Test-Path $venvPython) {
    & $venvPython $runPy
} else {
    Write-Host "[错误] 未找到虚拟环境 .venv，请先执行: python -m venv .venv" -ForegroundColor Red
    exit 1
}
