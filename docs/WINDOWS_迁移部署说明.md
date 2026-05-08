# Windows 迁移部署说明

## 推荐迁移方式

推荐使用“项目代码包 + Docker PostgreSQL + 空库初始化脚本”的方式迁移到同事电脑。这样不用手工安装 PostgreSQL，也不会带走你本机的演示档案数据。

迁移目标：

- 保留完整代码、接口、页面和基础字典
- 清空档案数据、操作日志和普通用户
- 只保留 `admin / Admin@123456`
- Windows 本机可通过 `http://127.0.0.1:15173` 登录
- 同一局域网设备可通过 `http://<同事电脑局域网IP>:15173` 访问

## 需要安装

在同事 Windows 电脑安装：

- Docker Desktop
- Python 3.11
- Node.js 20 LTS
- Git

Python 后端依赖文件：

```text
backend/requirements-windows.txt
```

前端依赖以 `frontend/package.json` 和 `frontend/package-lock.json` 为准，使用 `npm install` 安装。

## 代码打包建议

打包整个项目目录，但不要带这些本机产物：

```text
.venv/
frontend/node_modules/
frontend/dist/
backend/__pycache__/
backend/app/**/__pycache__/
backend/alembic/versions/__pycache__/
```

可以直接压缩项目目录，或者推送到 Git 仓库后让同事 `git clone`。

## 初始化数据库

在项目根目录打开 PowerShell：

```powershell
docker compose -p archive-system up -d postgres
```

## 启动后端

在项目根目录执行：

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\pip install -r backend\requirements-windows.txt
cd backend
..\.venv\Scripts\alembic upgrade head
..\.venv\Scripts\python scripts\init_empty_admin.py
..\.venv\Scripts\uvicorn app.main:app --host 0.0.0.0 --port 18080 --reload
```

`scripts\init_empty_admin.py` 会清空业务数据，只保留管理员：

```text
admin / Admin@123456
```

如需临时指定管理员密码：

```powershell
$env:DEFAULT_ADMIN_PASSWORD="YourStrongPassword"
..\.venv\Scripts\python scripts\init_empty_admin.py
```

## 启动前端

另开一个 PowerShell，在项目根目录执行：

```powershell
cd frontend
npm install
npm run dev
```

本机访问：

```text
http://127.0.0.1:15173
```

局域网访问：

```text
http://<同事电脑局域网IP>:15173
```

## 验收检查

后端健康检查：

```text
http://127.0.0.1:18080/api/health
```

登录后台后应看到：

- 纸质档案管理为空列表
- 电子档案管理为空列表
- 用户管理只有 admin
- 操作日志为空或只有后续登录产生的新日志
- 基础字典仍可用

## 常见问题

如果 `15432` 端口被占用，修改 `docker-compose.yml`：

```yaml
ports:
  - "15433:5432"
```

同时在 `backend\.env` 设置：

```text
DATABASE_URL=postgresql+psycopg://archive:archive_password@127.0.0.1:15433/archive_system
```

如果局域网设备打不开页面，检查 Windows 防火墙是否允许 Node.js 和 Python 监听端口 `15173`、`18080`。
