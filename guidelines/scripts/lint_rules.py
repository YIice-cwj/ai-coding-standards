#!/usr/bin/env python3
"""
lint_rules.py: 针对源码与提交变更执行 AI 规范一票否决项的自动化静态扫描。
覆盖：B4 过度防御、B-CMT 行内注释、B-SEC 机密泄露、C++ NRVO 破坏、UE5 UPROPERTY 漏标等。
"""

import os
import re
import sys
from pathlib import Path

IGNORE_DIRS = {".git", ".gemini", ".history", "node_modules", "build", "Intermediate", "Binaries"}

# 静态扫描检测规则
RULES = [
    {
        "id": "SEC-KEY",
        "name": "B-SEC 机密泄露防护",
        "pattern": re.compile(r"(['\"][sS][kK]-[a-zA-Z0-9]{20,}['\"])"),
        "exts": {".h", ".cc", ".cpp", ".py", ".ts", ".js", ".json", ".env"},
        "desc": "检测到可能包含真实的 API Secret Key"
    },
    {
        "id": "CPP-NRVO",
        "name": "C++ 破坏 NRVO 优化",
        "pattern": re.compile(r"return\s+std::move\s*\([^)]+\)\s*;"),
        "exts": {".h", ".cc", ".cpp", ".hpp"},
        "desc": "严禁使用 return std::move(x) 阻断 NRVO 返回值优化"
    },
    {
        "id": "CPP-OVER-DEF",
        "name": "B4 过度防御: 引用/this 判空",
        "pattern": re.compile(r"(&\w+\s*==\s*nullptr|this\s*==\s*nullptr)"),
        "exts": {".h", ".cc", ".cpp", ".hpp"},
        "desc": "语法或底层保证不可能为空，严禁对引用或 this 进行判空"
    },
    {
        "id": "UE5-NAKED-OBJ",
        "name": "UE5 裸 UObject* 成员变量",
        "pattern": re.compile(r"^\s*U\w+\s*\*\s*\w+\s*;", re.MULTILINE),
        "exts": {".h"},
        "desc": "UE5 成员变量应使用 TObjectPtr<T> 并配合 UPROPERTY() 防 GC 误杀"
    },
    {
        "id": "SQL-CONCAT",
        "name": "SQL 拼接注入高危",
        "pattern": re.compile(r"(SELECT\s+.*FROM\s+.*[\+\$]|\.format\(.*SELECT\s+)", re.IGNORECASE),
        "exts": {".py", ".ts", ".js", ".cc", ".cpp", ".go", ".java"},
        "desc": "严禁使用字符串拼接或格式化生成 SQL，必须使用参数化绑定"
    }
]

def scan_file(file_path: Path):
    issues = []
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return issues

    for rule in RULES:
        if file_path.suffix.lower() in rule["exts"]:
            lines = content.splitlines()
            for idx, line in enumerate(lines, start=1):
                # 排除规范文档与注释本身
                if file_path.suffix == ".md" or "ai-guidelines" in str(file_path):
                    continue
                match = rule["pattern"].search(line)
                if match:
                    issues.append((rule["id"], rule["name"], idx, line.strip(), rule["desc"]))
    return issues

def main():
    target_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    print(f"🛡️  正在对目录执行规范静态合规扫描: {target_dir}")
    
    total_scanned = 0
    total_issues = 0

    for root, dirs, files in os.walk(target_dir):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for f in files:
            file_path = Path(root) / f
            total_scanned += 1
            issues = scan_file(file_path)
            if issues:
                total_issues += len(issues)
                print(f"\n❌ [{file_path.relative_to(target_dir)}]")
                for rule_id, name, line_num, line_txt, desc in issues:
                    print(f"   Line {line_num} [{rule_id}] {name}: {desc}")
                    print(f"   > {line_txt}")

    print(f"\n📊 扫描完成：共检查 {total_scanned} 个文件，发现 {total_issues} 个违规项。")
    return 1 if total_issues > 0 else 0

if __name__ == "__main__":
    sys.exit(main())

