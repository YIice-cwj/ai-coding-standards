#!/usr/bin/env bash
# ==============================================================================
# AI Coding Standards (ai-coding-standards) 一键安装/更新脚本
# 支持系统: macOS, Linux, WSL, Git Bash
# 仓库源: https://github.com/YIice-cwj/ai-coding-standards
# ==============================================================================

set -e

REPO_URL="https://github.com/YIice-cwj/ai-coding-standards.git"
TAR_URL="https://github.com/YIice-cwj/ai-coding-standards/archive/refs/heads/main.tar.gz"

# 终端色彩
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

echo -e "${CYAN}${BOLD}"
echo "  ╔═══════════════════════════════════════════════════════════════════╗"
echo "  ║         AI Coding Standards - 一键安装与智能部署工具              ║"
echo "  ║        https://github.com/YIice-cwj/ai-coding-standards           ║"
echo "  ╚═══════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

FORCE=0
TARGET_DIR="."

for arg in "$@"; do
    case "$arg" in
        -f|--force|-y|--yes)
            FORCE=1
            ;;
        -*)
            # 忽略其他标志
            ;;
        *)
            TARGET_DIR="$arg"
            ;;
    esac
done

mkdir -p "$TARGET_DIR"
cd "$TARGET_DIR"
ABSOLUTE_TARGET="$(pwd)"
echo -e "${BLUE}🎯 目标安装路径: ${BOLD}${ABSOLUTE_TARGET}${NC}"

# 1. 检测既有规范文件与防误触判断
EXISTING=0
if [ -f "AGENTS.md" ] || [ -d "guidelines" ]; then
    EXISTING=1
fi

if [ "$EXISTING" -eq 1 ]; then
    echo -e "${YELLOW}⚠️  检测到当前目录中已存在 [AGENTS.md] 或 [guidelines/] 目录！${NC}"
    if [ "$FORCE" -eq 1 ]; then
        echo -e "${YELLOW}⚡ 检测到强制参数 (-y/--force)，将自动备份并继续覆盖安装...${NC}"
        ACTION="1"
    else
        echo -e "${CYAN}请选择操作方式:${NC}"
        echo "  [1] 自动备份旧规范至 .guidelines_backup_<时间戳> 并全新安装 (推荐)"
        echo "  [2] 直接强制覆盖现有规范文件"
        echo "  [3] 取消退出"
        read -r -p "请输入选项 [1-3] (默认: 1): " USER_CHOICE
        USER_CHOICE="${USER_CHOICE:-1}"
        ACTION="$USER_CHOICE"
    fi

    case "$ACTION" in
        1)
            BACKUP_DIR=".guidelines_backup_$(date +%Y%m%d_%H%M%S)"
            echo -e "${BLUE}📦 正在备份旧规范到: ${BOLD}${BACKUP_DIR}${NC}"
            mkdir -p "$BACKUP_DIR"
            [ -f "AGENTS.md" ] && cp -f "AGENTS.md" "$BACKUP_DIR/" 2>/dev/null || true
            [ -d "guidelines" ] && cp -rf "guidelines" "$BACKUP_DIR/" 2>/dev/null || true
            echo -e "${GREEN}✅ 备份完成！${NC}"
            ;;
        2)
            echo -e "${YELLOW}⚠️  已选择直接覆盖。${NC}"
            ;;
        *)
            echo -e "${RED}❌ 安装已取消。${NC}"
            exit 0
            ;;
    esac
fi

# 2. 拉取最新规范资产 (优先 git，降级使用 tarball)
TMP_DIR="$(mktemp -d 2>/dev/null || mktemp -d -t 'aiguidelines')"
cleanup() {
    rm -rf "$TMP_DIR"
}
trap cleanup EXIT

echo -e "${BLUE}⬇️  正在下载最新规范资产包...${NC}"

if command -v git >/dev/null 2>&1; then
    git clone --depth 1 "$REPO_URL" "$TMP_DIR/repo" --quiet
    SRC_DIR="$TMP_DIR/repo"
elif command -v curl >/dev/null 2>&1 && command -v tar >/dev/null 2>&1; then
    mkdir -p "$TMP_DIR/repo"
    curl -fsSL "$TAR_URL" | tar -xz -C "$TMP_DIR/repo" --strip-components 1
    SRC_DIR="$TMP_DIR/repo"
else
    echo -e "${RED}❌ 系统缺少 git 或 curl+tar，无法完成下载。请先安装 git 或 curl。${NC}"
    exit 1
fi

# 3. 部署规范文件至目标工程 (统一收敛于 AGENTS.md + guidelines/)
echo -e "${BLUE}📂 正在部署核心规范到当前工作区...${NC}"

cp -f "$SRC_DIR/AGENTS.md" "$ABSOLUTE_TARGET/"
rm -rf "$ABSOLUTE_TARGET/guidelines"
cp -rf "$SRC_DIR/guidelines" "$ABSOLUTE_TARGET/"
chmod +x "$ABSOLUTE_TARGET/guidelines/scripts/"*.py 2>/dev/null || true

echo -e "\n${GREEN}${BOLD}🎉 恭喜！AI 编程规范体系已成功安装/升级至当前工程！${NC}"
echo -e "${CYAN}------------------------------------------------------------${NC}"
echo -e "  📌 核心主控入口: ${BOLD}AGENTS.md${NC} (全工具统一唯一挂载点)"
echo -e "  📚 规范知识总库: ${BOLD}guidelines/${NC} (涵盖 C++, UE5, Web前端, Python, 架构, 审查)"
echo -e "  📝 交付标准模板: ${BOLD}guidelines/templates/${NC} (L3方案计划, B8三振求助, 记忆快照)"
echo -e "  🛠️  自动化防呆脚本: ${BOLD}guidelines/scripts/${NC} (链接自检, 规则合规扫描, Prompt打包)"
echo -e "${CYAN}------------------------------------------------------------${NC}"
echo -e "${YELLOW}💡 使用方式：在任意 AI 工具（Cursor, Trae, Copilot, Claude, Windsurf）中：${NC}"
echo -e "   直接输入 ${BOLD}@AGENTS.md <你的需求>${NC}，AI 将自动探测领域并精准遵循规范！\n"
echo -e "${CYAN}------------------------------------------------------------${NC}"
echo -e "${YELLOW}💡 使用方式：在任意支持的 AI IDE（Cursor, Trae, Copilot, Claude）中：${NC}"
echo -e "   直接输入 ${BOLD}@AGENTS.md <你的需求>${NC}，AI 将自动探测领域并遵循规范！\n"
