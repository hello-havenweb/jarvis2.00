@echo off
setlocal
cd /d "%~dp0"

echo ============================================================
echo  Starting JARVIS...
echo ============================================================
echo.

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found.
    echo         Please run install.bat first.
    pause
    exit /b 1
)

call .venv\Scripts\activate.bat

python main.py %*

if errorlevel 1 (
    echo.
    echo [ERROR] JARVIS exited with an error.
    echo         Run diagnose.bat for troubleshooting.
    pause
)

endlocal
