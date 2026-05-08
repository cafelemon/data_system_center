@echo off
setlocal

echo Stopping archive system windows...
taskkill /FI "WINDOWTITLE eq Archive System Backend*" /T /F >nul 2>nul
taskkill /FI "WINDOWTITLE eq Archive System Frontend*" /T /F >nul 2>nul
echo Done.
pause
