# -*- coding: utf-8 -*-
"""生成软著「源程序文档」：
  1) 全文版 TeX/PDF（全部自研源代码，每页固定 60 行）
  2) 申报 60 页版 TeX/PDF（前 30 页 + 后 30 页，页码 1-60 连续）
  3) 文件清单 CSV、统计信息 JSON、索引 Markdown

每页 60 行 >= 版权中心要求的 50 行/页；页眉含软件全称与版本号，页脚页码连续。
"""
import csv
import json
import math
import os
import re
import sys
import unicodedata

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C

LINES_PER_PAGE = 60
WRAP_COL = 118
CONT_INDENT = "    "

# ---- 文件选取与排序 ----
INCLUDE_EXT = {".py", ".ts", ".tsx", ".css"}
EXCLUDE_DIR_PARTS = {"node_modules", "__pycache__", ".venv", "dist", "build", ".pytest_cache"}
EXCLUDE_NAME_PATTERNS = (
    r"\.test\.tsx?$", r"\.spec\.tsx?$", r"^setup\.ts$", r"\.d\.ts$",
)

# 后端优先：入口 -> 基础设施 -> API -> 业务功能；前端：入口 -> 共享层 -> 功能层
BACKEND_PRIORITY = [
    "backend/app/main.py",
    "backend/app/__init__.py",
]
BACKEND_DIR_PRIORITY = [
    "backend/app/core/",
    "backend/app/shared/",
    "backend/app/api/",
    "backend/app/features/screening/",
    "backend/app/features/squat/",
    "backend/migrations/versions/",
]
FRONTEND_PRIORITY = [
    "frontend/src/main.tsx",
    "frontend/src/App.tsx",
    "frontend/src/vite-env.d.ts",
]
FRONTEND_DIR_PRIORITY = [
    "frontend/src/shared/api/",
    "frontend/src/shared/config/",
    "frontend/src/shared/i18n/",
    "frontend/src/shared/types/",
    "frontend/src/shared/components/",
    "frontend/src/shared/layout/",
    "frontend/src/features/",
]


def is_excluded(rel):
    parts = rel.replace("\\", "/").split("/")
    if any(p in EXCLUDE_DIR_PARTS for p in parts):
        return True
    name = parts[-1]
    for pat in EXCLUDE_NAME_PATTERNS:
        if re.search(pat, name):
            return True
    if "/tests/" in "/" + rel.replace("\\", "/"):
        return True
    return False


def collect_files():
    root = C.REPO_ROOT
    picked = []
    for base, _, files in os.walk(root):
        for fn in files:
            ext = os.path.splitext(fn)[1].lower()
            if ext not in INCLUDE_EXT:
                continue
            abs_path = os.path.join(base, fn)
            rel = os.path.relpath(abs_path, root).replace("\\", "/")
            if is_excluded(rel):
                continue
            # 只收 backend/app、backend/migrations/versions、frontend/src
            if not (rel.startswith("backend/app/") or rel.startswith("backend/migrations/versions/")
                    or rel.startswith("frontend/src/")):
                continue
            picked.append(rel)

    def sort_key(rel):
        # 先按后端/前端分组（保证「程序开头」是后端入口、「程序结尾」是前端功能层），组内再按优先级
        if rel in BACKEND_PRIORITY:
            return (0, 0, BACKEND_PRIORITY.index(rel), rel)
        if rel in FRONTEND_PRIORITY:
            return (1, 0, FRONTEND_PRIORITY.index(rel), rel)
        if rel.startswith("backend/"):
            for i, pref in enumerate(BACKEND_DIR_PRIORITY):
                if rel.startswith(pref):
                    return (0, 1 + i, 0, rel)
            return (0, 90, 0, rel)
        if rel.startswith("frontend/"):
            for i, pref in enumerate(FRONTEND_DIR_PRIORITY):
                if rel.startswith(pref):
                    return (1, 1 + i, 0, rel)
            return (1, 90, 0, rel)
        return (2, 0, 0, rel)

    return sorted(picked, key=sort_key)


# ---- 文本规范化 ----
def clean_line(line):
    line = line.replace("\t", "    ")
    line = "".join(ch for ch in line if ch == " " or ord(ch) >= 32)
    line = "".join(ch if ord(ch) <= 0xFFFF else "?" for ch in line)
    return line.rstrip()


def display_width(s):
    w = 0
    for ch in s:
        w += 2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1
    return w


def wrap_line(line):
    if display_width(line) <= WRAP_COL:
        return [line]
    out, cur, w = [], "", 0
    limit = WRAP_COL
    for ch in line:
        cw = 2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1
        if w + cw > limit:
            out.append(cur)
            cur, w = CONT_INDENT, display_width(CONT_INDENT)
            limit = WRAP_COL
        cur += ch
        w += cw
    if cur.strip():
        out.append(cur)
    return out


TEX_MAP = {
    "\\": r"\textbackslash{}",
    "{": r"\{",
    "}": r"\}",
    "$": r"\$",
    "&": r"\&",
    "#": r"\#",
    "_": r"\_",
    "%": r"\%",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}


def tex_escape(s):
    return "".join(TEX_MAP.get(ch, ch) for ch in s)


def comment_marker(rel):
    return "#" if rel.endswith(".py") else "//"


