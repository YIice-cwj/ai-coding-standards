@echo off
chcp 65001 >nul
:: ==============================================================================
:: AI Coding Standards (ai-coding-standards) Windows 一键安装/更新脚本
:: 仓库源: https://github.com/YIice-cwj/ai-coding-standards
:: ==============================================================================

setlocal enabledelayedexpansion

echo =====================================================================
echo          AI Coding Standards - Windows 一键安装与智能部署工具
echo         https://github.com/YIice-cwj/ai-coding-standards
echo =====================================================================
echo.

set "TARGET_DIR=%~dp0"
if not "%~1"=="" set "TARGET_DIR=%~1"
cd /d "%TARGET_DIR%"

echo [INFO] 目标安装路径: %CD%
echo.

:: 1. 检测既有规范文件与防误触判断
set "EXISTING=0"
if exist "AGENTS.md" set "EXISTING=1"
if exist "guidelines" set "EXISTING=1"

if "%EXISTING%"=="1" (
    echo [WARN] 检测到当前目录中已存在 [AGENTS.md] 或 [guidelines/] 目录！
    echo.
    echo 请选择操作方式:
    echo   [1] 自动备份旧规范至 .guidelines_backup_时间戳 并全新安装 (推荐)
    echo   [2] 直接强制覆盖现有规范文件
    echo   [3] 取消退出
    echo.
    set /p USER_CHOICE="请输入选项 [1-3] (默认: 1): "
    if "!USER_CHOICE!"=="" set "USER_CHOICE=1"

    if "!USER_CHOICE!"=="3" (
        echo [INFO] 安装已取消。
        goto :END
    )

    if "!USER_CHOICE!"=="1" (
        for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value 2^>nul') do set dt=%%I
        if "!dt!"=="" set dt=%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%
        set dt=!dt: =0!
        set "BACKUP_DIR=.guidelines_backup_!dt:~0,15!"

        echo [INFO] 正在备份旧规范到: !BACKUP_DIR!
        mkdir "!BACKUP_DIR!" >nul 2>&1
        if exist "AGENTS.md" copy /y "AGENTS.md" "!BACKUP_DIR!\" >nul 2>&1
        if exist "guidelines" xcopy /e /i /y "guidelines" "!BACKUP_DIR!\guidelines\" >nul 2>&1
        echo [OK] 备份已完成。
    )
)

:: 2. 拉取最新资产包 (优先 git，降级调用 PowerShell 解压 tarball/zip)
set "TEMP_DIR=%TEMP%\ai_guidelines_%RANDOM%"
mkdir "%TEMP_DIR%" >nul 2>&1

echo [INFO] 正在拉取最新规范资产...
where git >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    git clone --depth 1 https://github.com/YIice-cwj/ai-coding-standards.git "%TEMP_DIR%\repo" --quiet
    set "SRC_DIR=%TEMP_DIR%\repo"
) else (
    echo [INFO] 本地未检测到 git，正在使用 PowerShell 下载压缩包...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://github.com/YIice-cwj/ai-coding-standards/archive/refs/heads/main.zip' -OutFile '%TEMP_DIR%\repo.zip'; Expand-Archive -Path '%TEMP_DIR%\repo.zip' -DestinationPath '%TEMP_DIR%'"
    set "SRC_DIR=%TEMP_DIR%\ai-coding-standards-main"
    if not exist "!SRC_DIR!\AGENTS.md" set "SRC_DIR=%TEMP_DIR%\ai_coding_standards-main"
)

if not exist "!SRC_DIR!\AGENTS.md" (
    echo [ERROR] 下载资产包失败，请检查网络或 GitHub 连通性。
    goto :CLEANUP
)

:: 3. 部署规范文件至目标工程 (统一收敛于 AGENTS.md + guidelines\)
echo [INFO] 正在部署核心规范到当前工作区...
copy /y "!SRC_DIR!\AGENTS.md" "%CD%\" >nul
if exist "guidelines" rmdir /s /q "guidelines"
xcopy /e /i /y "!SRC_DIR!\guidelines" "%CD%\guidelines\" >nul

echo.
echo =====================================================================
echo  [OK] 恭喜！AI 编程规范体系已成功安装/升级至当前工程！
echo =====================================================================
echo   * 核心主控入口: AGENTS.md (全平台统一唯一挂载点)
echo   * 规范知识总库: guidelines\ (C++, UE5, Web, Python, 通用架构, 审查)
echo   * 交付标准模板: guidelines\templates\ (L3计划, B8三振求助, 记忆快照)
echo   * 自动化脚本库: guidelines\scripts\ (链接自检, 规则合规扫描)
echo =====================================================================
echo 使用方法: 在 Cursor / Trae / Copilot / Claude 中输入 @AGENTS.md 即可驱动！
echo.

:CLEANUP
if exist "%TEMP_DIR%" rmdir /s /q "%TEMP_DIR%" >nul 2>&1

:END
pause

