@echo off
setlocal

set "ROOT=%~dp0.."
cd /d "%ROOT%"

if not exist "logs" mkdir "logs"
if not exist "backend\data\archive_system.sqlite3" (
  echo Local database not found. Initializing now...
  cd /d "%ROOT%\backend"
  set "DATABASE_URL=sqlite:///./data/archive_system.sqlite3"
  "%ROOT%\.venv\Scripts\python.exe" scripts\init_sqlite_empty_admin.py
)

cd /d "%ROOT%"

start "Archive System Backend" /min "%~dp0run_backend.bat"
start "Archive System Frontend" /min "%~dp0run_frontend.bat"

exit /b 0
