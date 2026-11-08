# softcopyright · 软著材料生成

从本仓库源码生成软著登记整套材料（PDF 精确分页）。详细规则见 `SKILL.md`。

## 一次性准备

```powershell
cd scripts
Copy-Item config.example.py config.py     # 填：软件全称/版本/著作权人/完成日期/仓库路径
```

## 生成流程

```powershell
$py = "python"                 # 或解释器绝对路径
$s  = "<本目录>\scripts"

& $py "$s\make_source_doc.py"                     # 1) 源程序文档（全文 + 申报 60 页）
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
& "$s\build_pdf.ps1" -Dir "$s\..\.work\build\source_doc" -Python $py   # 2) 编译 PDF
& "$s\make_screenshots.ps1" -RoutesJson "$s\routes.example.json"       # 3) 真实截图（需先起服务）
& $py "$s\make_application_form.py"               # 4) 申请表底稿
& $py "$s\verify_materials.py"                    # 5) 校验
& $py "$s\deliver.py"                             # 6) 打包到 materials\
```

说明书 tex 放 `.work\build\manual`，图片放 `.work\build\manual\img`，规则见 `SKILL.md` 第 3 节；
交付前自查见 `SKILL.md` 第 10 节。
