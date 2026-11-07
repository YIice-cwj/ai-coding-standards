#!/usr/bin/env python3
"""
lint_rules.py: 针对源码变更执行 AI 规范一票否决项的自动化静态扫描。
覆盖：B-CMT 单行 Doxygen、B4 过度防御、B-SEC 机密泄露、C++ NRVO、UE5 UPROPERTY、
Python 可变默认与裸 except、TS any/eval、SQL 拼接、UE5 原生线程等。
"""

import os
import re
import sys
from pathlib import Path

IGNORE_DIRS = {
    ".git", ".gemini", ".history", ".screenshots", ".trae",
    "node_modules", "build", "dist", "__pycache__",
    ".venv", "venv", "Intermediate", "Binaries", "Saved", "DerivedDataCache",
}

CPP_EXTS = {".h", ".hpp", ".hh", ".hxx", ".cc", ".cpp", ".cxx", ".c++"}
PY_EXTS = {".py"}
JS_EXTS = {".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs"}
JVM_EXTS = {".java", ".kt", ".kts"}
GO_EXTS = {".go"}
CONFIG_EXTS = {".json", ".yaml", ".yml", ".env", ".toml"}
SECRET_EXTS = CPP_EXTS | PY_EXTS | JS_EXTS | JVM_EXTS | GO_EXTS | CONFIG_EXTS | {".pem", ".key"}

# 静态扫描检测规则
RULES = [
    {
        "id": "SEC-KEY",
        "name": "B-SEC 机密泄露防护",
        "pattern": re.compile(r"['\"][sS][kK]-[a-zA-Z0-9]{20,}['\"]"),
        "exts": SECRET_EXTS,
        "desc": "检测到可能包含真实的 API Secret Key"
    },
    {
        "id": "SEC-PRIVATE-KEY",
        "name": "B-SEC 私钥泄露防护",
        "pattern": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
        "exts": SECRET_EXTS,
        "desc": "检测到私钥内容，严禁提交到仓库"
    },
    {
        "id": "SEC-AWS-KEY",
        "name": "B-SEC AWS Access Key 泄露",
        "pattern": re.compile(r"AKIA[0-9A-Z]{16}"),
        "exts": SECRET_EXTS,
        "desc": "检测到疑似 AWS Access Key"
    },
    {
        "id": "SEC-GOOGLE-KEY",
        "name": "B-SEC Google API Key 泄露",
        "pattern": re.compile(r"AIza[0-9A-Za-z_-]{35}"),
        "exts": SECRET_EXTS,
        "desc": "检测到疑似 Google API Key"
    },
    {
        "id": "CPP-NRVO",
        "name": "C++ 破坏 NRVO 优化",
        "pattern": re.compile(r"return\s+std::move\s*\([^)]+\)\s*;"),
        "exts": CPP_EXTS,
        "desc": "严禁使用 return std::move(x) 阻断 NRVO 返回值优化"
    },
    {
        "id": "CPP-OVER-DEF",
        "name": "B4 过度防御: 引用/this 判空",
        "pattern": re.compile(r"(&\w+\s*==\s*nullptr|this\s*==\s*nullptr)"),
        "exts": CPP_EXTS,
        "desc": "语法或底层保证不可能为空，严禁对引用或 this 进行判空"
    },
    {
        "id": "CPP-DOC-SINGLELINE",
        "name": "B-CMT 单行压缩 Doxygen 文档头",
        "pattern": re.compile(r"/\*\s*@brief[^\n]*\*/"),
        "exts": CPP_EXTS,
        "desc": "文档头必须使用多行分标签 Doxygen 块，禁止单行压缩"
    },
    {
        "id": "CPP-CATCH-ALL",
        "name": "C++ 裸 catch(...) 吞异常",
        "pattern": re.compile(r"catch\s*\(\s*\.\.\.\s*\)"),
        "exts": CPP_EXTS,
        "desc": "严禁裸 catch(...) 掩盖异常，必须精确捕获具体类型"
    },
    {
        "id": "UE5-NAKED-OBJ",
        "name": "UE5 裸 UObject* 成员变量",
        "pattern": re.compile(r"^\s*U[A-Z]\w*\s*\*\s*\w+\s*;"),
        "exts": {".h"},
        "desc": "UE5 成员变量应使用 TObjectPtr<T> 并配合 UPROPERTY() 防 GC 误杀"
    },
    {
        "id": "UE5-STD-THREAD",
        "name": "UE5 禁止原生 std 线程",
        "pattern": re.compile(r"std::(thread|jthread)"),
        "exts": CPP_EXTS,
        "desc": "UE5 必须使用 FAsyncTask / Async / ParallelFor，严禁绕过引擎调度器"
    },
    {
        "id": "PY-MUT-DEFAULT",
        "name": "Python 可变默认实参",
        "pattern": re.compile(r"def\s+\w+\s*\([^)]*=\s*(\[\]|\{\})"),
        "exts": PY_EXTS,
        "desc": "严禁使用 [] / {} 作为默认实参，必须用 None 哨兵并在函数体内初始化"
    },
    {
        "id": "PY-BARE-EXCEPT",
        "name": "Python 裸 except 吞异常",
        "pattern": re.compile(r"except\s*:"),
        "exts": PY_EXTS,
        "desc": "严禁裸 except:，必须精确捕获具体异常类型"
    },
    {
        "id": "TS-ANY",
        "name": "TypeScript 滥用 any",
        "pattern": re.compile(r"(:\s*any\b|\bas\s+any\b|<any>|Array<any>)"),
        "exts": JS_EXTS,
        "desc": "严禁 any，必须使用 unknown + 类型守卫收缩"
    },
    {
        "id": "JS-EVAL",
        "name": "JS/TS eval 或 new Function",
        "pattern": re.compile(r"\b(eval|new\s+Function)\s*\("),
        "exts": JS_EXTS,
        "desc": "严禁 eval / new Function 执行不可信输入"
    },
    {
        "id": "SQL-CONCAT",
        "name": "SQL 拼接注入高危",
        "pattern": re.compile(r"(SELECT\s+.*FROM\s+.*[\+\$]|\.format\(.*SELECT\s+)", re.IGNORECASE),
        "exts": {".py", ".ts", ".tsx", ".js", ".jsx", ".go", ".java", ".cc", ".cpp"},
        "desc": "严禁使用字符串拼接或格式化生成 SQL，必须使用参数化绑定"
    },
]


