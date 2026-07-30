@echo off
setlocal

start "References Agent WAVE" wsl.exe --cd "%~dp0." bash -lc "exec bash start-local.sh"
timeout /t 5 /nobreak >nul
start "" http://127.0.0.1:8642

echo Website launch requested: http://127.0.0.1:8642
echo If the first page load is early, wait for the server window to show "Application startup complete" and refresh.
endlocal
