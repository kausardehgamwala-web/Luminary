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
set "VENV_PY=%~dp0.venv\Scripts\python.exe"

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

"%VENV_PY%" "%~dp0server.py"
if %errorlevel% neq 0 (
  echo.
  echo [SERVER TERMINATED WITH ERROR CODE %errorlevel%]
)
echo.
echo Press any key to close this window...
pause

