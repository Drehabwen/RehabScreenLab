# -*- coding: utf-8 -*-
"""校验软著 PDF 材料是否满足提交要求。"""
import json
import os
import re
import sys

from pypdf import PdfReader

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C


def check_source_pdf(path, expect_pages):
    r = PdfReader(path)
    pages = len(r.pages)
    stats = []
    header_ok = 0
    for i, page in enumerate(r.pages):
        text = page.extract_text() or ""
        lines = [ln.rstrip() for ln in text.split("\n")]
        nonblank = [ln for ln in lines if ln.strip()]
        has_header = (C.SOFTWARE_NAME in text) and ("第" in text)
        if has_header:
            header_ok += 1
        # 代码行数 = 非空行数 - 页眉行
        code_lines = max(0, len(nonblank) - 1)
        stats.append({"page": i + 1, "code_lines": code_lines, "header": has_header})
    code_counts = [s["code_lines"] for s in stats]
    return {
        "file": os.path.basename(path),
        "pages": pages,
        "expect_pages": expect_pages,
        "pages_match": pages == expect_pages,
        "min_code_lines": min(code_counts) if code_counts else 0,
        "max_code_lines": max(code_counts) if code_counts else 0,
        "avg_code_lines": round(sum(code_counts) / len(code_counts), 1) if code_counts else 0,
        "pages_below_50": [s["page"] for s in stats if s["code_lines"] < 50],
        "header_ok_pages": header_ok,
        "pages_list": stats,
    }


def check_manual_pdf(path):
    if not os.path.exists(path):
        return {"file": os.path.basename(path), "exists": False}
    r = PdfReader(path)
    pages = len(r.pages)
    thin = []
    no_header = []
    for i, page in enumerate(r.pages):
        text = page.extract_text() or ""
        nonblank = [ln for ln in text.split("\n") if ln.strip()]
        if len(nonblank) < 30:
            thin.append({"page": i + 1, "lines": len(nonblank)})
        if (C.SOFTWARE_NAME not in text) and (C.HEADER_NAME not in text):
            no_header.append(i + 1)
    sample0 = (r.pages[0].extract_text() or "")[:400]
    return {
        "file": os.path.basename(path),
        "exists": True,
        "pages": pages,
        "pages_in_range_35_59": 35 <= pages <= 59,
        "thin_pages_lt30lines": thin,
        "pages_without_software_name": no_header,
        "cover_sample": sample0,
    }


def main():
    report = {}
    full = os.path.join(C.OUT, "source_full.pdf")
    sub = os.path.join(C.OUT, "source_submit_60p.pdf")
    man = os.path.join(C.OUT, "manual.pdf")

    if os.path.exists(sub):
        report["source_submit_60p"] = check_source_pdf(sub, 60)
    if os.path.exists(full):
        f = check_source_pdf(full, 298)
        f.pop("pages_list", None)
        report["source_full"] = f
    report["manual"] = check_manual_pdf(man)

    # 精简输出
    brief = {
        "source_submit_60p": {k: v for k, v in report.get("source_submit_60p", {}).items() if k != "pages_list"},
        "source_full": report.get("source_full", {}),
        "manual": report.get("manual", {}),
    }
    print(json.dumps(brief, ensure_ascii=False, indent=2))
    out = os.path.join(C.OUT, "verification_report.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=2)
    print("report:", out)


if __name__ == "__main__":
    main()
