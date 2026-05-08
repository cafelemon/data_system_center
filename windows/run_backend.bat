@echo off
setlocal

set "ROOT=%~dp0.."
if not exist "%ROOT%\logs" mkdir "%ROOT%\logs"

cd /d "%ROOT%\backend"
set "DATABASE_URL=sqlite:///./data/archive_system.sqlite3"
"%ROOT%\.venv\Scripts\uvicorn.exe" app.main:app --host 0.0.0.0 --port 18080 >> "%ROOT%\logs\backend.log" 2>&1
