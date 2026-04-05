@echo off
:: PSC Search — Install as background startup task
:: Run this once as Administrator

set PYTHONW=C:\Users\JOJIS\AppData\Local\Programs\Python\Python313\pythonw.exe
set APP_DIR=C:\Users\JOJIS\Desktop\SearchRecord
set APP_SCRIPT=app.py
set TASK_NAME=PSCConsumerSearch

echo Installing PSC Consumer Search as a background startup task...

:: Delete old task if exists
schtasks /delete /tn "%TASK_NAME%" /f >nul 2>&1

:: Create task: run at logon, hidden, in the app directory
schtasks /create ^
  /tn "%TASK_NAME%" ^
  /tr "\"%PYTHONW%\" \"%APP_DIR%\%APP_SCRIPT%\"" ^
  /sc ONLOGON ^
  /rl HIGHEST ^
  /f >nul

if %errorlevel% neq 0 (
    echo FAILED. Try running this file as Administrator.
    pause
    exit /b 1
)

echo.
echo SUCCESS! PSC Search will now start automatically on login.
echo.
echo Starting it now...
schtasks /run /tn "%TASK_NAME%"
echo.
echo App is running in the background.
echo Open http://localhost:5000 in your browser.
echo The public URL will be printed to the log file:
echo   %APP_DIR%\psc_search.log
echo.
pause
