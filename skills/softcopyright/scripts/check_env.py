# -*- coding: utf-8 -*-
"""环境自检：确认生成软著材料所需工具与中文字体是否就绪。

输出 <work>/build/environment.json 与 environment.md；缺硬性依赖时 exit 1。
Usage: python check_env.py
"""
import json
import os
import platform
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C

FONTS = [
    (r"C:\Windows\Fonts\simsun.ttc", "宋体 SimSun"),
    (r"C:\Windows\Fonts\simhei.ttf", "黑体 SimHei"),
    (r"C:\Windows\Fonts\consola.ttf", "Consolas 等宽"),
]
CHROME_CANDIDATES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
]


def module_ok(name):
    try:
        __import__(name)
        return True
    except Exception:
        return False


def cmd_version(cmd, args=("--version",)):
    exe = shutil.which(cmd)
    if not exe:
        return None, None
    try:
        out = subprocess.run([exe, *args], capture_output=True, text=True, timeout=20)
        first = (out.stdout or out.stderr or "").strip().splitlines()
        return exe, (first[0] if first else "")
    except Exception as e:
        return exe, f"error: {e}"


def main():
    report = {"platform": platform.platform(), "python": platform.python_version(), "checks": [], "hard_fail": []}

    def add(name, ok, detail, hard=False):
        report["checks"].append({"name": name, "ok": bool(ok), "detail": detail, "hard": hard})
        if hard and not ok:
            report["hard_fail"].append(name)

    # Python 与依赖
    major, minor = sys.version_info[:2]
    add("Python >= 3.10", (major, minor) >= (3, 10), f"{major}.{minor}", hard=True)
    for mod in ["docx", "pypdf", "PIL"]:
        add(f"python 模块 {mod}", module_ok(mod), "import ok" if module_ok(mod) else "缺失，请先安装", hard=(mod != "PIL"))
    add("python-docx 可用于申请表底稿", module_ok("docx"), "export DOCX")
    add("pypdf 可用于页数/行数校验", module_ok("pypdf"), "verify PDF")

    # xelatex
    exe, ver = cmd_version("xelatex")
    add("xelatex（TeX Live）", bool(exe), f"{exe} | {ver}" if exe else "未找到 xelatex，无法生成中文 PDF", hard=True)

    # 中文字体（Windows 必需）
    if os.name == "nt":
        for path, label in FONTS:
            add(f"字体 {label}", os.path.exists(path), path, hard=(label.startswith("宋体") or "Consolas" in label))
    else:
        add("中文字体检查", True, "非 Windows，跳过（请自行确认 fontspec 可用字体）")

    # Chrome/Edge（截图用）
    chrome = next((p for p in CHROME_CANDIDATES if os.path.exists(p)), None)
    add("Chrome/Edge（实拍截图）", bool(chrome), chrome or "未找到，截图需手动准备", hard=False)

    # git（追溯提交号）
    gexe, gver = cmd_version("git", ("--version",))
    add("git", bool(gexe), gver or "未找到", hard=False)

    # 图像工具
    add("Pillow（截图裁切/压缩）", module_ok("PIL"), "ok" if module_ok("PIL") else "缺失", hard=False)

    os.makedirs(C.BUILD, exist_ok=True)
    out = os.path.join(C.BUILD, "environment.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    md = ["# 环境检查", "", f"- 平台：{report['platform']}", f"- Python：{report['python']}", "", "| 检查项 | 结果 | 详情 |", "| --- | --- | --- |"]
    for c in report["checks"]:
        mark = "✅" if c["ok"] else ("❌" if c["hard"] else "⚠️")
        md.append(f"| {c['name']} | {mark} | {c['detail']} |")
    if report["hard_fail"]:
        md += ["", "**硬性依赖缺失：" + "、".join(report["hard_fail"]) + "**"]
    with open(os.path.join(C.BUILD, "environment.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(md) + "\n")

    for c in report["checks"]:
        print(("OK   " if c["ok"] else ("FAIL " if c["hard"] else "WARN ")) + c["name"] + " | " + c["detail"])
    print("report:", out)
    if report["hard_fail"]:
        print("缺硬性依赖:", ", ".join(report["hard_fail"]))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
