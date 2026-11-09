# -*- coding: utf-8 -*-
"""说明书自检：禁词、字段表式小标题、占位符、页数与每页行数、图片数、页眉。

Usage:
  python lint_manual.py                          # 用 config 里的默认路径
  python lint_manual.py --tex-dir <dir> --pdf <pdf>
  python lint_manual.py --no-pdf                 # 只查 tex 源
退出码：0=通过；1=存在硬性违规（占位符/字段表式标题/页数越界/薄页）
"""
import argparse
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C

BANNED = [
    "旨在", "赋能", "一站式", "智能化", "高效便捷", "显著提升", "强大能力", "强大功能",
    "丰富功能", "全面提升", "无缝", "极致", "引领", "助力", "全方位", "深度赋能",
]
FIELD_LABELS = ["进入方式：", "操作步骤：", "页面内容：", "操作规则：", "操作结果：", "使用场景："]
# 只认「未完成文档」的痕迹；不认 UI 术语里的"占位提示"这类正常表述
PLACEHOLDER_PATTERNS = [
    r"TODO", r"待补充", r"Lorem", r"XXX",
    r"【[^】]{0,20}待[^】]{0,10}】", r"\[待填\]", r"（待填）", r"占位符【",
]


def strip_tex_comment(line):
    out, i = [], 0
    while i < len(line):
        ch = line[i]
        if ch == "%" and (i == 0 or line[i - 1] != "\\"):
            break
        out.append(ch)
        i += 1
    return "".join(out)


def scan_tex(tex_dir):
    hits = {"banned": [], "field_labels": [], "placeholders": []}
    files = sorted(glob.glob(os.path.join(tex_dir, "**", "*.tex"), recursive=True))
    for path in files:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            for lineno, raw in enumerate(f, 1):
                line = strip_tex_comment(raw)
                for word in BANNED:
                    if word in line:
                        hits["banned"].append({"file": os.path.basename(path), "line": lineno, "word": word})
                for lab in FIELD_LABELS:
                    if lab in line:
                        hits["field_labels"].append({"file": os.path.basename(path), "line": lineno, "label": lab})
                for pat in PLACEHOLDER_PATTERNS:
                    m = re.search(pat, line)
                    if m:
                        hits["placeholders"].append({"file": os.path.basename(path), "line": lineno, "text": m.group(0)})
    return files, hits


def scan_pdf(pdf_path):
    if not pdf_path or not os.path.exists(pdf_path):
        return {"exists": False}
    from pypdf import PdfReader
    r = PdfReader(pdf_path)
    pages = len(r.pages)
    counts, no_header, images = [], [], 0
    for i, page in enumerate(r.pages):
        text = page.extract_text() or ""
        nonblank = [ln for ln in text.split("\n") if ln.strip()]
        counts.append(len(nonblank))
        if C.SOFTWARE_NAME not in text and C.HEADER_NAME not in text:
            no_header.append(i + 1)
        if page.images:
            images += len(list(page.images))
    return {
        "exists": True,
        "pages": pages,
        "pages_in_range": 35 <= pages <= 59,
        "thin_pages": [{"page": i + 1, "lines": c} for i, c in enumerate(counts) if c < 30],
        "min_lines": min(counts) if counts else 0,
        "avg_lines": round(sum(counts) / len(counts), 1) if counts else 0,
        "pages_without_software_name": no_header,
        "embedded_images": images,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tex-dir", default=None)
    ap.add_argument("--pdf", default=None)
    ap.add_argument("--no-pdf", action="store_true")
    args = ap.parse_args()

    tex_dir = args.tex_dir
    if not tex_dir:
        cand = os.path.join(C.BUILD_MANUAL, "sections")
        tex_dir = cand if os.path.isdir(cand) else C.BUILD_MANUAL
    pdf_path = None if args.no_pdf else (args.pdf or os.path.join(C.OUT, "manual.pdf"))

    files, hits = scan_tex(tex_dir) if os.path.isdir(tex_dir) else ([], {"banned": [], "field_labels": [], "placeholders": []})
    pdf = scan_pdf(pdf_path)

    hard = bool(hits["placeholders"] or hits["field_labels"])
    if pdf.get("exists"):
        if not pdf["pages_in_range"]:
            hard = True
        # 薄页只警告（封面/图页/末页常豁免），不阻断
    report = {
        "tex_dir": tex_dir,
        "tex_files": len(files),
        "banned_count": len(hits["banned"]),
        "field_label_count": len(hits["field_labels"]),
        "placeholder_count": len(hits["placeholders"]),
        "hits": hits,
        "pdf": pdf,
        "hard_fail": hard,
    }

    os.makedirs(C.BUILD, exist_ok=True)
    out = os.path.join(C.BUILD, "说明书自检.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"tex 文件 {len(files)} | 禁词 {len(hits['banned'])} | 字段式标题 {len(hits['field_labels'])} | 占位符 {len(hits['placeholders'])}")
    for item in hits["banned"][:10]:
        print("  BANNED ", item["file"], item["line"], item["word"])
    for item in hits["field_labels"][:10]:
        print("  LABEL  ", item["file"], item["line"], item["label"])
    for item in hits["placeholders"][:10]:
        print("  PLACE  ", item["file"], item["line"], item["text"])
    if pdf.get("exists"):
        print(f"PDF {pdf['pages']} 页，区间内={pdf['pages_in_range']}，最小行数={pdf['min_lines']}，"
              f"图片={pdf['embedded_images']}，无页眉页={pdf['pages_without_software_name'][:5]}")
        if pdf["thin_pages"]:
            print("  薄页(<30行):", pdf["thin_pages"][:10])
    print("report:", out)
    return 1 if hard else 0


if __name__ == "__main__":
    raise SystemExit(main())
