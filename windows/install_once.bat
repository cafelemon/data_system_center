@echo off
setlocal

set "ROOT=%~dp0.."
cd /d "%ROOT%"

if not exist "logs" mkdir "logs"

echo [1/5] Checking Python...
py -3.11 --version || (
  echo Please install Python 3.11 first.
  pause
  exit /b 1
)

echo [2/5] Creating Python virtual environment...
if not exist ".venv\Scripts\python.exe" (
  py -3.11 -m venv .venv
)

echo [3/5] Installing backend dependencies...
".venv\Scripts\python.exe" -m pip install --upgrade pip
".venv\Scripts\pip.exe" install -r "backend\requirements-windows.txt"
if errorlevel 1 (
  echo Backend dependency installation failed.
  pause
  exit /b 1
)

echo [4/5] Installing frontend dependencies and building...
cd /d "%ROOT%\frontend"
call npm install
if errorlevel 1 (
  echo Frontend dependency installation failed.
  pause
  exit /b 1
)
call npm run build
if errorlevel 1 (
  echo Frontend build failed.
  pause
  exit /b 1
)

echo [5/5] Initializing empty local database...
cd /d "%ROOT%\backend"
set "DATABASE_URL=sqlite:///./data/archive_system.sqlite3"
"%ROOT%\.venv\Scripts\python.exe" scripts\init_sqlite_empty_admin.py
if errorlevel 1 (
  echo Database initialization failed.
  pause
  exit /b 1
)

echo.
echo Install finished. You can run windows\start_system.bat now.
pause
