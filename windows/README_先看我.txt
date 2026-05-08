档案管理系统 Windows 单机版

第一次使用：
1. 先安装 Python 3.11 和 Node.js 20 LTS。
2. 双击 install_once.bat。
3. 双击 start_system.bat。
4. 浏览器打开后使用 admin / Admin@123456 登录。
5. 需要开机自启动时，双击 register_startup_task.bat。

日常使用：
- 开机后如果已注册自启动，等待十几秒后打开 http://127.0.0.1:15173。
- 如果没有注册自启动，双击 start_system.bat。
- 如需停止系统，双击 stop_system.bat。

重要数据文件：
backend\data\archive_system.sqlite3

备份方法：
复制 backend\data\archive_system.sqlite3 到 U 盘或其他安全位置。

注意：
不要删除 backend、frontend、windows、docs 这些文件夹。
