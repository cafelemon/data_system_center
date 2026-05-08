# Windows 小白单机版部署说明

## 适用场景

这个方案适合完全不懂数据库和 Docker 的同事使用。它不需要安装 Docker Desktop，不需要启动数据库软件，数据库就是项目里的一个 SQLite 文件。

最终效果：

- 双击安装脚本完成依赖安装和空库初始化
- 双击启动脚本打开系统
- 可以注册 Windows 任务计划程序，登录 Windows 后自动启动前后端
- 数据为空，只保留 `admin / Admin@123456`
- 不需要 Docker，不需要 PostgreSQL

## 需要同事安装的软件

只需要安装：

- Python 3.11
- Node.js 20 LTS

安装时建议勾选 “Add Python to PATH”。Node.js 用默认安装即可。

## 第一次安装

把整个项目文件夹复制到同事电脑，例如：

```text
D:\archive-system
```

双击运行：

```text
windows\install_once.bat
```

这个脚本会自动完成：

- 创建 `.venv`
- 安装后端依赖
- 安装前端依赖
- 构建前端
- 创建本地 SQLite 数据库
- 清空业务数据，只保留 admin

数据库文件位置：

```text
backend\data\archive_system.sqlite3
```

## 手动启动

双击运行：

```text
windows\start_system.bat
```

脚本会启动：

- 后端：`http://127.0.0.1:18080`
- 前端：`http://127.0.0.1:15173`

并自动打开浏览器。

登录账号：

```text
admin / Admin@123456
```

## 开机自启动

双击运行：

```text
windows\register_startup_task.bat
```

它会创建一个 Windows 任务计划程序任务：

```text
ArchiveSystemStartup
```

之后同事每次登录 Windows，系统会自动在后台启动前端和后端。

如果要取消开机自启动，双击运行：

```text
windows\unregister_startup_task.bat
```

## 停止系统

双击运行：

```text
windows\stop_system.bat
```

## 局域网访问

如果同事电脑和其他设备在同一个可信局域网，可以在其他设备访问：

```text
http://<同事电脑局域网IP>:15173
```

如果打不开，通常是 Windows 防火墙拦截了 Python 或 Node.js。允许访问专用网络即可。

## 数据清空重置

如果想再次清空数据，只保留 admin：

```text
双击 windows\stop_system.bat
双击 windows\install_once.bat
```

或者在 PowerShell 运行：

```powershell
cd backend
..\ .venv\Scripts\python scripts\init_sqlite_empty_admin.py
```

实际输入时 `..\ .venv` 中间不要有空格：

```powershell
..\.venv\Scripts\python scripts\init_sqlite_empty_admin.py
```

## 备份数据

只需要备份这个文件：

```text
backend\data\archive_system.sqlite3
```

恢复时把备份文件覆盖回同一路径即可。

## 交付包文件夹结构

给同事的压缩包根目录中应包含：

```text
backend\
frontend\
windows\
docs\
README.md
```

同事只需要进入 `windows` 文件夹，按顺序双击：

```text
install_once.bat
start_system.bat
register_startup_task.bat
```
