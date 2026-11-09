# softcopyright · 软著材料生成

从本仓库源码生成软著登记整套材料（PDF 精确分页）。规则细节见 `SKILL.md` 与 `references/`。

## 一次性准备

```powershell
cd scripts
Copy-Item config.example.py config.py     # 填：软件全称/版本/著作权人/完成日期/仓库路径
```

## 生成流程

```powershell
$py = "python"                            # 或解释器绝对路径
$s  = "<本目录>\scripts"

& $py "$s\check_env.py"                                            # 0 环境自检
& $py "$s\propose_code_selection.py"                               # 1 候选清单 + code_selection.json（先确认再生成）
& $py "$s\make_source_doc.py"                                      # 2 源程序 tex（全文 + 申报 60 页）
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
& "$s\build_pdf.ps1" -Dir "$s\..\.work\build\source_doc" -Python $py   # 3 编译源程序 PDF
& "$s\make_screenshots.ps1" -RoutesJson "$s\routes.example.json"       # 4 实拍界面（需先起前后端）
& "$s\build_pdf.ps1" -Dir "$s\..\.work\build\manual" -Python $py       #   编译说明书 PDF
& $py "$s\make_application_form.py"                                # 5 申请表底稿
& $py "$s\lint_manual.py"                                          # 6a 说明书自检
& $py "$s\verify_materials.py"                                     # 6b 材料校验
& $py "$s\deliver.py"                                              # 6c 打包到 materials\
```

## 中间产物

全部落在 `.work\`（已 gitignore）：

```
.work/
├── build/
│   ├── environment.json /.md     环境自检结果
│   ├── code_selection.json       选材留痕（selected / start_line / end_line / reason）
│   ├── 代码文件候选清单.md
│   ├── source_doc/               source_full.tex / source_submit_60p.tex / 清单 / 统计
│   ├── manual/                   说明书 tex + img\ + 编译日志
│   └── 说明书自检.json
└── out/                          source_full.pdf / source_submit_60p.pdf / manual.pdf
```

`deliver.py` 按中文命名整理到 `<仓库根>\materials\`。

## 交付前

按 `SKILL.md` 第 10 节验收清单逐条打勾；`verify_materials.py` 与 `lint_manual.py` 的 JSON 必须全绿。
