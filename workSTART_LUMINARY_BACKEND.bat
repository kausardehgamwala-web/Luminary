@echo off
setlocal enabledelayedexpansion
title Luminary AI Website and Backend (DeepSeek and Stable Diffusion Connected)
color 0E
echo ========================================================
echo   Luminary AI Website + Backend Running on Port 8000
echo   Website: http://localhost:8000/
echo   Text AI: deepseek-coder:6.7b (Ollama)
echo   Image AI: Stable Diffusion v1-5 (Local CPU)
echo ========================================================
echo.

if "%1"=="test" goto run_tests
if "%1"=="run_tests" goto run_tests

:: Check if port 8000 is already in use and attempt to kill existing process
netstat -ano | findstr LISTENING | findstr :8000 >nul 2>&1
if %errorlevel% equ 0 (
  echo [INFO] Port 8000 is currently occupied. Attempting to restart server...
  for /f "tokens=5" %%a in ('netstat -ano ^| findstr LISTENING ^| findstr :8000') do (
    taskkill /PID %%a /F >nul 2>&1
  )
  timeout /t 1 >nul
  netstat -ano | findstr LISTENING | findstr :8000 >nul 2>&1
  if !errorlevel! equ 0 (
    echo [INFO] Luminary Backend is ALREADY RUNNING in the background on http://localhost:8000/
    echo Opening Luminary Website...
    start http://localhost:8000/
    echo.
    echo Press any key to close this window...
    pause
    exit /b 0
  )
)

:: ── VENV CHECK: Dedicated Luminary Virtual Environment ──────────────────────
for %%I in ("%~dp0.venv\Scripts\python.exe") do set "VENV_PY=%%~fI"

if not exist "%VENV_PY%" (
  echo.
  echo ========================================================
  echo [ERROR] Luminary dedicated virtual environment not found!
  echo Missing interpreter: %VENV_PY%
  echo.
  echo Please run setup_luminary_env.bat first to create the
  echo dedicated environment and install all dependencies.
  echo ========================================================
  echo.
  pause
  exit /b 1
)

:: ── DEPENDENCY CHECK: Silently install/verify requirements.txt ──────────────
if exist "%~dp0requirements.txt" (
  echo [INFO] Verifying Python dependencies quietly...
  "%VENV_PY%" -m pip install -r "%~dp0requirements.txt" --quiet
)

echo Starting Luminary Server with dedicated Python: %VENV_PY%
echo.

:: ── SECURITY CHECK: LUMINARY_AUTH_SECRET must be set ────────────────────────
:: This key signs all session tokens. Without it the server will refuse to start.
:: To generate a secure secret (run once, save the output):
::
::   python -c "import secrets; print(secrets.token_hex(32))"
::
:: Then set it here before the server launch line, e.g.:
::   set LUMINARY_AUTH_SECRET=your_generated_secret_here
::
:: Or add it to a .env file (never commit .env to git).
:: ─────────────────────────────────────────────────────────────────────────────
if not defined LUMINARY_AUTH_SECRET (
  echo [INFO] LUMINARY_AUTH_SECRET not set in CMD. luminary_auth will auto-load from .env or generate a secure 256-bit key.
)

:: -- Output Token Limits --------------------------------------------------
set "CHAT_OUTPUT_TOKENS=2048"
set "DOC_OUTPUT_TOKENS=4096"
set "PPT_OUTPUT_TOKENS=4096"
set "SHEET_OUTPUT_TOKENS=4096"
set "PROMPT_BUILDER_MAX_TOKENS=1024"
set "SDXL_PROMPT_MAX_TOKENS=77"
set "FALLBACK_CAP=1024"
"%VENV_PY%" "%~dp0server.py" --host 0.0.0.0 --port 8000
if %errorlevel% neq 0 (
  echo.
  echo [SERVER TERMINATED WITH ERROR CODE %errorlevel%]
)
echo.
echo Press any key to close this window...
pause
exit /b 0

:run_tests
for %%I in ("%~dp0.venv\Scripts\python.exe") do set "VENV_PY=%%~fI"
if not exist "%VENV_PY%" set "VENV_PY=python"
echo Running Luminary Ruthless System Test Suite...
"%VENV_PY%" "%~dp0test_system.py"
echo Test suite execution completed.
pause
exit /b 0


