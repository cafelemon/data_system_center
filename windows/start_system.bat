@echo off
setlocal

call "%~dp0start_background.bat"

echo Starting archive system...
echo Backend:  http://127.0.0.1:18080/api/health
echo Frontend: http://127.0.0.1:15173
echo.
echo Login: admin / Admin@123456
echo.
timeout /t 5 /nobreak >nul
start "" "http://127.0.0.1:15173"
exit /b 0