def build_lines(files):
    """返回 (all_lines, per_file_counts)。"""
    all_lines = []
    counts = []
    for rel in files:
        abs_path = os.path.join(C.REPO_ROOT, rel.replace("/", os.sep))
        with open(abs_path, "r", encoding="utf-8", errors="replace") as f:
            raw = f.read()
        if raw.startswith("\ufeff"):
            raw = raw[1:]
        marker = comment_marker(rel)
        sep = f"{marker} ==================== {rel} ===================="
        src_lines = raw.splitlines()
        expanded = [sep]
        for ln in src_lines:
            cleaned = clean_line(ln)
            if not cleaned.strip():
                # 软著要求程序每页不少于 50 行：剔除空行，保证每页全部为有效代码行
                continue
            expanded.extend(wrap_line(cleaned))
        expanded.append(marker + " ==================== end " + rel + " ====================")
        counts.append({"path": rel, "source_lines": len(src_lines), "doc_lines": len(expanded)})
        all_lines.extend(expanded)
    return all_lines, counts


PREAMBLE = r"""\documentclass[10.5pt]{ctexart}
\usepackage[a4paper,top=15mm,bottom=12mm,left=12mm,right=12mm]{geometry}
\usepackage{fancyhdr}
\usepackage{fontspec}
\setmonofont{Consolas}
\setCJKmonofont{SimSun}
\setCJKmainfont{SimSun}
\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\fontsize{8pt}{9.5pt}\selectfont %(HEADER)s}
\fancyhead[R]{\fontsize{8pt}{9.5pt}\selectfont 第 \thepage{} 页}
\renewcommand{\headrulewidth}{0.2pt}
\renewcommand{\footrulewidth}{0pt}
\setlength{\parindent}{0pt}
\setlength{\parskip}{0pt}
\setlength{\headheight}{13pt}
\newenvironment{codebox}
  {\begin{minipage}[t][250mm][t]{\textwidth}\raggedright\ttfamily\fontsize{7.5pt}{11.6pt}\selectfont\vspace{0pt}}
  {\end{minipage}}
\begin{document}
"""

PAGE_OPEN = r"\begin{codebox}" "\n"
PAGE_CLOSE = "\\end{codebox}\n\\clearpage\n"
END_DOC = "\\end{document}\n"


def render_pages_tex(pages, header):
    parts = [PREAMBLE % {"HEADER": tex_escape(header)}]
    for page in pages:
        parts.append(PAGE_OPEN)
        for line in page:
            if line.strip():
                parts.append(tex_escape(line) + "\\par\n")
            else:
                parts.append("\\hbox{}\\par\n")
        parts.append(PAGE_CLOSE)
    parts.append(END_DOC)
    return "".join(parts)


def chunk(pages, size):
    return [pages[i:i + size] for i in range(0, len(pages), size)]


def main():
    files = collect_files()
    if not files:
        raise SystemExit("no source files selected")

    all_lines, counts = build_lines(files)

    # 裁掉不足一整页的尾部，使每页（含申报版最后一页）都是满 60 行有效代码
    tail = len(all_lines) % LINES_PER_PAGE
    trimmed = 0
    if tail:
        trimmed = tail
        all_lines = all_lines[:-tail]

    pages = chunk(all_lines, LINES_PER_PAGE)
    total_pages = len(pages)

    # 申报 60 页：前 30 页 + 后 30 页
    if total_pages <= 60:
        submit_pages = pages
    else:
        submit_pages = pages[:30] + pages[-30:]

    os.makedirs(C.BUILD_SOURCE, exist_ok=True)
    os.makedirs(C.OUT, exist_ok=True)

    header = C.HEADER_NAME
    full_tex = os.path.join(C.BUILD_SOURCE, "source_full.tex")
    submit_tex = os.path.join(C.BUILD_SOURCE, "source_submit_60p.tex")
    with open(full_tex, "w", encoding="utf-8", newline="\n") as f:
        f.write(render_pages_tex(pages, header))
    with open(submit_tex, "w", encoding="utf-8", newline="\n") as f:
        f.write(render_pages_tex(submit_pages, header))

    # 清单与统计
    with open(os.path.join(C.BUILD_SOURCE, "source_file_list.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["序号", "文件路径", "源码行数", "文档行数(含折行/分隔)"])
        for i, item in enumerate(counts, 1):
            w.writerow([i, item["path"], item["source_lines"], item["doc_lines"]])

    src_total = sum(c["source_lines"] for c in counts)
    stats = {
        "software": C.SOFTWARE_NAME,
        "version": C.VERSION,
        "file_count": len(files),
        "source_lines": src_total,
        "doc_lines": len(all_lines),
        "lines_per_page": LINES_PER_PAGE,
        "total_pages": total_pages,
        "submit_pages": len(submit_pages),
        "submit_range": "前30页+后30页" if total_pages > 60 else "全部",
        "source_lines_submitted": sum(len(p) for p in submit_pages),
        "trimmed_tail_lines": trimmed,
        "blank_lines_dropped": True,
    }
    with open(os.path.join(C.BUILD_SOURCE, "source_stats.json"), "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

    print(json.dumps(stats, ensure_ascii=False, indent=2))
    print("tex:", full_tex)
    print("tex:", submit_tex)


if __name__ == "__main__":
    main()
