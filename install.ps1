# ==============================================================================
# AI Coding Standards (ai_coding_standards) PowerShell 一键安装/更新脚本
# 仓库源: https://github.com/YIice-cwj/ai_coding_standards
# ==============================================================================

[CmdletBinding()]
param (
    [string]$TargetDir = ".",
    [switch]$Force
)

$ErrorActionPreference = "Stop"
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

Write-Host "╔═══════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║         AI Coding Standards - PowerShell 一键安装工具             ║" -ForegroundColor Cyan
Write-Host "║        https://github.com/YIice-cwj/ai_coding_standards           ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

Set-Location $TargetDir
$AbsoluteTarget = Get-Location
Write-Host "🎯 目标安装路径: $AbsoluteTarget" -ForegroundColor Blue

$hasAgents = Test-Path "AGENTS.md"
$hasGuidelines = Test-Path "guidelines"

if ($hasAgents -or $hasGuidelines) {
    Write-Host "⚠️  检测到当前目录中已存在 [AGENTS.md] 或 [guidelines/] 目录！" -ForegroundColor Yellow
    
    $choice = "1"
    if ($Force) {
        Write-Host "⚡ 检测到 -Force 参数，将自动备份并继续覆盖安装..." -ForegroundColor Yellow
    } else {
        Write-Host "请选择操作方式:" -ForegroundColor Cyan
        Write-Host "  [1] 自动备份旧规范至 .guidelines_backup_<时间戳> 并全新安装 (推荐)"
        Write-Host "  [2] 直接强制覆盖现有规范文件"
        Write-Host "  [3] 取消退出"
        $inputVal = Read-Host "请输入选项 [1-3] (默认: 1)"
        if ($inputVal) { $choice = $inputVal.Trim() }
    }

    switch ($choice) {
        "1" {
            $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
            $backupDir = ".guidelines_backup_$timestamp"
            Write-Host "📦 正在备份旧规范到: $backupDir" -ForegroundColor Blue
            New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
            if (Test-Path "AGENTS.md") { Copy-Item "AGENTS.md" $backupDir -Force }
            if (Test-Path "guidelines") { Copy-Item "guidelines" $backupDir -Recurse -Force }
            Write-Host "✅ 备份完成！" -ForegroundColor Green
        }
        "2" {
            Write-Host "⚠️ 已选择直接覆盖。" -ForegroundColor Yellow
        }
        Default {
            Write-Host "❌ 安装已取消。" -ForegroundColor Red
            Exit 0
        }
    }
}

$tempBase = Join-Path $env:TEMP ("ai_guidelines_" + [System.Guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $tempBase -Force | Out-Null

try {
    Write-Host "⬇️  正在下载最新规范资产包..." -ForegroundColor Blue
    $zipPath = Join-Path $tempBase "repo.zip"
    Invoke-WebRequest -Uri "https://github.com/YIice-cwj/ai_coding_standards/archive/refs/heads/main.zip" -OutFile $zipPath
    Expand-Archive -Path $zipPath -DestinationPath $tempBase -Force
    $srcDir = Join-Path $tempBase "ai_coding_standards-main"

    Write-Host "📂 正在部署核心规范到当前工作区..." -ForegroundColor Blue
    Copy-Item (Join-Path $srcDir "AGENTS.md") $AbsoluteTarget -Force
    if (Test-Path "guidelines") { Remove-Item "guidelines" -Recurse -Force }
    Copy-Item (Join-Path $srcDir "guidelines") $AbsoluteTarget -Recurse -Force

    Write-Host "`n🎉 恭喜！AI 编程规范体系已成功安装/升级至当前工程！" -ForegroundColor Green
    Write-Host "💡 使用方式：在 Cursor / Trae / Copilot / Claude 中输入 @AGENTS.md 即可驱动！`n" -ForegroundColor Yellow
}
finally {
    if (Test-Path $tempBase) { Remove-Item $tempBase -Recurse -Force -ErrorAction SilentlyContinue }
}

