# -*- coding: utf-8 -*-
"""源码选材的共享规则：文件发现、排除、分组与排序。

被 make_source_doc.py（执行）与 propose_code_selection.py（留痕）共用，
避免两处规则漂移。
"""
import os
import re

INCLUDE_EXT = {".py", ".ts", ".tsx", ".js", ".jsx", ".css", ".java", ".kt", ".go", ".rs"}
EXCLUDE_DIR_PARTS = {
    "node_modules", "__pycache__", ".venv", "venv", "dist", "build",
    ".pytest_cache", ".git", "coverage", ".next", "output",
}
EXCLUDE_NAME_PATTERNS = (
    r"\.test\.tsx?$", r"\.spec\.tsx?$", r"^setup\.ts$", r"\.d\.ts$",
    r"^vite\.config\.", r"^vitest\.config\.", r"^eslint\.config\.",
)

# 后端：入口 -> 基础设施 -> API -> 业务；前端：入口 -> 共享层 -> 业务
BACKEND_PRIORITY = ["backend/app/main.py", "backend/app/__init__.py"]
BACKEND_DIR_PRIORITY = [
    "backend/app/core/",
    "backend/app/shared/",
    "backend/app/api/",
    "backend/app/features/",
    "backend/migrations/versions/",
]
FRONTEND_PRIORITY = ["frontend/src/main.tsx", "frontend/src/App.tsx", "frontend/src/vite-env.d.ts"]
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
    if any(re.search(pat, name) for pat in EXCLUDE_NAME_PATTERNS):
        return True
    if "/tests/" in "/" + rel.replace("\\", "/"):
        return True
    return False


def collect_files(repo_root, include_roots=None):
    """返回按「先分组再排序」排好的相路径列表。"""
    picked = []
    for base, _, files in os.walk(repo_root):
        for fn in files:
            ext = os.path.splitext(fn)[1].lower()
            if ext not in INCLUDE_EXT:
                continue
            abs_path = os.path.join(base, fn)
            rel = os.path.relpath(abs_path, repo_root).replace("\\", "/")
            if is_excluded(rel):
                continue
            if include_roots and not any(rel.startswith(r) for r in include_roots):
                continue
            picked.append(rel)
    return sorted(picked, key=_sort_key)


def _sort_key(rel):
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


def describe_priority(rel):
    """给每个文件一个可读的选材理由，写进 code_selection.json。"""
    if rel in BACKEND_PRIORITY:
        return "程序入口/后端初始化，前 30 页起始段"
    if rel in FRONTEND_PRIORITY:
        return "前端入口，后 30 页收尾段"
    for pref in BACKEND_DIR_PRIORITY:
        if rel.startswith(pref):
            return "后端核心：" + pref.split("/")[-2]
    for pref in FRONTEND_DIR_PRIORITY:
        if rel.startswith(pref):
            return "前端核心：" + pref.split("/")[-2]
    return "其它自研源码"


def count_lines(path):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return len(f.read().splitlines())
    except OSError:
        return 0
