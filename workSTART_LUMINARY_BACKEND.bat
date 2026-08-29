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

set "PY_CMD="

:: List of candidates to test (tested with real python execution, not just where)
set CANDIDATE_1="%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
set CANDIDATE_2="py"
set CANDIDATE_3="python"
set CANDIDATE_4="%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
set CANDIDATE_5="%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
set CANDIDATE_6="%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
set CANDIDATE_7="%ProgramFiles%\Python312\python.exe"
set CANDIDATE_8="%ProgramFiles%\Python311\python.exe"
set CANDIDATE_9="%ProgramFiles%\Python310\python.exe"

for /L %%i in (1,1,9) do (
  if not defined PY_CMD (
    set "CURRENT_CANDIDATE=!CANDIDATE_%%i!"
    !CURRENT_CANDIDATE! -c "import sys; sys.exit(0)" >nul 2>nul
    if !errorlevel! equ 0 (
      set "PY_CMD=!CURRENT_CANDIDATE!"
    )
  )
)

if not defined PY_CMD (
  echo.
  echo [ERROR] No working Python installation was found.
  echo Checked PATH, User Cache, and standard Python directories.
  echo Please install Python 3.10+ and add it to your system PATH.
  echo.
  pause
  exit /b 1
)

echo Starting Luminary Server with Python: %PY_CMD%
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
  echo.
  echo [SECURITY ERROR] LUMINARY_AUTH_SECRET is not set.
  echo.
  echo This environment variable signs all session tokens. The server will
  echo refuse to start without it to prevent token-forgery attacks.
  echo.
  echo To generate a secret, run:
  echo   %PY_CMD% -c "import secrets; print(secrets.token_hex(32))"
  echo.
  echo Then either:
  echo   a) Add:  set LUMINARY_AUTH_SECRET=^<your_secret^>
  echo      to this .bat file (above the server launch line), OR
  echo   b) Set it in your system environment variables, OR
  echo   c) Add LUMINARY_AUTH_SECRET=^<your_secret^> to a .env file
  echo      (make sure .env is in .gitignore and never committed).
  echo.
  pause
  exit /b 1
)

%PY_CMD% "%~dp0server.py"
if %errorlevel% neq 0 (
  echo.
  echo [SERVER TERMINATED WITH ERROR CODE %errorlevel%]
)
echo.
echo Press any key to close this window...
pause

