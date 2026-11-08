# -*- coding: utf-8 -*-
"""生成《计算机软件著作权登记申请表·填写信息表》DOCX + Markdown。

字段顺序与字数限制依据登记系统实际表单：
- 主要功能：500~1300 字
- 技术特点：标签 + 文本 ≤100 字
- 开发/运行硬件环境、开发操作系统、开发工具、运行平台、支撑环境：单项 ≤50 字
- 源程序量：纯数字（全部源程序总行数）
- 页数：纯数字（实际提交的代码鉴别材料页数）
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config as C

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

OUT_DIR = C.OUT_FORMS
STATS_JSON = os.path.join(C.BUILD_SOURCE, "source_stats.json")

FUNC_TEXT = (
    "本软件面向学校、基层医疗机构与康复筛查现场，提供青少年姿态与脊柱风险筛查的完整闭环管理，主要功能如下。"
    "一、受试者管理：支持受试者建档，记录姓名、性别、出生日期、年级、班级与联系方式等信息，支持信息编辑与按班级、"
    "年级检索，支持通过 Excel 名单批量导入并生成筛查任务，导入时进行字段校验与重复项提示。"
    "二、筛查会话管理：以筛查会话为业务主对象，记录会话编号、受试者、筛查模式、执行状态与时间，支持创建、查询、"
    "详情查看与状态流转，会话列表可按状态、班级与日期筛选。"
    "三、静态体态采集与指标计算：通过摄像头采集正面站立图像，由姿态估计模型提取人体关键点，计算肩线倾斜、躯干偏移、"
    "骨盆倾斜等左右方向性对称指标，并给出采集质量评分与置信度，质量不足时提示重拍。"
    "四、Adams 前屈测试记录：提供动作引导与计时，支持留存采集画面作为证据，并由受训观察者在结构化表单中录入人工"
    "观察结果，包括左右不对称、躯干旋转方向与观察者资质，软件不自动判读严重程度。"
    "五、深蹲动作评估（可选）：对深蹲过程进行实时姿态估计，输出下蹲深度、稳定性、左右对称性与常见代偿风险提示，"
    "作为动作控制补充证据，不参与脊柱风险升级。"
    "六、质量控制与复采：对每个采集协议执行质量检查，输出数据可用、需复采、需人工复核等结论，并生成复采任务，"
    "避免以低质量数据生成结论。"
    "七、证据整合与报告门控：汇总各协议结果、证据来源与缺失项，依据报告就绪策略判断能否生成正式筛查报告，"
    "证据缺失、证据冲突或未完成复核时阻断报告并给出具体待办事项。"
    "八、报告与复核复测：生成一级分诊摘要与正式筛查报告，呈现风险等级、支持证据、冲突项与下一步建议，"
    "支持人工复核记录、复测任务派发与跟踪，历史记录可按受试者追溯。"
    "九、双端运行与同步：支持浏览器访问与打包的 Android 应用，移动端本地优先采集，并支持与康复工作台的数据同步。"
)

TECH_TEXT = (
    "前后端分离架构；以筛查会话为证据主对象，建立证据账本与报告就绪门控；"
    "MediaPipe 姿态估计结合可解释几何指标；四协议解耦、质量门控与人工复核闭环。"
)

TECH_TAGS = C.TECH_TAGS


def load_stats():
    if os.path.exists(STATS_JSON):
        with open(STATS_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"source_lines": 0, "file_count": 0, "total_pages": 0, "submit_pages": 0}


def set_cell_font(cell, size=10.0, bold=False, color=None):
    for p in cell.paragraphs:
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(1)
        for r in p.runs:
            r.font.size = Pt(size)
            r.font.bold = bold
            r.font.name = "宋体"
            r._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
            if color:
                r.font.color.rgb = color


def add_heading(doc, text, level=1):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10 if level == 1 else 8)
    p.paragraph_format.space_after = Pt(4)
    run = p.add_run(text)
    run.font.bold = True
    run.font.size = Pt(13.5 if level == 1 else 12)
    run.font.name = "黑体"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "黑体")
    run.font.color.rgb = RGBColor(0x1F, 0x33, 0x55)
    return p


def add_para(doc, text, size=10.5, bold=False, indent=False, color=None):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.35
    if indent:
        p.paragraph_format.first_line_indent = Cm(0.74)
    run = p.add_run(text)
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.name = "宋体"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
    if color:
        run.font.color.rgb = color
    return p


def add_table(doc, rows, widths=(3.4, 10.4, 3.4), headers=("字段", "填写内容", "依据 / 限制")):
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = table.rows[0].cells
    for i, h in enumerate(headers):
        hdr[i].text = h
        set_cell_font(hdr[i], size=10.0, bold=True)
    for row in rows:
        cells = table.add_row().cells
        for i, val in enumerate(row):
            cells[i].text = str(val)
            set_cell_font(cells[i], size=9.5)
    for row in table.rows:
        for i, w in enumerate(widths):
            row.cells[i].width = Cm(w)
    return table


def build_docx(stats):
    doc = Document()
    sec = doc.sections[0]
    sec.page_width = Cm(21.0)
    sec.page_height = Cm(29.7)
    sec.top_margin = Cm(2.4)
    sec.bottom_margin = Cm(2.2)
    sec.left_margin = Cm(2.4)
    sec.right_margin = Cm(2.0)

    style = doc.styles["Normal"]
    style.font.name = "宋体"
    style.font.size = Pt(10.5)
    style.element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(2)
    run = p.add_run("计算机软件著作权登记申请表 · 填写信息表")
    run.font.size = Pt(18)
    run.font.bold = True
    run.font.name = "黑体"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "黑体")

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(10)
    run = p.add_run(
        f"软件名称：{C.SOFTWARE_NAME}　版本号：{C.VERSION}\n"
        "（本表为登记系统在线申请表的填写底稿，按字段顺序照抄填报即可）"
    )
    run.font.size = Pt(10)
    run.font.color.rgb = RGBColor(0x44, 0x44, 0x44)
    run.font.name = "宋体"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")

    add_heading(doc, "一、软件基本信息")
    add_table(doc, [
        ("软件全称", C.SOFTWARE_NAME, "须与代码材料页眉、说明书完全一致"),
        ("软件简称", C.SOFTWARE_ABBR, "可选填"),
        ("版本号", C.VERSION, "首次登记通常写 V1.0"),
        ("软件分类", C.SOFTWARE_CATEGORY, "可选：应用软件/系统软件/中间件/嵌入式软件"),
        ("开发完成日期", C.COMPLETION_DATE, "YYYY-MM-DD，不得晚于申请日"),
        ("开发方式", C.DEV_MODE, "可选：单独开发/合作开发/委托开发/下达任务开发"),
        ("软件说明", C.SOFTWARE_KIND, "原创（修改或合成软件另选）"),
        ("发表状态", C.PUBLISH_STATUS, "未发表则不填首次发表日期"),
        ("首次发表日期", "未发表，不填", "已发表时填写 YYYY-MM-DD"),
        ("权利取得方式", C.RIGHTS_ACQUISITION, "原始取得"),
        ("权利范围", C.RIGHTS_SCOPE, "全部权利 / 部分权利"),
        ("页数", C.PAGES_SUBMITTED,
         "代码鉴别材料实际提交页数；本项目提交前 30 页 + 后 30 页 = 60 页"),
    ])

    add_heading(doc, "二、著作权人信息（复合字段）")
    add_table(doc, [
        ("著作权人类型", C.OWNER_TYPE, "自然人登记需身份证正反面扫描件"),
        ("姓名", C.OWNER, "★ 提交前必须替换为真实姓名"),
        ("国家", "中国", ""),
        ("省市", "【省 / 市待填】", "★ 提交前填写"),
        ("证件类型", "居民身份证", ""),
        ("证件号码", "【身份证号待填】", "★ 提交前填写"),
        ("联系地址 / 邮编", "【联系地址待填】 / 【邮编待填】", "★ 提交前填写"),
        ("联系人 / 电话 / 邮箱", "【联系人待填】 / 【电话待填】 / 【邮箱待填】", "接收补正通知"),
    ])

    add_heading(doc, "三、开发与运行环境（每项 ≤50 字）")
    add_table(doc, [
        ("开发的硬件环境", C.DEV_HARDWARE, "实际开发设备配置"),
        ("运行的硬件环境", C.RUN_HARDWARE, "部署与终端设备要求"),
        ("开发该软件的操作系统", C.DEV_OS, "实际开发机操作系统版本"),
        ("软件开发环境 / 开发工具", C.DEV_TOOLS, "只写 IDE，不写框架名"),
        ("该软件的运行平台 / 操作系统", C.RUN_PLATFORM, ""),
        ("软件运行支撑环境 / 支持软件", C.SUPPORT_ENV, "运行时依赖，不加前缀"),
        ("编程语言", C.LANGUAGES, "系统预设按钮 + 自定义 ≤120 字"),
        ("源程序量", f"{stats.get('source_lines', 0)}", "纯数字，全部源程序总行数（不写“行”字）"),
    ], widths=(4.0, 9.6, 3.6))

    add_heading(doc, "四、功能与技术描述")
    add_table(doc, [
        ("开发目的（≤50 字）", C.DEV_PURPOSE, f"当前 {len(C.DEV_PURPOSE)} 字"),
        ("面向领域 / 行业（≤50 字）", C.DOMAIN, f"当前 {len(C.DOMAIN)} 字"),
    ], widths=(4.4, 9.2, 3.6))
    add_para(doc, f"软件的主要功能（{len(FUNC_TEXT)} 字，要求 500~1300 字）：", bold=True, size=10.5)
    add_para(doc, FUNC_TEXT, size=10.5, indent=True)
    add_para(doc, f"软件的技术特点（{len(TECH_TEXT)} 字，要求 ≤100 字）：", bold=True, size=10.5)
    add_para(doc, TECH_TEXT, size=10.5, indent=True)
    add_para(doc, f"技术特点标签（多选）：{TECH_TAGS}", size=10.5)

    add_heading(doc, "五、能力边界声明（建议在“软件说明/备注”中体现）")
    add_para(doc, "1. 本软件为筛查与康复工作流辅助工具，不是医疗诊断设备，不替代医生判断与影像学诊断。", indent=True)
    add_para(doc, "2. V1.0 已实现的采集协议为：静态体态、Adams 前屈（人工结构化记录）、深蹲（可选）；"
                  "步态剪影一级分流为后续规划能力，本次登记不主张已实现。", indent=True)
    add_para(doc, "3. 软件不输出 Cobb 角，不由手机画面自动计算 ATR，不输出脊柱侧弯严重度分级。", indent=True)
    add_para(doc, "4. ATR 等数值仅接受经验证设备的人工测量录入，并记录来源与操作者。", indent=True)

    add_heading(doc, "六、提交与填写提示")
    tips = [
        "在登记系统在线填写并提交，提交后在线打印、签字（个人）或盖章（单位）。",
        "软件全称、版本号、开发完成日期须与《源程序文档》《软件说明书》页眉及封面完全一致。",
        "源程序不足 60 页全部提交；超过 60 页提交前 30 页与后 30 页，每页不少于 50 行程序。",
        "说明书文档除特定情况外每页不少于 30 行；超过 60 页同样按前 30 + 后 30 提交。",
        "开发完成日期不得晚于申请日；未发表软件不填首次发表日期。",
        "个人申请需身份证正反面清晰扫描件，且在有效期内。",
        "常见补正原因：代码材料每页不足 50 行、文档每页不足 30 行、名称/版本不一致、身份证明不符、申请表未签字。",
        "提交前把本表所有【】占位符替换为真实信息，并逐项核对第七节一致性表。",
    ]
    for i, t in enumerate(tips, 1):
        add_para(doc, f"{i}. {t}", indent=True)

    add_heading(doc, "七、材料一致性核对表")
    add_table(doc, [
        ("软件全称", C.SOFTWARE_NAME, "申请表 / 代码材料页眉 / 说明书封面与页眉", "□ 一致"),
        ("版本号", C.VERSION, "申请表 / 代码材料页眉 / 说明书封面与页眉", "□ 一致"),
        ("著作权人", C.OWNER, "申请表 / 说明书封面 / 身份证明", "□ 一致"),
        ("开发完成日期", C.COMPLETION_DATE, "申请表 / 说明书封面", "□ 一致"),
        ("编程语言", C.LANGUAGES, "申请表 / 说明书系统架构章节", "□ 一致"),
        ("源程序量", f"{stats.get('source_lines', 0)}", "申请表 / 说明书概述章节", "□ 一致"),
        ("提交页数", C.PAGES_SUBMITTED, "申请表页数字段 / 代码材料实际页数", "□ 一致"),
    ], widths=(3.2, 5.4, 8.2, 2.0), headers=("核对项", "取值", "需核对位置", "结果"))

    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(12)
    run = p.add_run("生成日期：2026-11-08　｜　本表数值均由源码仓库与构建产物自动读取，改数后请同步更新其它材料。")
    run.font.size = Pt(9)
    run.font.color.rgb = RGBColor(0x66, 0x66, 0x66)

    os.makedirs(OUT_DIR, exist_ok=True)
    docx_path = os.path.join(OUT_DIR, f"软著登记申请表填写信息表_{C.VERSION}.docx")
    doc.save(docx_path)
    return docx_path


def build_markdown(stats):
    L = []
    A = L.append
    A("# 计算机软件著作权登记申请表 · 填写信息表")
    A("")
    A(f"- 软件全称：**{C.SOFTWARE_NAME}**")
    A(f"- 版本号：**{C.VERSION}**")
    A("- 填写底稿生成日期：2026-11-08")
    A("")
    A("> 按登记系统字段顺序照抄填报。★ 为提交前必须替换/填写的项。")
    A("")
    A("## 一、软件基本信息")
    A("")
    A("| 字段 | 填写内容 | 依据 / 限制 |")
    A("| --- | --- | --- |")
    rows1 = [
        ("软件全称", C.SOFTWARE_NAME, "与代码页眉、说明书一致"),
        ("软件简称", C.SOFTWARE_ABBR, "可选"),
        ("版本号", C.VERSION, "首次登记写 V1.0"),
        ("软件分类", C.SOFTWARE_CATEGORY, "应用软件/系统软件/中间件/嵌入式软件/其他"),
        ("开发完成日期", C.COMPLETION_DATE, "YYYY-MM-DD"),
        ("开发方式", C.DEV_MODE, "单独/合作/委托/下达任务开发"),
        ("软件说明", C.SOFTWARE_KIND, "原创"),
        ("发表状态", C.PUBLISH_STATUS, "未发表不填首次发表日期"),
        ("首次发表日期", "未发表，不填", "已发表填 YYYY-MM-DD"),
        ("权利取得方式", C.RIGHTS_ACQUISITION, "原始取得"),
        ("权利范围", C.RIGHTS_SCOPE, "全部权利"),
        ("页数", C.PAGES_SUBMITTED, "前 30 页 + 后 30 页 = 60"),
    ]
    for r in rows1:
        A(f"| {r[0]} | {r[1]} | {r[2]} |")
    A("")
    A("## 二、著作权人信息（复合字段）")
    A("")
    A("| 字段 | 填写内容 | 说明 |")
    A("| --- | --- | --- |")
    rows2 = [
        ("著作权人类型", C.OWNER_TYPE, "需身份证正反面扫描件"),
        ("姓名", C.OWNER, "★ 提交前替换"),
        ("国家", "中国", ""),
        ("省市", "【省 / 市待填】", "★"),
        ("证件类型", "居民身份证", ""),
        ("证件号码", "【身份证号待填】", "★"),
        ("联系地址 / 邮编", "【联系地址待填】 / 【邮编待填】", "★"),
        ("联系人 / 电话 / 邮箱", "【联系人待填】 / 【电话待填】 / 【邮箱待填】", "接收补正通知"),
    ]
    for r in rows2:
        A(f"| {r[0]} | {r[1]} | {r[2]} |")
    A("")
    A("## 三、开发与运行环境（每项 ≤50 字）")
    A("")
    A("| 字段 | 填写内容 |")
    A("| --- | --- |")
    rows3 = [
        ("开发的硬件环境", C.DEV_HARDWARE),
        ("运行的硬件环境", C.RUN_HARDWARE),
        ("开发该软件的操作系统", C.DEV_OS),
        ("软件开发环境 / 开发工具", C.DEV_TOOLS),
        ("该软件的运行平台 / 操作系统", C.RUN_PLATFORM),
        ("软件运行支撑环境 / 支持软件", C.SUPPORT_ENV),
        ("编程语言", C.LANGUAGES),
        ("源程序量", f"{stats.get('source_lines', 0)}（纯数字，全部源程序总行数）"),
    ]
    for r in rows3:
        A(f"| {r[0]} | {r[1]} |")
    A("")
    A("## 四、功能与技术描述")
    A("")
    A(f"- **开发目的（≤50 字，{len(C.DEV_PURPOSE)} 字）**：{C.DEV_PURPOSE}")
    A(f"- **面向领域 / 行业（≤50 字，{len(C.DOMAIN)} 字）**：{C.DOMAIN}")
    A(f"- **技术特点标签（多选）**：{TECH_TAGS}")
    A("")
    A(f"### 软件的主要功能（{len(FUNC_TEXT)} 字，要求 500~1300 字）")
    A("")
    A(FUNC_TEXT)
    A("")
    A(f"### 软件的技术特点（{len(TECH_TEXT)} 字，要求 ≤100 字）")
    A("")
    A(TECH_TEXT)
    A("")
    A("## 五、能力边界声明")
    A("")
    A("1. 本软件为筛查与康复工作流辅助工具，不是医疗诊断设备，不替代医生判断与影像学诊断。")
    A("2. V1.0 已实现采集协议：静态体态、Adams 前屈（人工结构化记录）、深蹲（可选）；步态剪影一级分流为后续规划能力，本次登记不主张已实现。")
    A("3. 软件不输出 Cobb 角，不由手机画面自动计算 ATR，不输出脊柱侧弯严重度分级。")
    A("4. ATR 等数值仅接受经验证设备的人工测量录入，并记录来源与操作者。")
    A("")
    A("## 六、提交与填写提示")
    A("")
    tips = [
        "在线填写提交后打印签字（个人）或盖章（单位）。",
        "软件全称、版本号、开发完成日期须与代码材料、说明书完全一致。",
        "源程序不足 60 页全部提交；超过 60 页提交前 30 + 后 30，每页不少于 50 行。",
        "说明书每页不少于 30 行；超过 60 页同样按前 30 + 后 30 提交。",
        "开发完成日期不得晚于申请日；未发表不填首次发表日期。",
        "身份证扫描件清晰、正反面齐全、在有效期内。",
        "常见补正：代码每页不足 50 行、文档每页不足 30 行、名称版本不一致、身份证明不符、申请表未签字。",
        "提交前替换本表全部【】占位符，并核对第七节一致性表。",
    ]
    for i, t in enumerate(tips, 1):
        A(f"{i}. {t}")
    A("")
    A("## 七、材料一致性核对表")
    A("")
    A("| 核对项 | 取值 | 需核对位置 | 结果 |")
    A("| --- | --- | --- | --- |")
    rows7 = [
        ("软件全称", C.SOFTWARE_NAME, "申请表 / 代码页眉 / 说明书", "□"),
        ("版本号", C.VERSION, "申请表 / 代码页眉 / 说明书", "□"),
        ("著作权人", C.OWNER, "申请表 / 说明书封面 / 身份证明", "□"),
        ("开发完成日期", C.COMPLETION_DATE, "申请表 / 说明书封面", "□"),
        ("编程语言", C.LANGUAGES, "申请表 / 说明书架构章节", "□"),
        ("源程序量", f"{stats.get('source_lines', 0)}", "申请表 / 说明书概述章节", "□"),
        ("提交页数", C.PAGES_SUBMITTED, "申请表页数字段 / 代码材料实际页数", "□"),
    ]
    for r in rows7:
        A(f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} |")
    A("")

    os.makedirs(OUT_DIR, exist_ok=True)
    md_path = os.path.join(OUT_DIR, "软著登记申请表填写信息表.md")
    with open(md_path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(L))
    return md_path


def check_limits():
    errs = []
    if not (500 <= len(FUNC_TEXT) <= 1300):
        errs.append(f"主要功能字数 {len(FUNC_TEXT)} 不在 500~1300")
    if len(TECH_TEXT) > 100:
        errs.append(f"技术特点字数 {len(TECH_TEXT)} 超过 100")
    if len(C.DEV_PURPOSE) > 50:
        errs.append(f"开发目的字数 {len(C.DEV_PURPOSE)} 超过 50")
    if len(C.DOMAIN) > 50:
        errs.append(f"面向领域字数 {len(C.DOMAIN)} 超过 50")
    for name, val in [
        ("开发的硬件环境", C.DEV_HARDWARE),
        ("运行的硬件环境", C.RUN_HARDWARE),
        ("开发操作系统", C.DEV_OS),
        ("开发工具", C.DEV_TOOLS),
        ("运行平台", C.RUN_PLATFORM),
        ("支撑环境", C.SUPPORT_ENV),
    ]:
        if len(val) > 50:
            errs.append(f"{name} 字数 {len(val)} 超过 50")
    return errs


def main():
    stats = load_stats()
    errs = check_limits()
    if errs:
        print("字段长度校验失败：")
        for e in errs:
            print(" -", e)
        raise SystemExit(1)
    docx_path = build_docx(stats)
    md_path = build_markdown(stats)
    print(f"主要功能 {len(FUNC_TEXT)} 字（500~1300）")
    print(f"技术特点 {len(TECH_TEXT)} 字（≤100）")
    print(f"开发目的 {len(C.DEV_PURPOSE)} 字 / 面向领域 {len(C.DOMAIN)} 字（≤50）")
    print("docx:", docx_path)
    print("md:", md_path)


if __name__ == "__main__":
    main()
