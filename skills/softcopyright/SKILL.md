---
name: softcopyright
description: 从本仓库（或任意本地源码仓库）生成中国软件著作权登记整套材料：60 页源程序文档、35-59 页软件说明书（真实运行截图）、申请表填写底稿、提交指引。当需要"做软著 / 申请软著 / 写软件说明书 / 生成源代码文档 / 软著登记"时使用。
version: 1.0.0
---

# 软著材料生成（PDF 精确分页版）

从真实源码仓库产出一整套可提交的软著登记材料。与 GitHub 上 Fokkyp / Zibor233 / XavierLin19 那类 skill 的关键区别：**不用 Word 自动分页，改用 xelatex 硬控每页行数**，把"每页不足 50 行 / 页数漂移"这个最大补正点直接消灭。

## 0. 先确认五个字段（缺一不可，不许自己编）

| 字段 | 说明 |
| --- | --- |
| 软件全称 | 例如「青跃智衡青少年姿态与脊柱早筛系统」，须与代码页眉、说明书封面三处一致 |
| 版本号 | 首次登记一律 `V1.0` |
| 著作权人 | 个人给姓名；未给时用 `【著作权人姓名】` 占位，并在交付说明里标注 |
| 开发完成日期 | 取源码最后提交日，`YYYY-MM-DD`，不得晚于申请日 |
| 发表状态 | 未发表 / 已发表（已发表须给首次发表日期） |

可自动推导：编程语言、源程序量（行数）、开发硬件环境（读本机配置）、开发工具（只写 IDE）。

## 1. 源码选材（决定"程序开头/结尾"是否成立）

- 只收自研源码：`.py .ts .tsx .js .css .java .kt .go .rs`；**排除** `node_modules/ dist/ build/ .venv/ __pycache__/ .git/`、测试文件、生成代码、二进制与资源。
- 排序必须**先分组再排序**，否则后端 `features/__init__.py` 这类根文件会漏到前端之后，导致"程序结尾"是后端文件：
  1. 后端：`main.py` → `core/` → `shared/` → `api/` → `features/<业务模块>/` → `migrations/`
  2. 前端：`main.tsx`/`App.tsx` → `shared/`(api→config→i18n→types→components→layout) → `features/`
  3. 其它
- 每个文件前插一行 `# ===== <相对路径> =====`（前端用 `//`），便于审核员定位。

## 2. 排版硬规则（合规核心）

- **每页 60 行**（≥50 行不踩线）：按 60 行切 chunk，每页一个固定高度 `minipage`，页后 `\clearpage`，TeX 不会再自己分页。
- **剔除空行**：空行占行但不算程序行，留着会出现"60 行里只有 48 行有效"。
- **折行**：单行超过 118 显示列时确定性折行（全角按 2 列），续行缩进 4 空格，避免 TeX overfull 把行挤成两行。
- **裁尾**：末尾不足一页的行裁掉，保证申报版最后一页是满页。
- 页眉：左「软件全称 + 版本号」，右「第 N 页」；页码连续。
- 申报版构成：`总页数 > 60` → 前 30 页 + 后 30 页，页码重编 1–60；`≤60` → 全部提交。
- 全文版另存一份「备查」，不用于上传。

xelatex 骨架：

```latex
\documentclass[10.5pt]{ctexart}
\usepackage[a4paper,top=15mm,bottom=12mm,left=12mm,right=12mm]{geometry}
\usepackage{fancyhdr}
\usepackage{fontspec}
\setmonofont{Consolas}
\setCJKmonofont{SimSun}
\pagestyle{fancy}\fancyhf{}
\fancyhead[L]{\fontsize{8pt}{9.5pt}\selectfont 软件全称 V1.0}
\fancyhead[R]{\fontsize{8pt}{9.5pt}\selectfont 第 \thepage{} 页}
\setlength{\parindent}{0pt}\setlength{\parskip}{0pt}\setlength{\headheight}{13pt}
\newenvironment{codebox}
  {\begin{minipage}[t][250mm][t]{\textwidth}\raggedright\ttfamily\fontsize{7.5pt}{11.6pt}\selectfont\vspace{0pt}}
  {\end{minipage}}
\begin{document}
% 每页：\begin{codebox} 60 行（空行用 \hbox{}\par）\end{codebox}\clearpage
\end{document}
```

TeX 转义必须单字符映射：`\ { } $ & # _ % ~ ^` → `\textbackslash{} \{ \} \$ \& \# \_ \% \textasciitilde{} \textasciicircum{}`。不能先替换反斜杠再替换花括号，否则会二次转义。

## 3. 软件说明书（文档鉴别材料）

