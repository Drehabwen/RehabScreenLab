---
name: softcopyright
description: 从本地源码仓库生成中国软件著作权登记整套材料：60 页源程序文档（前30+后30、每页60行硬控）、35-59 页软件说明书（真实运行截图）、申请表填写底稿、提交指引，输出 PDF + DOCX，并自动校验。当需要"做软著 / 申请软著 / 写软件说明书 / 生成源代码文档 / 软著登记"时使用。
version: 1.1.0
---

# 软著材料生成（PDF 精确分页）

从真实源码仓库产出一整套可提交的软著材料。与 Fokkyp / Zibor233 等 Word 版 skill 的关键区别：**用 xelatex 硬控每页行数**，页数和每页行数是排出来的、不是数出来的，直接消灭"每页不足 50 行 / 页数漂移"这个最大补正点。

## 何时用

用户要"做软著材料 / 申请软著 / 写软件说明书 / 生成源代码文档 / 整理软著登记资料"，且有可读的本地源码仓库。

## 先确认 5 个字段（不许自己编）

| 字段 | 说明 |
| --- | --- |
| 软件全称 | 须与代码页眉、说明书封面三处一致 |
| 版本号 | 首次登记 `V1.0` |
| 著作权人 | 未给姓名时用 `【著作权人姓名】` 占位并在交付说明标注 |
| 开发完成日期 | 取源码最后提交日，`YYYY-MM-DD`，不得晚于申请日 |
| 发表状态 | 未发表 / 已发表（已发表给首次发表日期） |

可自动推导：编程语言、源程序量、开发硬件环境（读本机配置）、开发工具（只写 IDE）。

## 6 步流程

```powershell
$py = "python"; $s = "<skill目录>\scripts"
Copy-Item "$s\config.example.py" "$s\config.py"   # 填软件名/版本/著作权人/日期/仓库路径

& $py "$s\check_env.py"                            # 0) 环境自检（xelatex/字体/Chrome/依赖）
& $py "$s\propose_code_selection.py"               # 1) 候选清单+code_selection.json → 人工确认
& $py "$s\make_source_doc.py"                      # 2) 生成全文/申报版 tex + 清单 + 统计
Set-ExecutionPolicy -Scope Process Bypass -Force
& "$s\build_pdf.ps1" -Dir "$s\..\.work\build\source_doc" -Python $py   # 3) 编译源程序 PDF
& "$s\make_screenshots.ps1" -RoutesJson "$s\routes.example.json"       # 4) 实拍界面（先起前后端）
#    说明书 tex 放 .work\build\manual，图片放 .work\build\manual\img，再 build_pdf.ps1 编一遍
& $py "$s\make_application_form.py"                # 5) 申请表底稿 DOCX+MD
& $py "$s\lint_manual.py"; & $py "$s\verify_materials.py"; & $py "$s\deliver.py"  # 6) 自检+校验+打包
```

## 硬规则（详见 references/）

1. 源程序每页 **60 行**、**剔除空行**、超 118 列折行、末尾裁到整页。
2. 总页数 >60 → 提交**前 30 + 后 30**，页码重编 1–60；否则全部提交。
3. 说明书写 **35–59 页**，正文每页 **≥30 行**；封面/末页/纯图页可豁免。
4. 选材必须先**分组再排序**（后端→前端）；单根仓库（如只有 `src/`）用 config 的 `SOURCE_PRIORITY_FILES` / `SOURCE_DIR_ORDER` 自定义顺序，否则"程序结尾"会落在错误文件上。
5. 页眉左「软件全称 + 版本号」、右「第 N 页」，页码连续。
6. 截图必须**实拍运行中的界面**，禁止用设计稿冒充；出 `截图来源清单.json`。
7. 申请表：主要功能 **500~1300 字**、技术特点 **≤100 字**、硬件环境拆开发/运行、源程序量与页数**纯数字**。
8. 三处名称/版本一致；全文除 `【著作权人姓名】` 外无占位与 TODO。

## 交付结构

```
materials/
├── README.md
├── 01_源程序文档/  申报60页.pdf、全文_备查.pdf、源文件清单.csv、统计.json、校验报告.json
├── 02_软件说明书/  说明书.pdf、真实运行截图来源清单.json
├── 03_登记申请表/  申请表填写信息表_V1.0.docx / .md
└── 04_提交指引/    提交材料清单与注意事项.md
```

## 验收清单

- [ ] 申报版 60 页，每页 60 行有效代码，页眉含全称+版本，页码 1–60
- [ ] 说明书 35–59 页，页数/行数/页眉/图片数通过 `lint_manual.py`
- [ ] 申请表字数与纯数字项通过 `make_application_form.py` 断言
- [ ] `verify_materials.py` 的 JSON 全部 `true`，`pages_below_50` 为空
- [ ] `materials/` 齐全，README 数字与实际一致

## 参考文件

- [references/material-rules.md](references/material-rules.md) — 页数/行数/选段/选材排序（合规核心）
- [references/application-fields.md](references/application-fields.md) — 申请表 25 个字段顺序与字数上限
- [references/writing-style.md](references/writing-style.md) — 说明书骨架、禁词表、自检项
- [references/windows-pitfalls.md](references/windows-pitfalls.md) — PS5.1/xelatex/Chrome/git 踩坑

## 脚本

| 脚本 | 作用 |
| --- | --- |
| `check_env.py` | 环境自检（Python/docx/pypdf/xelatex/字体/Chrome/git） |
| `propose_code_selection.py` | 扫源码出 `code_selection.json` + 候选清单（可审计） |
| `make_source_doc.py` | 按选择文件/规则生成 60 行分页 tex + 清单 + 统计 |
| `build_pdf.ps1` | xelatex 两遍编译并校验页数 |
| `make_screenshots.ps1` | 按 routes.json 批量实拍（fake camera 可用） |
| `make_application_form.py` | 申请表底稿 DOCX+MD，内置字数断言 |
| `lint_manual.py` | 说明书自检（禁词/字段式标题/占位/页数行数/图片） |
| `verify_materials.py` | PDF 逐页校验（页数/每页行数/页眉） |
| `deliver.py` | 中文命名打包 + README + 提交指引 |

## 禁止

- 不虚构未实现功能；规划能力必须写"后续规划"。
- 不用设计稿/示意图冒充运行截图。
- 不跳过 `code_selection.json` 确认，直接抽全库。
