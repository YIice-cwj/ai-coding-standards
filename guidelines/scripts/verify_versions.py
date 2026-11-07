#!/usr/bin/env python3
"""
verify_versions.py: 校验规范仓库的文件头版本与 INDEX.md 版本登记处是否一致。
零三方依赖，可直接作为 Git Pre-commit Hook 或 CI 自动化门禁。
"""

import re
import sys
from pathlib import PurePosixPath
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
INDEX_PATH = REPO_ROOT / "guidelines" / "INDEX.md"

ROW_PATTERN = re.compile(
    r"^\|\s*\[([^\]]+)\]\(([^)]+)\)\s*\|\s*\*\*(\d+\.\d+\.\d+)\*\*\s*\|\s*(\d{4}-\d{2}-\d{2})\s*\|",
    re.MULTILINE,
)
FILE_VERSION_PATTERN = re.compile(
    r"^\*\*版本\*\*: (\d+\.\d+\.\d+)  \*\*日期\*\*: (\d{4}-\d{2}-\d{2})", re.MULTILINE
)
DOMAIN_VERSION_PATTERN = re.compile(
    r"\*\*域版本\*\*: (\d+\.\d+\.\d+)  \*\*日期\*\*: (\d{4}-\d{2}-\d{2})"
)
DOMAIN_DIR_PATTERN = re.compile(r"^\d{2}-")


def parse_registry(index_text: str):
    marker = "## 四、 版本登记处"
    if marker not in index_text:
        print("❌ 未找到 INDEX.md 的版本登记处章节。")
        return []
    section = index_text.split(marker, 1)[1]
    return ROW_PATTERN.findall(section)


def read_version(path: Path, pattern: re.Pattern):
    try:
        content = path.read_text(encoding="utf-8")
    except OSError as exc:
        return None, f"无法读取: {exc}"
    match = pattern.search(content)
    if not match:
        return None, "未找到版本头"
    return match.groups(), None


def main() -> int:
    index_text = INDEX_PATH.read_text(encoding="utf-8")
    rows = parse_registry(index_text)
    if not rows:
        print("❌ 版本登记处为空或格式不匹配。")
        return 1

    failures = []
    checked_files = 0
    checked_domains = set()

    for name, link, version, date in rows:
        link_parts = PurePosixPath(link).parts
        domain_name = link_parts[0] if link_parts else ""
        target = (INDEX_PATH.parent / link).resolve()

        if DOMAIN_DIR_PATTERN.match(domain_name):
            domain_dir = REPO_ROOT / "guidelines" / domain_name
            if not domain_dir.is_dir():
                failures.append(f"[{name}] 域目录不存在: {domain_dir}")
                continue
            checked_domains.add(domain_name)
            files = sorted(domain_dir.glob("*.md"))
            if not files:
                failures.append(f"[{name}] 域目录没有 Markdown 文件: {domain_dir}")
                continue
            for path in files:
                checked_files += 1
                actual, error = read_version(path, DOMAIN_VERSION_PATTERN)
                if error or actual != (version, date):
                    failures.append(
                        f"[{name}] {path.relative_to(REPO_ROOT)}: "
                        f"文件头 {actual or error} != 登记 {(version, date)}"
                    )
            continue

        if not target.is_file():
            failures.append(f"[{name}] 登记链接目标不存在: {target}")
            continue

        checked_files += 1
        actual, error = read_version(target, FILE_VERSION_PATTERN)
        if error or actual != (version, date):
            failures.append(
                f"[{name}] {target.relative_to(REPO_ROOT)}: "
                f"文件头 {actual or error} != 登记 {(version, date)}"
            )

    all_domains = sorted(
        path.name
        for path in (REPO_ROOT / "guidelines").iterdir()
        if path.is_dir() and DOMAIN_DIR_PATTERN.match(path.name)
    )
    for domain in all_domains:
        if domain not in checked_domains:
            failures.append(f"[{domain}] 域目录未在 INDEX 版本登记处登记")

    print(f"🔍 已检查 {len(checked_domains)} 个域、{checked_files} 个文件版本头。")
    if failures:
        print(f"\n❌ 发现 {len(failures)} 处版本不一致:")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    print("✅ 完美！所有文件头版本与 INDEX 版本登记处 100% 一致。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
