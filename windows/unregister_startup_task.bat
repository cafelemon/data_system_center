@echo off
setlocal

set "TASK_NAME=ArchiveSystemStartup"
schtasks /Delete /TN "%TASK_NAME%" /F
echo Startup task removed: %TASK_NAME%
pause
