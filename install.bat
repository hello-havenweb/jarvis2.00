@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

echo ============================================================
echo  JARVIS INSTALLER
echo ============================================================
echo.

set "INSTALL_FAILED=0"

REM --- Check Windows ---
ver | find "Windows" >nul 2>&1
if errorlevel 1 (
    echo [FAIL] This installer requires Windows.
    set "INSTALL_FAILED=1"
    goto :end_install
)
echo [PASS] Windows detected.

REM --- Check Python ---
where python >nul 2>&1
if errorlevel 1 (
    echo [FAIL] Python not found in PATH.
    echo        Install Python 3.11.x from https://python.org
    echo        Ensure "Add Python to PATH" is checked.
    set "INSTALL_FAILED=1"
    goto :end_install
)

REM --- Check Python version ---
for /f "tokens=*" %%i in ('python -c "import sys; v=sys.version_info; print(f'{v.major}.{v.minor}.{v.micro}')"') do set "PYVER=%%i"
for /f "tokens=1,2 delims=." %%a in ("%PYVER%") do (
    set "PYMAJOR=%%a"
    set "PYMINOR=%%b"
)

if not "%PYMAJOR%"=="3" (
    echo [FAIL] Python 3.11.x required. Found: %PYVER%
    set "INSTALL_FAILED=1"
    goto :end_install
)
if not "%PYMINOR%"=="11" (
    echo [FAIL] Python 3.11.x required. Found: %PYVER%
    echo        JARVIS requires Python 3.11.x specifically.
    set "INSTALL_FAILED=1"
    goto :end_install
)
echo [PASS] Python %PYVER% detected.

REM --- Create venv ---
if not exist ".venv" (
    echo [....] Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo [FAIL] Could not create virtual environment.
        set "INSTALL_FAILED=1"
        goto :end_install
    )
)
echo [PASS] Virtual environment ready.

REM --- Activate venv ---
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo [FAIL] Could not activate virtual environment.
    set "INSTALL_FAILED=1"
    goto :end_install
)
echo [PASS] Virtual environment activated.

REM --- Upgrade pip ---
echo [....] Upgrading pip...
python -m pip install --upgrade pip --quiet
if errorlevel 1 (
    echo [WARN] pip upgrade had issues, continuing...
)
echo [PASS] pip upgraded.

REM --- Install requirements ---
echo [....] Installing dependencies (this may take several minutes)...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo [FAIL] Dependency installation failed.
    echo        Check requirements.txt and your internet connection.
    set "INSTALL_FAILED=1"
    goto :end_install
)
echo [PASS] Dependencies installed.

REM --- Verify critical imports ---
echo [....] Verifying critical imports...
python -c "import PySide6; import requests; import yaml; import dotenv; import psutil; import numpy; print('OK')"
if errorlevel 1 (
    echo [FAIL] Critical import verification failed.
    set "INSTALL_FAILED=1"
    goto :end_install
)
echo [PASS] Critical imports verified.

REM --- Install Playwright browsers ---
echo [....] Installing Playwright browsers (this may take a few minutes)...
python -m playwright install chromium >nul 2>&1
if errorlevel 1 (
    echo [WARN] Playwright browser installation failed. Browser features will be unavailable.
) else (
    echo [PASS] Playwright browsers installed.
)

REM --- Create data directories ---
echo [....] Creating data directories...
if not exist "data" mkdir data
if not exist "data\database" mkdir data\database
if not exist "data\logs" mkdir data\logs
if not exist "data\memory" mkdir data\memory
if not exist "data\cache" mkdir data\cache
if not exist "data\backups" mkdir data\backups
echo [PASS] Data directories created.

REM --- Create .env if missing ---
if not exist ".env" (
    copy ".env.example" ".env" >nul 2>&1
    echo [PASS] Created .env from .env.example — edit with your settings.
) else (
    echo [PASS] .env already exists.
)

REM --- Create config if missing ---
if not exist "config\config.yaml" (
    if exist "config\config.example.yaml" (
        copy "config\config.example.yaml" "config\config.yaml" >nul 2>&1
        echo [PASS] Created config\config.yaml from example.
    )
) else (
    echo [PASS] config\config.yaml already exists.
)

REM --- Initialize database ---
echo [....] Initializing database...
python -c "from memory.database import DatabaseManager; db=DatabaseManager(); db.initialize(); print('OK')"
if errorlevel 1 (
    echo [FAIL] Database initialization failed.
    set "INSTALL_FAILED=1"
    goto :end_install
)
echo [PASS] Database initialized.

REM --- Run smoke tests ---
echo [....] Running smoke tests...
python -m pytest tests\test_smoke.py -x -q 2>nul
if errorlevel 1 (
    echo [WARN] Some smoke tests did not pass. Check logs for details.
) else (
    echo [PASS] Smoke tests passed.
)

REM --- Run diagnostics ---
echo [....] Running diagnostics...
python scripts\diagnostics.py
echo.

:end_install
echo.
if "%INSTALL_FAILED%"=="1" (
    echo ============================================================
    echo  INSTALLATION FAILED
    echo  Please review the errors above and retry.
    echo ============================================================
) else (
    echo ============================================================
    echo  INSTALLATION COMPLETE
    echo  Run JARVIS with: run_jarvis.bat
    echo ============================================================
)
echo.
pause
endlocal
