# RehabScreenLab 青少年姿态与脊柱早筛

RehabScreenLab 是面向校园和机构现场的筛查闭环工具，不是医学诊断系统。

当前产品主线：

```text
步态剪影初筛分流
→ 静态体态与受训人员 Adams 标准筛查
→ 证据质量、来源、冲突与复核门禁
→ 正式筛查报告
→ 复测与归档
```

## 唯一活动工程

```text
早筛/
├─ frontend/                 React + TypeScript + Vite 移动端
├─ backend/                  FastAPI + SQLite 后端
├─ docs/                     当前产品与技术规格
├─ ui-design/
│  ├─ high-fidelity-v3/      当前高保真与设计系统
│  └─ archive/               历史视觉稿，不参与当前实现
├─ docker-compose.yml
├─ Makefile
└─ codex-plan.md             当前实施记录
```

以下嵌套副本已经移除，不得重新创建：

- `frontend/frontend`
- `backend/backend`
- `docs/docs`
- `ui-design/ui-design`

## 权威文档

按以下顺序处理冲突：

1. [`docs/SPEC.md`](docs/SPEC.md)
2. [`docs/PRD.md`](docs/PRD.md)
3. [`docs/PROTOCOL_API_CONTRACT.md`](docs/PROTOCOL_API_CONTRACT.md)
4. [`docs/REPORT_LOGIC.md`](docs/REPORT_LOGIC.md)
5. [`docs/TECH_ROADMAP.md`](docs/TECH_ROADMAP.md)

历史资料统一位于 [`docs/archive`](docs/archive)，不作为当前开发依据。

## 产品硬边界

- 步态剪影只用于一级分流和数据留存，不能单独生成正式报告。
- 正式报告必须有可用的静态体态证据和受训观察者提交的 Adams 记录。
- 手机不得自动计算 ATR、Cobb 角或 Adams 严重度。
- ATR 只接受可追溯的已验证外部设备记录。
- 深蹲是可选动作证据，缺失或失败不能阻断正式报告。
- 缺失、复采、冲突和待复核状态必须由后端报告门禁处理。

## 本地开发

后端：

```powershell
cd backend
python -m pytest -q
uvicorn app.main:app --reload --port 8010
```

前端：

```powershell
cd frontend
npm install
npm run check
npm run test -- --run
npm run dev
```

完整构建：

```powershell
docker compose up --build
```
