@echo off
setlocal
title WAVE Agent - Public HTTPS Tunnel
cd /d "%~dp0"

powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0start-public-tunnel.ps1"

echo.
echo Public tunnel has stopped. This window can now be closed.
pause
endlocal
