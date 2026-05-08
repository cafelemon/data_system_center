@echo off
setlocal

set "TASK_NAME=ArchiveSystemStartup"
set "SCRIPT=%~dp0start_background.bat"

schtasks /Create /TN "%TASK_NAME%" /SC ONLOGON /TR "\"%SCRIPT%\"" /RL LIMITED /F
if errorlevel 1 (
  echo Failed to register startup task.
  pause
  exit /b 1
)

echo Startup task registered: %TASK_NAME%
echo The backend and frontend will start automatically after Windows login.
pause
