# ============================================================
# corp-knowledge-agent 一键演示脚本 (PowerShell)
#
# 用法 (在项目根目录下):
#   .\demo\run_all.ps1           # 默认 mock 模式
#   .\demo\run_all.ps1 -Real     # real 模式 (从 .env 读 LLM_API_KEY)
#   .\demo\run_all.ps1 -Real -Single "年假怎么算"   # 单问题
#
# 依赖: Python 3.11+, pip install -r requirements.txt
# ============================================================

param(
    [switch]$Real = $false,
    [string]$Single = "",
    [switch]$Seed = $false
)

$ErrorActionPreference = "Stop"

# 切到脚本所在目录的上一级 (项目根)
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
Push-Location $ProjectRoot

try {
    Write-Host "===================================================" -ForegroundColor Cyan
    Write-Host " corp-knowledge-agent demo runner" -ForegroundColor Cyan
    Write-Host " 模式: $(if ($Real) {'real'} else {'mock'})" -ForegroundColor Cyan
    if ($Single) { Write-Host " 单问题: $Single" -ForegroundColor Cyan }
    Write-Host "===================================================" -ForegroundColor Cyan
    Write-Host ""

    # 1. 设置 LLM_MODE
    if ($Real) {
        $env:LLM_MODE = "real"
        # 如果 .env 不存在，提醒用户
        if (-not (Test-Path ".env")) {
            Write-Host "⚠️  没找到 .env 文件，请先复制 .env.example 并填入 API key:" -ForegroundColor Yellow
            Write-Host "   cp .env.example .env  (PowerShell: Copy-Item .env.example .env)" -ForegroundColor Yellow
            Write-Host "   然后编辑 .env 填入 LLM_API_KEY" -ForegroundColor Yellow
            exit 1
        }
    } else {
        $env:LLM_MODE = "mock"
    }

    # 2. (可选) 初始化 SQLite
    if ($Seed -or -not (Test-Path "data/employees.db")) {
        if (-not (Test-Path "data/employees.db")) {
            Write-Host "→ 初始化 SQLite ..." -ForegroundColor Gray
        }
        python -m data.seed_db
        if ($LASTEXITCODE -ne 0) { throw "data.seed_db failed" }
    }

    # 3. 跑 demo
    if ($Single) {
        python demo/run_demo.py --q $Single
    } else {
        python demo/run_demo.py --all
    }

    if ($LASTEXITCODE -ne 0) { throw "run_demo.py failed" }

    Write-Host ""
    Write-Host "✅ Demo 跑完" -ForegroundColor Green
}
finally {
    Pop-Location
}