@echo off
setlocal
cd /d "%~dp0"

echo ============================================================
echo  OLLAMA SETUP HELPER
echo ============================================================
echo.

where ollama >nul 2>&1
if errorlevel 1 (
    echo Ollama is not installed or not in PATH.
    echo.
    echo Download Ollama from: https://ollama.ai
    echo After installing, run this script again.
    pause
    exit /b 1
)

echo [PASS] Ollama found.
echo.
echo Pulling recommended model (llama3)...
echo This may take several minutes depending on your internet speed.
echo.

ollama pull llama3

if errorlevel 1 (
    echo.
    echo [WARN] Model pull may have failed. Try manually:
    echo        ollama pull llama3
) else (
    echo.
    echo [PASS] Model ready.
)

echo.
echo Available models:
ollama list
echo.
pause
endlocal