def scan_file(file_path: Path):
    suffix = file_path.suffix.lower()
    if suffix == ".md" or file_path.resolve() == Path(__file__).resolve():
        return []

    issues = []
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return issues

    for rule in RULES:
        if suffix not in rule["exts"]:
            continue
        for line_number, line in enumerate(content.splitlines(), start=1):
            if rule["pattern"].search(line):
                issues.append((rule["id"], rule["name"], line_number, line.strip(), rule["desc"]))
    return issues


def main() -> int:
    target_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    print(f"🛡️  正在对目录执行规范静态合规扫描: {target_dir}")

    total_scanned = 0
    total_issues = 0

    for root, dirs, files in os.walk(target_dir):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for filename in files:
            file_path = Path(root) / filename
            if file_path.suffix.lower() not in (CPP_EXTS | PY_EXTS | JS_EXTS | JVM_EXTS | GO_EXTS | CONFIG_EXTS):
                continue
            total_scanned += 1
            issues = scan_file(file_path)
            if issues:
                total_issues += len(issues)
                print(f"\n❌ [{file_path.relative_to(target_dir)}]")
                for rule_id, name, line_number, line_text, desc in issues:
                    print(f"   Line {line_number} [{rule_id}] {name}: {desc}")
                    print(f"   > {line_text}")

    print(f"\n📊 扫描完成：共检查 {total_scanned} 个文件，发现 {total_issues} 个违规项。")
    return 1 if total_issues > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
