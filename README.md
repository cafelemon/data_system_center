# 纸质档案目录管理系统

纸质档案目录管理系统用于公司内部纸质档案目录电子化台账管理，当前一期目标是参照已确认截图，快速形成一套可运行、可演示、可持续修改的企业后台系统。

本系统只管理纸质档案目录信息，不上传电子文件，不做文件预览，不做 OCR，不接知识库。系统核心围绕档案编号、档案名称、档案类型、状态、保管期限、所属部门、归档日期、存放位置、责任人等字段建立可查询、可维护、可统计的目录管理能力。

## 当前阶段

当前已完成 P0、P1、P2、P3、P4、P5、P6。

P6 已完成数据统计看板，当前系统可以用管理员账号登录后台，维护用户账号、纸质档案目录、系统配置，并查看真实数据库统计图表。

## 一期核心页面

一期菜单固定为四个模块：

1. 档案列表
2. 用户管理
3. 系统设置
4. 数据统计

界面风格以截图为目标：左侧固定菜单、顶部浅色导航栏、白色内容背景、浅灰分割线、蓝色主按钮、卡片式筛选区、轻量表格、状态彩色标签、统计卡片和 ECharts 图表。

## 技术栈

前端：

- Vue 3
- TypeScript
- Vite
- Element Plus
- ECharts
- Pinia
- Vue Router
- Axios

后端：

- FastAPI
- SQLAlchemy ORM
- Pydantic
- Alembic
- PostgreSQL
- JWT + RBAC
- openpyxl

部署：

- Docker Compose
- Nginx
- Ubuntu Server

## 文档入口

- [PRD 与技术栈原始方案](纸质档案目录管理系统落地方案_prd_技术栈.md)
- [P0 项目启动与目标冻结](docs/P0_项目启动与目标冻结.md)
- [P1 工程底座搭建与基础联通](docs/P1_工程底座搭建与基础联通.md)
- [P2 核心数据模型与初始化数据](docs/P2_核心数据模型与初始化数据.md)
- [P3 登录用户与权限基础功能](docs/P3_登录用户与权限基础功能.md)
- [P4 档案列表核心功能](docs/P4_档案列表核心功能.md)
- [P5 系统设置功能](docs/P5_系统设置功能.md)
- [P6 数据统计看板](docs/P6_数据统计看板.md)
- [开发进度记录](PROCESS.md)

## 本地启动

启动 PostgreSQL：

```bash
docker compose -p archive-system up -d postgres
```

安装并启动后端：

```bash
python3 -m venv .venv
.venv/bin/pip install -r backend/requirements.txt
cd backend
../.venv/bin/alembic upgrade head
../.venv/bin/python scripts/seed_data.py
../.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 18080 --reload
```

安装并启动前端：

```bash
cd frontend
npm install
npm run dev
```

本机访问 `http://127.0.0.1:15173`，系统会先进入登录页。

局域网演示时，确认本机和访问设备在同一可信局域网内，然后使用 `http://<本机局域网IP>:15173` 访问。前端开发服务会通过 Vite proxy 转发 `/api` 到本机后端 `18080` 端口。

后端地址为 `http://127.0.0.1:18080`，健康检查接口为 `http://127.0.0.1:18080/api/health`。前端开发服务使用 `http://127.0.0.1:15173` 或 `http://<本机局域网IP>:15173`。本项目 PostgreSQL 使用本机端口 `15432` 映射容器内 `5432`，避免占用机器上已有的 PostgreSQL 服务。

P3 主要接口：

- 登录：`POST http://127.0.0.1:18080/api/auth/login`
- 当前用户：`GET http://127.0.0.1:18080/api/auth/me`
- 用户列表：`GET http://127.0.0.1:18080/api/users`
- 用户筛选选项：`GET http://127.0.0.1:18080/api/users/options`

P4 主要接口：

- 档案列表：`GET http://127.0.0.1:18080/api/archives`
- 档案详情：`GET http://127.0.0.1:18080/api/archives/{id}`
- 档案筛选选项：`GET http://127.0.0.1:18080/api/archives/options`
- 新建档案：`POST http://127.0.0.1:18080/api/archives`
- 编辑档案：`PUT http://127.0.0.1:18080/api/archives/{id}`
- 软删除档案：`DELETE http://127.0.0.1:18080/api/archives/{id}`

P5 主要接口：

- 档案类型配置：`GET/POST http://127.0.0.1:18080/api/settings/archive-types`
- 档案类型编辑：`PUT http://127.0.0.1:18080/api/settings/archive-types/{id}`
- 档案类型状态：`PATCH http://127.0.0.1:18080/api/settings/archive-types/{id}/status`
- 档案类型删除：`DELETE http://127.0.0.1:18080/api/settings/archive-types/{id}`
- 保管期限配置：`GET/POST http://127.0.0.1:18080/api/settings/retention-periods`
- 保管期限编辑：`PUT http://127.0.0.1:18080/api/settings/retention-periods/{id}`
- 保管期限状态：`PATCH http://127.0.0.1:18080/api/settings/retention-periods/{id}/status`
- 保管期限删除：`DELETE http://127.0.0.1:18080/api/settings/retention-periods/{id}`

P6 主要接口：

- 统计概览：`GET http://127.0.0.1:18080/api/statistics/overview`
- 状态分布：`GET http://127.0.0.1:18080/api/statistics/status-distribution`
- 类型分布：`GET http://127.0.0.1:18080/api/statistics/type-distribution`
- 部门排行：`GET http://127.0.0.1:18080/api/statistics/department-ranking?limit=8`
- 月度趋势：`GET http://127.0.0.1:18080/api/statistics/monthly-trend?months=12`

## 下一阶段

P7 将实现 Excel 导出与基础操作日志。

## 演示账号

- 管理员：`admin / Admin@123456`
- 普通演示用户默认密码：`User@123456`
