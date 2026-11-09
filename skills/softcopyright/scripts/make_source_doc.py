# -*- coding: utf-8 -*-
"""生成软著「源程序文档」：
  1) 全文版 TeX/PDF（全部入选源码，每页固定 60 行有效代码）
  2) 申报 60 页版 TeX（前 30 + 后 30，页码 1-60 连续）
  3) 文件清单 CSV、统计 JSON

选材来源（优先级）：
  A. <work>/build/code_selection.json —— 由 propose_code_selection.py 产出并人工确认过的选择文件
  B. 无选择文件时，按 source_rules.py 的规则自动选取（向后兼容）
"""
import csv
import json
import os
import sys
import unicodedata

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C
import source_rules as R

LINES_PER_PAGE = 60
WRAP_COL = 118
CONT_INDENT = "    "
SELECTION_JSON = os.path.join(C.BUILD, "code_selection.json")


def load_selection():
    """返回 None 表示没有选择文件；否则返回 {path: (start, end, reason)}（仅 selected=True）。"""
    if not os.path.exists(SELECTION_JSON):
        return None
    with open(SELECTION_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)
    items = {}
    for e in data.get("files", []):
        if not e.get("selected", True):
            continue
        path = e.get("path", "").replace("\\", "/")
        if not path:
            continue
        start = int(e.get("start_line") or 0)   # 0/None = 全文件
        end = int(e.get("end_line") or 0)
        items[path] = (start, end, e.get("reason", ""))
    return items


def clean_line(line):
    line = line.replace("\t", "    ")
    line = "".join(ch for ch in line if ch == " " or ord(ch) >= 32)
    line = "".join(ch if ord(ch) <= 0xFFFF else "?" for ch in line)
    return line.rstrip()


def char_width(ch):
    return 2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1


def display_width(s):
    return sum(char_width(ch) for ch in s)


def wrap_line(line):
    if display_width(line) <= WRAP_COL:
        return [line]
    out, cur, w = [], "", 0
    for ch in line:
        cw = char_width(ch)
        if w + cw > WRAP_COL:
            out.append(cur)
            cur, w = CONT_INDENT, display_width(CONT_INDENT)
        cur += ch
        w += cw
    if cur.strip():
        out.append(cur)
    return out


TEX_MAP = {
    "\\": r"\textbackslash{}", "{": r"\{", "}": r"\}", "$": r"\$", "&": r"\&",
    "#": r"\#", "_": r"\_", "%": r"\%", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}",
}


def tex_escape(s):
    return "".join(TEX_MAP.get(ch, ch) for ch in s)


def comment_marker(rel):
    return "#" if rel.endswith(".py") else "//"


def build_lines(files, selection):
    all_lines, counts = [], []
    for rel in files:
        abs_path = os.path.join(C.REPO_ROOT, rel.replace("/", os.sep))
        if not os.path.exists(abs_path):
            print("  [skip] missing:", rel)
            continue
        with open(abs_path, "r", encoding="utf-8", errors="replace") as f:
            raw = f.read()
        if raw.startswith("\ufeff"):
            raw = raw[1:]
        src_lines = raw.splitlines()

        start = end = 0
        reason = R.describe_priority(rel)
        if selection is not None:
            if rel not in selection:
                continue
            start, end, sel_reason = selection[rel]
            reason = sel_reason or reason
            if start > 0:
                src_lines = src_lines[start - 1:end if end > 0 else None]

        marker = comment_marker(rel)
        rng = f" [L{start}-L{end}]" if start > 0 else ""
        sep = f"{marker} ==================== {rel}{rng} ===================="
        expanded = [sep]
        for ln in src_lines:
            cleaned = clean_line(ln)
            if not cleaned.strip():
                continue   # 软著要求每页 >=50 行：剔除空行，保证整页都是有效代码行
            expanded.extend(wrap_line(cleaned))
        expanded.append(f"{marker} ==================== end {rel} ====================")
        counts.append({"path": rel, "source_lines": len(src_lines),
                       "doc_lines": len(expanded), "reason": reason})
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
END_DOC = "\\end{document}\n"


def render_pages_tex(pages, header):
    parts = [PREAMBLE % {"HEADER": tex_escape(header)}]
    for page in pages:
        parts.append("\\begin{codebox}\n")
        for line in page:
            parts.append((tex_escape(line) if line.strip() else "\\hbox{}") + "\\par\n")
        parts.append("\\end{codebox}\n\\clearpage\n")
    parts.append(END_DOC)
    return "".join(parts)


def chunk(items, size):
    return [items[i:i + size] for i in range(0, len(items), size)]


ROOTS = getattr(C, "SOURCE_INCLUDE_ROOTS", None)


def main():
    selection = load_selection()
    if selection is None:
        files = R.collect_files(C.REPO_ROOT, ROOTS)
        mode = "rules"
    else:
        files = [p for p in R.collect_files(C.REPO_ROOT, ROOTS) if p in selection]
        mode = "code_selection.json"
        missing = [p for p in selection if p not in files]
        for p in missing:
            print("  [warn] selected but not discoverable:", p)

    if not files:
        raise SystemExit("no source files selected")

    all_lines, counts = build_lines(files, selection)
    tail = len(all_lines) % LINES_PER_PAGE
    if tail:
        all_lines = all_lines[:-tail]      # 裁尾：保证最后一页是满页
    pages = chunk(all_lines, LINES_PER_PAGE)
    total_pages = len(pages)
    submit_pages = pages if total_pages <= 60 else pages[:30] + pages[-30:]

    os.makedirs(C.BUILD_SOURCE, exist_ok=True)
    os.makedirs(C.OUT, exist_ok=True)

    with open(os.path.join(C.BUILD_SOURCE, "source_full.tex"), "w", encoding="utf-8", newline="\n") as f:
        f.write(render_pages_tex(pages, C.HEADER_NAME))
    with open(os.path.join(C.BUILD_SOURCE, "source_submit_60p.tex"), "w", encoding="utf-8", newline="\n") as f:
        f.write(render_pages_tex(submit_pages, C.HEADER_NAME))

    with open(os.path.join(C.BUILD_SOURCE, "source_file_list.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["序号", "文件路径", "源码行数", "文档行数", "选材理由"])
        for i, item in enumerate(counts, 1):
            w.writerow([i, item["path"], item["source_lines"], item["doc_lines"], item["reason"]])

    stats = {
        "software": C.SOFTWARE_NAME,
        "version": C.VERSION,
        "selection_mode": mode,
        "file_count": len(counts),
        "source_lines": sum(c["source_lines"] for c in counts),
        "doc_lines": len(all_lines),
        "lines_per_page": LINES_PER_PAGE,
        "total_pages": total_pages,
        "submit_pages": len(submit_pages),
        "submit_range": "前30页+后30页" if total_pages > 60 else "全部",
        "trimmed_tail_lines": tail,
    }
    with open(os.path.join(C.BUILD_SOURCE, "source_stats.json"), "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

    print(json.dumps(stats, ensure_ascii=False, indent=2))
    print("tex:", os.path.join(C.BUILD_SOURCE, "source_full.tex"))
    print("tex:", os.path.join(C.BUILD_SOURCE, "source_submit_60p.tex"))


if __name__ == "__main__":
    main()
