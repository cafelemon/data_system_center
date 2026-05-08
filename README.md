# 档案目录管理系统

档案目录管理系统用于公司内部纸质档案与电子档案目录台账管理，当前一期目标是参照已确认截图，快速形成一套可运行、可演示、可持续修改的企业后台系统。

本系统只管理档案目录元数据，不上传电子文件，不做文件预览，不做 OCR，不接知识库。系统核心围绕档案编号、档案名称、档案类型、内部档案类型、状态、保管期限、归档部门、归档人、归档日期、纸质存放位置、电子存储路径、责任人等字段建立可查询、可维护、可统计的目录管理能力。

## 当前阶段

当前已完成 P0、P1、P2、P3、P4、P5、P6、P7 以及双台账字段改造。

P7 已完成 Excel 导出与基础操作日志；双台账改造已将档案入口拆分为“纸质档案管理”和“电子档案管理”，统计看板支持按全部/纸质/电子筛选，部门字典已切换为 15 个归档部门。

内部档案类型为纸质和电子台账的必填手工字段，可在列表中筛选查找；原“档案类型”继续作为必选字典字段，用于统计分析。

## 一期核心页面

一期核心菜单：

1. 纸质档案管理
2. 电子档案管理
3. 用户管理
4. 系统设置
5. 数据统计
6. 操作日志

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
- [Windows 小白单机版部署说明](docs/WINDOWS_小白单机版部署说明.md)
- [Windows 迁移部署说明](docs/WINDOWS_迁移部署说明.md)
- [P0 项目启动与目标冻结](docs/P0_项目启动与目标冻结.md)
- [P1 工程底座搭建与基础联通](docs/P1_工程底座搭建与基础联通.md)
- [P2 核心数据模型与初始化数据](docs/P2_核心数据模型与初始化数据.md)
- [P3 登录用户与权限基础功能](docs/P3_登录用户与权限基础功能.md)
- [P4 档案列表核心功能](docs/P4_档案列表核心功能.md)
- [P5 系统设置功能](docs/P5_系统设置功能.md)
- [P6 数据统计看板](docs/P6_数据统计看板.md)
- [P7 Excel导出与基础操作日志](docs/P7_Excel导出与基础操作日志.md)
- [双台账字段改造](docs/P7_1_双台账字段改造.md)
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

如果迁移到新电脑并需要空库，只保留 admin 管理员账号，运行：

```bash
cd backend
../.venv/bin/alembic upgrade head
../.venv/bin/python scripts/init_empty_admin.py
```

如果同事不方便使用 Docker 和 PostgreSQL，可使用 Windows 小白单机版：

```text
windows/install_once.bat
windows/start_system.bat
windows/register_startup_task.bat
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

P4 / 双台账主要接口：

- 纸质档案列表：`GET http://127.0.0.1:18080/api/archives?archive_medium=paper`
- 电子档案列表：`GET http://127.0.0.1:18080/api/archives?archive_medium=electronic`
- 档案详情：`GET http://127.0.0.1:18080/api/archives/{id}`
- 档案筛选选项：`GET http://127.0.0.1:18080/api/archives/options`
- 新建档案：`POST http://127.0.0.1:18080/api/archives`
- 编辑档案：`PUT http://127.0.0.1:18080/api/archives/{id}`
- 软删除档案：`DELETE http://127.0.0.1:18080/api/archives/{id}`
- 批量软删除档案：`DELETE http://127.0.0.1:18080/api/archives/batch`

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

- 统计概览：`GET http://127.0.0.1:18080/api/statistics/overview?archive_medium=all`
- 状态分布：`GET http://127.0.0.1:18080/api/statistics/status-distribution?archive_medium=paper`
- 类型分布：`GET http://127.0.0.1:18080/api/statistics/type-distribution?archive_medium=electronic`
- 部门排行：`GET http://127.0.0.1:18080/api/statistics/department-ranking?limit=8&archive_medium=all`
- 月度趋势：`GET http://127.0.0.1:18080/api/statistics/monthly-trend?months=12&archive_medium=all`

统计接口的 `archive_medium` 可选值为 `all`、`paper`、`electronic`，默认 `all`。

P7 主要接口：

- 纸质档案导出：`GET http://127.0.0.1:18080/api/archives/export?archive_medium=paper`
- 电子档案导出：`GET http://127.0.0.1:18080/api/archives/export?archive_medium=electronic`
- 操作日志：`GET http://127.0.0.1:18080/api/operation-logs`

## 下一阶段

P8 将实现 Docker 化与本地部署。

## 演示账号

- 管理员：`admin / Admin@123456`
- 普通演示用户默认密码：`User@123456`
