@echo off
setlocal

set "ROOT=%~dp0.."
if not exist "%ROOT%\logs" mkdir "%ROOT%\logs"

cd /d "%ROOT%\frontend"
call npm run preview >> "%ROOT%\logs\frontend.log" 2>&1
