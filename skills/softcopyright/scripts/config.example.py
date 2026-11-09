# -*- coding: utf-8 -*-
"""软著材料全局配置。复制本文件为 config.py 后填写。"""
import os

# ---- 软件身份 ----
SOFTWARE_NAME = "<软件全称，例如：青跃智衡青少年姿态与脊柱早筛系统>"
VERSION = "V1.0"
VERSION_NUMBER = "1.0"
SOFTWARE_ABBR = "<简称>"
HEADER_NAME = f"{SOFTWARE_NAME} {VERSION}"

# ---- 著作权人与日期 ----
OWNER_PLACEHOLDER = "【著作权人姓名】"
OWNER = OWNER_PLACEHOLDER
OWNER_TYPE = "自然人（个人）"
COMPLETION_DATE = "<YYYY-MM-DD>"
COMPLETION_DATE_CN = "<YYYY年MM月DD日>"
PUBLISH_STATUS = "未发表"
DEV_MODE = "单独开发"
SOFTWARE_KIND = "原创"
RIGHTS_ACQUISITION = "原始取得"
RIGHTS_SCOPE = "全部权利"
SOFTWARE_CATEGORY = "应用软件"

# ---- 环境（表单单项 <= 50 字符）----
DEV_HARDWARE = "<开发机：CPU/内存/硬盘>"
RUN_HARDWARE = "<运行：CPU/内存/硬盘/终端>"
DEV_OS = "<Windows 11>"
DEV_TOOLS = "开发环境: <OS>/开发工具: <IDE>"
RUN_PLATFORM = "<运行平台>"
SUPPORT_ENV = "<运行时依赖>"

# ---- 登记字段 ----
LANGUAGES = "<Python、TypeScript、CSS>"
DEV_PURPOSE = "<<=50 字，不能只写软件名>"
DOMAIN = "<<=50 字>"
TECH_TAGS = "<医疗软件、人工智能软件、APP 等，可空>"
PAGES_SUBMITTED = "60"

# ---- 路径 ----
REPO_ROOT = r"<仓库根目录绝对路径>"
# 只扫描这些子目录（相对仓库根）。避免把 android/、脚本目录、示例工程纳入源程序。
SOURCE_INCLUDE_ROOTS = ["backend/app/", "backend/migrations/versions/", "frontend/src/"]
BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".work")
BUILD = os.path.join(BASE, "build")
BUILD_SOURCE = os.path.join(BUILD, "source_doc")
BUILD_MANUAL = os.path.join(BUILD, "manual")
BUILD_FORMS = os.path.join(BUILD, "forms")
OUT = os.path.join(BASE, "out")
OUT_SOURCE = os.path.join(OUT, "01_source_code")
OUT_MANUAL = os.path.join(OUT, "02_manual")
OUT_FORMS = os.path.join(OUT, "03_application")
TMP = os.path.join(BASE, "tmp")
