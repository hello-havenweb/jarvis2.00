@echo off
setlocal
cd /d "%~dp0"

echo ============================================================
echo  JARVIS DIAGNOSTICS
echo ============================================================
echo.

if not exist ".venv\Scripts\python.exe" (
    echo [FAIL] Virtual environment not found. Run install.bat first.
    pause
    exit /b 1
)

call .venv\Scripts\activate.bat
python scripts\diagnostics.py
echo.
pause
endlocal
