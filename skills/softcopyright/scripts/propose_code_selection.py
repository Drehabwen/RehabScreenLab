# -*- coding: utf-8 -*-
"""扫描仓库源码，产出「代码文件候选清单」与可编辑的 code_selection.json。

流程上应先跑本脚本 → 人工确认（改 selected / start_line / end_line / reason）→ 再跑
make_source_doc.py，这样「为什么选这个文件」有留痕，可审计、可回退。

Usage:
  python propose_code_selection.py            # 生成（已存在则备份为 .bak）
  python propose_code_selection.py --force    # 覆盖已有选择文件
"""
import json
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C
import source_rules as R

OUT_JSON = os.path.join(C.BUILD, "code_selection.json")
OUT_MD = os.path.join(C.BUILD, "代码文件候选清单.md")


def group_of(rel):
    if rel.startswith("backend/"):
        return "后端"
    if rel.startswith("frontend/"):
        return "前端"
    return "其它"


def main():
    force = "--force" in sys.argv
    os.makedirs(C.BUILD, exist_ok=True)
    if os.path.exists(OUT_JSON) and not force:
        shutil.copy2(OUT_JSON, OUT_JSON + ".bak")
        print("已有选择文件，已备份为 code_selection.json.bak；如需按当前扫描重建请加 --force")
        return 0

    files = R.collect_files(
        C.REPO_ROOT,
        getattr(C, "SOURCE_INCLUDE_ROOTS", None),
        getattr(C, "SOURCE_PRIORITY_FILES", None),
        getattr(C, "SOURCE_DIR_ORDER", None),
    )
    entries = []
    total_lines = 0
    for i, rel in enumerate(files, 1):
        abs_path = os.path.join(C.REPO_ROOT, rel.replace("/", os.sep))
        lines = R.count_lines(abs_path)
        total_lines += lines
        entries.append({
            "index": i,
            "path": rel,
            "group": group_of(rel),
            "lines": lines,
            "selected": True,
            "start_line": 0,
            "end_line": 0,
            "reason": R.describe_priority(rel),
        })

    payload = {
        "software": C.SOFTWARE_NAME,
        "version": C.VERSION,
        "repo_root": C.REPO_ROOT,
        "generated_by": "propose_code_selection.py",
        "note": "selected=false 排除该文件；start_line/end_line 为 1-based 闭区间，填 0 表示整个文件；改完再跑 make_source_doc.py",
        "file_count": len(entries),
        "total_lines": total_lines,
        "estimated_pages": (total_lines + 59) // 60,
        "files": entries,
    }
    with open(OUT_JSON, "w", encoding="utf-8", newline="\n") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    lines_md = [
        "# 代码文件候选清单",
        "",
        f"- 仓库：`{C.REPO_ROOT}`",
        f"- 候选文件：**{len(entries)}** 个，合计 **{total_lines}** 行",
        f"- 按每页 60 行估算：**{payload['estimated_pages']}** 页（>60 页则只提交前 30 + 后 30）",
        "",
        "> 确认方式：编辑同目录 `code_selection.json`，把不需要的文件改 `selected: false`，"
        "需要截取区间时填 `start_line` / `end_line`（1-based，0 表示整文件），并补 `reason`。",
        "",
        "| # | 文件 | 分组 | 行数 | 选材理由 |",
        "| --- | --- | --- | --- | --- |",
    ]
    for e in entries:
        lines_md.append(f"| {e['index']} | `{e['path']}` | {e['group']} | {e['lines']} | {e['reason']} |")
    with open(OUT_MD, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines_md) + "\n")

    print(f"候选文件 {len(entries)} 个 / {total_lines} 行 / 约 {payload['estimated_pages']} 页")
    print("json:", OUT_JSON)
    print("md  :", OUT_MD)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
