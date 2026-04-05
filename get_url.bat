@echo off
:: Show the current public URL from the log file
set LOG=%~dp0psc_search.log

if not exist "%LOG%" (
    echo No log file found. Is the app running?
    echo Run install_service.bat first.
    pause
    exit /b
)

echo.
findstr /i "trycloudflare" "%LOG%"
echo.
echo Full log: %LOG%
pause