- 篇幅 **35–59 页**（<60 可整本提交，避免前 30+后 30）。xelatex 编译两遍，第二遍目录页码才正确。
- 每页正文 **≥30 行**（封面、末页、纯图页可豁免，但别整页只放一张图）。
- 章节骨架：
  1 软件概述（含**相关文档表**、术语、产品边界）
  2 运行环境（硬件/软件/**系统要求最低-推荐配置表**、兼容性、权限）
  3 系统架构与技术特征（分层、技术栈、证据模型、状态机）
  4 功能模块说明（按真实页面，一模块一节）
  5 操作流程（逐页配截图，按真实流程）
  6 报告与业务规则（风险分层、门控条件、缺失/冲突处理）
  7 数据管理与隐私
  8 行业/医学边界与免责声明
  9 异常处理
  10 版本维护 + **常见问题解答**
- 写作红线：段落化；禁止「进入方式：/操作步骤：/操作结果：」这种字段表；禁止「旨在、赋能、一站式、智能化、高效便捷、显著提升、强大功能、丰富功能」；每个页面写到具体控件、状态标签、提示文案、异常反馈；不得虚构未实现功能，规划能力写明"后续规划"。
- 医学/安全类必须写：非诊断设备、不替代专业判断、不输出什么指标（如 Cobb 角 / ATR）。

## 4. 截图必须实拍（不许用设计稿冒充）

1. 从仓库起服务：后端 `uvicorn app.main:app --port <p>`，前端 `npm run dev`（`node_modules` 常在仓库里，可直接跑）。
2. Chrome headless 实拍，移动端统一 `480x1000 CSS px @2x`，窄屏对比 `360x780 @3x`：

```powershell
& $chrome --headless=new --disable-gpu --hide-scrollbars --no-first-run `
  --force-device-scale-factor=2 --window-size=480,1000 --virtual-time-budget=9000 `
  --use-fake-ui-for-media-stream --use-fake-device-for-media-stream `
  --user-data-dir=$profile --screenshot="$out" "http://localhost:5174/<route>"
```

3. 视口太窄会右侧裁切 → 加宽重截，别硬截。摄像头页用 fake device 拿到真实页面（未开始采集态）。
4. 生成 `截图来源清单.json`：文件名、路由、视口、像素、sha256、拍摄时间。

## 5. 申请表填写底稿（按登记系统真实表单）

| 字段 | 要点 |
| --- | --- |
| 软件全称 / 简称 / 版本号 | 全称带宽本号拆开填；版本号 `V1.0` |
| 软件分类 | 应用软件 / 系统软件 / 中间件 / 嵌入式软件 / 其他 |
| 开发完成日期 | `YYYY-MM-DD` |
| 开发方式 | **单独开发**（不是"独立开发"） |
| 软件说明 | 原创 |
| 发表状态 / 首次发表日期 | 未发表不填日期 |
| 著作权人 | 自然人：国家/省市/姓名/证件类型/证件号 |
| 权利取得方式 / 权利范围 | 原始取得 / 全部权利 |
| 开发的硬件环境 / 运行的硬件环境 | 各 ≤50 字，**必须拆成两项** |
| 开发该软件的操作系统 | 实际开发机版本，≤50 字 |
| 软件开发环境 / 开发工具 | `开发环境: Windows 11/开发工具: Visual Studio Code`，只写 IDE |
| 该软件的运行平台 / 操作系统 | ≤50 字 |
| 软件运行支撑环境 / 支持软件 | 运行时依赖，不加前缀，≤50 字 |
| 编程语言 | 预设按钮 + 自定义 ≤120 字 |
| 源程序量 | **纯数字**，全部源程序总行数 |
| 开发目的 / 面向领域 | 各 ≤50 字，不能只写软件名 |
| 软件的主要功能 | **500~1300 字**（写少了会被补正） |
| 软件的技术特点 | 标签多选（医疗软件/人工智能软件/APP…）+ 文本 **≤100 字** |
| 页数 | **纯数字**，代码鉴别材料实际页数（60） |

底稿输出 DOCX（python-docx：宋体 10.5pt、Table Grid）+ Markdown 双份，并把 ★ 待填项（姓名、身份证号、省市、地址、邮箱）列成表。

## 6. 自动校验（交付前必跑）

用 pypdf 逐页校验并输出 JSON：
- 申报版 `pages == 60`；`min(每页非空行 - 1) >= 50`；命中「软件全称 + 第 N 页」的页数 == 总页数
- 全文版同规则
- 说明书：`35 <= pages <= 59`；列出每页非空行 <30 的页码；检查页眉；统计内嵌图片数；检索 `TODO|待补充|Lorem` 计数为 0
- 三处一致性：申请表取值 == 代码页眉 == 说明书封面

## 7. 交付目录

```
materials/
├── README.md
├── 01_源程序文档/  …_申报60页.pdf、…_全文_备查.pdf、源文件清单.csv、统计.json、校验报告.json
├── 02_软件说明书/  …_软件说明书.pdf、真实运行截图来源清单.json
├── 03_登记申请表/  软著登记申请表填写信息表_V1.0.docx / .md
└── 04_提交指引/    软著提交材料清单与注意事项.md
```

## 8. Windows 踩坑记录

- **PowerShell 5.1 无 BOM 的 .ps1 按 GBK 解码** → 脚本纯 ASCII，中文只放 `.tex`/`.py`；需 `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force`。
- 中文 PDF 走 **TeX Live 的 xelatex**；LibreOffice 可能缺主程序、Chrome 在受限沙箱会崩（需完整权限）。
- 不要依赖 pip 装 PDF 库；python-docx / pypdf / Pillow 一般已就绪。
- 中文路径：用 python 遍历/读写，不要塞进 PowerShell 命令行参数。
- 仓库的 `docs/`、`ui-design/` 只作事实来源与素材，设计稿不能冒充截图。

## 9. 脚本

见 `scripts/`：`config.example.py`（元数据，先复制为 `config.py`）、`make_source_doc.py`、`build_pdf.ps1`、`make_screenshots.ps1`、`make_application_form.py`、`verify_materials.py`、`deliver.py`。用法见 `README.md`。

## 10. 验收清单

- [ ] 申报版 60 页，每页 60 行有效代码，页眉含全称+版本，页码 1–60 连续
- [ ] 全文备查版同规则，页数 = ceil(总行数/60)
- [ ] 说明书 35–59 页，正文每页 ≥30 行，目录页码正确，含真实运行截图 + 来源清单
- [ ] 申请表：主要功能 500–1300 字、技术特点 ≤100 字、纯数字项无单位、硬件环境拆分
- [ ] 三处名称/版本一致；全文无 TODO/占位（著作权人占位符除外且已标注）
- [ ] materials 目录齐全，PDF 可打开，README 数字与实际一致
