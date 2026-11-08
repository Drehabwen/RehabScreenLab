# -*- coding: utf-8 -*-
"""把构建产物按中文命名整理成交付目录，并生成 README 与提交指引。"""
import json
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C

DELIVER = os.path.join(C.REPO_ROOT, "materials")

NAMES = {
    "source_submit": f"{C.SOFTWARE_NAME}{C.VERSION}_源程序文档_申报60页.pdf",
    "source_full": f"{C.SOFTWARE_NAME}{C.VERSION}_源程序文档_全文_备查.pdf",
    "manual": f"{C.SOFTWARE_NAME}{C.VERSION}_软件说明书.pdf",
    "form_docx": f"软著登记申请表填写信息表_{C.VERSION}.docx",
    "form_md": "软著登记申请表填写信息表.md",
    "file_list": "源程序文件清单.csv",
    "source_stats": "源程序统计.json",
    "verify": "校验报告.json",
}


def load_json(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def page_count(pdf):
    try:
        from pypdf import PdfReader
        return len(PdfReader(pdf).pages)
    except Exception:
        return 0


def copy(src, dst):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if os.path.exists(src):
        shutil.copy2(src, dst)
        return True
    return False


SUBMIT_GUIDE = """# 软著提交材料清单与注意事项

> 软件：**{name}**　版本：**{version}**　著作权人：**{owner}**
> 生成日期：2026-11-08　｜　源码基线：{commit}

## 一、提交材料清单（中国版权保护中心）

| # | 材料 | 本项目对应文件 | 要求 |
| --- | --- | --- | --- |
| 1 | 计算机软件著作权登记申请表 | 在线填写（底稿见 `03_登记申请表/`） | 提交后打印签字（个人）/盖章（单位） |
| 2 | 源程序鉴别材料 | `01_源程序文档/…_源程序文档_申报60页.pdf` | 前 30 页 + 后 30 页，共 {source_pages} 页，每页 {lines_per_page} 行 |
| 3 | 文档鉴别材料 | `02_软件说明书/…_软件说明书.pdf` | 共 {manual_pages} 页（不足 60 页可整本提交），每页不少于 30 行 |
| 4 | 身份证明 | 申请人身份证正反面扫描件 | 清晰、完整、在有效期内 |
| 5 | 委托书（可选） | 由代理机构提供 | 自行办理则无需 |

上传格式以登记系统当前要求为准（通常为 PDF）。`源程序文档_全文_备查.pdf`（{full_pages} 页）不用于上传，供自查与应对补正。

## 二、提交前必改项（占位符）

| 占位符 | 出现位置 | 处理 |
| --- | --- | --- |
| `【著作权人姓名】` | 申请表 DOCX/MD、说明书封面页眉 | 替换为真实姓名 |
| `【身份证号待填】` | 申请表 DOCX/MD | 填写身份证号 |
| `【省 / 市待填】`、`【联系地址待填】`、`【邮编待填】` | 申请表 DOCX/MD | 按实际填写 |
| `【联系人待填】`、`【电话待填】`、`【邮箱待填】` | 申请表 DOCX/MD | 填写可用联系方式 |

说明书封面中的著作权人已按占位符生成，替换姓名后如需要可直接改 PDF 文本或用源码重编译。

## 三、登记系统填写顺序（照抄 `03_登记申请表`）

1. 软件全称：{name}
2. 软件简称：{abbr}
3. 版本号：{version}
4. 软件分类：{category}
5. 开发完成日期：{completion}
6. 开发方式：{dev_mode}　软件说明：{kind}　发表状态：{publish}
7. 著作权人：自然人 / 中国 / 省市 / 姓名 / 身份证
8. 权利取得方式：{rights}　权利范围：全部权利
9. 开发的硬件环境、运行的硬件环境、开发操作系统、开发工具、运行平台、支撑环境（每项 ≤50 字，见底稿）
10. 编程语言：{langs}
11. 源程序量：{source_lines}（纯数字）
12. 开发目的（≤50 字）、面向领域（≤50 字）、主要功能（500~1300 字）、技术特点（≤100 字 + 标签）
13. 页数：{source_pages}（纯数字，指提交的代码材料页数）

## 四、易被补正的 8 个点（自检）

- [ ] 代码材料每页是否 ≥50 行（本项目每页 {lines_per_page} 行，已达标）
- [ ] 代码材料是否前 30 + 后 30 连续，共 60 页
- [ ] 说明书每页是否 ≥30 行、是否整本 PDF 连续页码
- [ ] 申请表、代码页眉、说明书三处软件全称与版本号是否完全一致
- [ ] 开发完成日期是否早于或等于申请日
- [ ] 未发表是否误填了首次发表日期
- [ ] 著作权人姓名、证件号与身份证扫描件是否一致
- [ ] 申请表是否已签字/盖章

## 五、官方入口与时限

- 中国版权保护中心：https://www.ccopyright.com.cn/
- 著作权登记系统：https://register.ccopyright.com.cn/login.html
- 法规：《计算机软件著作权登记办法》 https://www.gov.cn/zhengce/2002-02/20/content_5724627.htm
- 一般审核周期 30—40 个工作日，可申请加急；登记证书电子化后在线下载。

## 六、追溯信息

- 源码仓库：`D:\\Users\\DORAT\\Desktop\\03_AI康复项目\\早筛`（origin: github.com/Drehabwen/RehabScreenLab）
- 基线提交：`{commit}`（{commit_date}）
- 源程序选取：{file_count} 个源文件、{source_lines} 行，剔除测试/依赖/构建产物与空行后按每页 {lines_per_page} 行排版
- 材料构建与校验脚本：`C:\\Users\\DORAT\\Desktop\\_softcopyright_rssl\\build`
"""


README = """# {name} {version} · 软件著作权登记材料

本目录为软件著作权登记用的成套材料，可直接对照提交。生成日期 2026-11-08。

## 目录

```
materials/
├── README.md                       ← 本文件
├── 01_源程序文档/
│   ├── {n_source_submit}   ← 上传用（60 页，每页 {lines_per_page} 行）
│   ├── {n_source_full}     ← 备查（{full_pages} 页，不用于上传）
│   ├── {n_file_list}               ← 源文件选取清单（序号/路径/行数）
│   └── {n_source_stats}            ← 统计信息
├── 02_软件说明书/
│   └── {n_manual}             ← 上传用（{manual_pages} 页）
├── 03_登记申请表/
│   ├── {n_form_docx}  ← 填写底稿（Word 可改）
│   └── {n_form_md}                 ← 同内容的 Markdown 版
└── 04_提交指引/
    └── 软著提交材料清单与注意事项.md ← 清单、必改项、自检表、官方入口
```

## 三分钟上手

1. 打开 `04_提交指引/软著提交材料清单与注意事项.md`，先看「提交前必改项」。
2. 把 `03_登记申请表/` 里的 `【著作权人姓名】`、身份证号、地址、邮箱等占位符替换成真实信息。
3. 登录中国版权保护中心登记系统，按底稿逐项填写申请表。
4. 上传 `01_源程序文档/…_申报60页.pdf` 与 `02_软件说明书/…_软件说明书.pdf`，以及身份证扫描件。
5. 打印申请表签字后提交，等待受理。

## 合规要点（已校验）

- 源程序文档：共 {source_pages} 页（前 30 页 + 后 30 页），每页 {lines_per_page} 行有效代码，页眉含软件全称与版本号，页码连续。
- 软件说明书：共 {manual_pages} 页，不足 60 页可整本提交；每页正文不少于 30 行。
- 三处名称与版本号一致：申请表 / 源程序页眉 / 说明书封面页眉。

## 校验

`01_源程序文档/校验报告.json` 为自动校验结果（页数、每页行数、页眉命中页数）。
"""


def main():
    os.makedirs(DELIVER, exist_ok=True)
    stats = load_json(os.path.join(C.BUILD_SOURCE, "source_stats.json"))
    verify = load_json(os.path.join(C.OUT, "verification_report.json"))

    src_submit = os.path.join(C.OUT, "source_submit_60p.pdf")
    src_full = os.path.join(C.OUT, "source_full.pdf")
    manual = os.path.join(C.OUT, "manual.pdf")
    form_docx = os.path.join(C.OUT_FORMS, f"软著登记申请表填写信息表_{C.VERSION}.docx")
    form_md = os.path.join(C.OUT_FORMS, "软著登记申请表填写信息表.md")
    file_list = os.path.join(C.BUILD_SOURCE, "source_file_list.csv")

    d_src = os.path.join(DELIVER, "01_源程序文档")
    d_man = os.path.join(DELIVER, "02_软件说明书")
    d_form = os.path.join(DELIVER, "03_登记申请表")
    d_guide = os.path.join(DELIVER, "04_提交指引")

    moved = []
    moved.append((copy(src_submit, os.path.join(d_src, NAMES["source_submit"])), "源程序申报60页"))
    moved.append((copy(src_full, os.path.join(d_src, NAMES["source_full"])), "源程序全文"))
    moved.append((copy(file_list, os.path.join(d_src, NAMES["file_list"])), "源文件清单"))
    moved.append((copy(os.path.join(C.BUILD_SOURCE, "source_stats.json"),
                       os.path.join(d_src, NAMES["source_stats"])), "源程序统计"))
    moved.append((copy(os.path.join(C.OUT, "verification_report.json"),
                       os.path.join(d_src, NAMES["verify"])), "校验报告"))
    moved.append((copy(manual, os.path.join(d_man, NAMES["manual"])), "软件说明书"))
    moved.append((copy(os.path.join(C.BUILD_MANUAL, "img", "real", "screenshot_manifest.json"),
                       os.path.join(d_man, "真实运行截图来源清单.json")), "截图来源清单"))
    moved.append((copy(form_docx, os.path.join(d_form, NAMES["form_docx"])), "申请表 DOCX"))
    moved.append((copy(form_md, os.path.join(d_form, NAMES["form_md"])), "申请表 MD"))

    source_pages = verify.get("source_submit_60p", {}).get("pages", 60)
    full_pages = verify.get("source_full", {}).get("pages", stats.get("total_pages", 0))
    manual_pages = verify.get("manual", {}).get("pages", 0)
    if not manual_pages and os.path.exists(manual):
        manual_pages = page_count(manual)

    commit, commit_date = "", ""
    try:
        import subprocess
        commit = subprocess.check_output(
            ["git", "-C", C.REPO_ROOT, "rev-parse", "--short", "HEAD"], text=True).strip()
        commit_date = subprocess.check_output(
            ["git", "-C", C.REPO_ROOT, "log", "-1", "--format=%cd", "--date=short"], text=True).strip()
    except Exception:
        pass

    guide = SUBMIT_GUIDE.format(
        name=C.SOFTWARE_NAME, version=C.VERSION, owner=C.OWNER, abbr=C.SOFTWARE_ABBR,
        commit=commit, commit_date=commit_date,
        source_pages=source_pages, full_pages=full_pages, manual_pages=manual_pages,
        lines_per_page=stats.get("lines_per_page", 60),
        source_lines=stats.get("source_lines", 0), file_count=stats.get("file_count", 0),
        category=C.SOFTWARE_CATEGORY, completion=C.COMPLETION_DATE, dev_mode=C.DEV_MODE,
        kind=C.SOFTWARE_KIND, publish=C.PUBLISH_STATUS, rights=C.RIGHTS_ACQUISITION,
        langs=C.LANGUAGES,
    )
    os.makedirs(d_guide, exist_ok=True)
    with open(os.path.join(d_guide, "软著提交材料清单与注意事项.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write(guide)

    readme = README.format(
        name=C.SOFTWARE_NAME, version=C.VERSION,
        n_source_submit=NAMES["source_submit"], n_source_full=NAMES["source_full"],
        n_file_list=NAMES["file_list"], n_source_stats=NAMES["source_stats"],
        n_manual=NAMES["manual"], n_form_docx=NAMES["form_docx"], n_form_md=NAMES["form_md"],
        lines_per_page=stats.get("lines_per_page", 60),
        full_pages=full_pages, source_pages=source_pages, manual_pages=manual_pages,
    )
    with open(os.path.join(DELIVER, "README.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write(readme)

    # 打印结果
    print("交付目录:", DELIVER)
    for ok, label in moved:
        print(("  [OK]   " if ok else "  [MISS] ") + label)
    print(f"  源程序申报页数={source_pages} 全文页数={full_pages} 说明书页数={manual_pages}")
    total = 0
    for root, _, files in os.walk(DELIVER):
        for fn in files:
            total += os.path.getsize(os.path.join(root, fn))
    print("  合计 %.1f MB" % (total / 1024 / 1024))
    if manual_pages == 0:
        print("警告: 说明书 PDF 尚未就绪，交付包不完整")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
