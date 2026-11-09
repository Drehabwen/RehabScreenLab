# Windows 踩坑记录

| 现象 | 原因 | 处理 |
| --- | --- | --- |
| `.ps1` 报语法错误、中文变乱码 | PowerShell 5.1 把**无 BOM** 的 .ps1 按 GBK 解码 | 脚本保持**纯 ASCII**；中文只放 `.tex`/`.py`；或存成 UTF-8 with BOM |
| 无法运行脚本：未数字签名 | 执行策略 | `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force` |
| `pwsh` 命令不存在 | 本机只有 Windows PowerShell 5.1 | 用 `& '<脚本>' -参数` 或 `powershell -File` |
| xelatex 报 driver 崩溃 / PDF 0 字节 | 受限沙箱下 `xdvipdfmx` 崩 | 用完整权限运行；或先 `xelatex -no-pdf` 再单独 `xdvipdfmx` |
| LibreOffice 目录在但 `soffice.exe` 找不到 | 安装不完整 | 不要依赖它，中文 PDF 走 TeX Live xelatex |
| Chrome headless 报 crashpad `OpenProcess: 拒绝访问` | 受限令牌 | 完整权限运行；或改用已存在的 Chrome/Edge 路径 |
| 截图右侧被裁 | 视口窄于页面最小宽度 | 加宽（如 480×1000）；别硬截 |
| `pip install` 卡死 | 无外网 | 不依赖新装库；python-docx / pypdf / Pillow 一般已就绪 |
| 中文路径在命令里乱码 | 命令行参数编码 | 用 python 遍历/读写，路径不要塞进 PowerShell 参数 |
| git push 报 `denied to deploy key` | SSH 是只读 deploy key | `gh auth setup-git` + https remote + `git config http.sslBackend openssl` |
| git https 报 `schannel: SEC_E_NO_CREDENTIALS` | TLS 后端问题 | `git config http.sslBackend openssl` |

## 环境自检

`python check_env.py` 会检查：Python≥3.10、python-docx/pypdf/Pillow、xelatex 版本、宋体/Consolas 字体、Chrome 路径、git；输出 `environment.json` + `environment.md`，缺硬性依赖 exit 1。
