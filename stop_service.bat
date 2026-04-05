@echo off
set TASK_NAME=PSCConsumerSearch

echo Stopping PSC Consumer Search...
schtasks /end /tn "%TASK_NAME%" >nul 2>&1
taskkill /f /im pythonw.exe >nul 2>&1
taskkill /f /im cloudflared.exe >nul 2>&1
echo Stopped.
pause
