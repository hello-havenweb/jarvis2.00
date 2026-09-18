@echo off
setlocal
cd /d "%~dp0"

echo ============================================================
echo  JARVIS UPDATER
echo ============================================================
echo.

if not exist ".venv" (
    echo [FAIL] Virtual environment not found. Run install.bat first.
    pause
    exit /b 1
)

call .venv\Scripts\activate.bat

echo [....] Updating dependencies...
pip install -r requirements.txt --upgrade --quiet
if errorlevel 1 (
    echo [FAIL] Dependency update failed.
    pause
    exit /b 1
)
echo [PASS] Dependencies updated.

echo [....] Running diagnostics...
python scripts\diagnostics.py

echo.
echo ============================================================
echo  UPDATE COMPLETE
echo ============================================================
pause
endlocal
