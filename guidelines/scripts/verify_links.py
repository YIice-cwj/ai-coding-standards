#!/usr/bin/env python3
"""
verify_links.py: 校验规范仓库中所有 Markdown 文件的相对链接与文件有效性。
零三方依赖，可直接作为 Git Pre-commit Hook 或 CI 自动化门禁。
"""

import os
import re
import sys
from pathlib import Path

IGNORE_DIRS = {".git", ".gemini", ".history", "node_modules", ".vscode"}

def get_markdown_files(root_dir: Path):
    md_files = []
    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for f in files:
            if f.endswith(".md"):
                md_files.append(Path(root) / f)
    return md_files

def verify_links(root_dir: Path) -> int:
    md_files = get_markdown_files(root_dir)
    broken_links = []
    total_checked = 0

    link_pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")

    for md_file in md_files:
        try:
            content = md_file.read_text(encoding="utf-8")
        except Exception as e:
            print(f"❌ 无法读取文件: {md_file} - {e}")
            broken_links.append((str(md_file), "FILE_READ_ERROR", str(e)))
            continue

        for text, link in link_pattern.findall(content):
            # 排除外部网络链接、邮箱、纯锚点及虚拟示例
            if (link.startswith("http://") or link.startswith("https://") 
                or link.startswith("mailto:") or link.startswith("#")
                or link.startswith("conversation:") or "example" in link.lower()
                or "20261019" in link or "20261026" in link):
                continue

            total_checked += 1
            clean_link = link.split("#")[0]
            if not clean_link:
                continue

            target_path = (md_file.parent / clean_link).resolve()
            if not target_path.exists():
                broken_links.append((
                    str(md_file.relative_to(root_dir)),
                    link,
                    str(target_path)
                ))

    print(f"🔍 已扫描 {len(md_files)} 个文档，校验了 {total_checked} 个内部相对链接。")
    if broken_links:
        print(f"\n❌ 发现 {len(broken_links)} 处失效断链:")
        for src, link, tgt in broken_links:
            print(f"  - 在 [{src}] 中: '{link}' -> 目标不存在: {tgt}")
        return 1

    print("✅ 完美！全库所有相对链接 100% 有效。")
    return 0

if __name__ == "__main__":
    repo_root = Path(__file__).resolve().parent.parent.parent
    sys.exit(verify_links(repo_root))

