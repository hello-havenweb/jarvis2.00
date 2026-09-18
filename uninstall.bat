@echo off
setlocal
cd /d "%~dp0"

echo ============================================================
echo  JARVIS UNINSTALLER
echo ============================================================
echo.
echo This will remove the virtual environment (.venv).
echo Your data in data/ will NOT be deleted.
echo.
set /p CONFIRM="Are you sure? (yes/no): "
if /i not "%CONFIRM%"=="yes" (
    echo Cancelled.
    pause
    exit /b 0
)

if exist ".venv" (
    rmdir /s /q ".venv"
    echo [DONE] Virtual environment removed.
) else (
    echo [INFO] No virtual environment found.
)

echo.
echo Uninstall complete. Data files preserved in data/.
pause
endlocal
