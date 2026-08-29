@echo off
setlocal enabledelayedexpansion
title Luminary AI - Dedicated Virtual Environment Setup
color 0B
echo ========================================================
echo   Luminary AI - Dedicated Virtual Environment Setup
echo   Target: %~dp0.venv
echo ========================================================
echo.

:: 1. Search for a suitable base Python interpreter to create the venv
set "BASE_PY="
set CANDIDATE_1="python"
set CANDIDATE_2="py"
set CANDIDATE_3="%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
set CANDIDATE_4="%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
set CANDIDATE_5="%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
set CANDIDATE_6="%ProgramFiles%\Python312\python.exe"
set CANDIDATE_7="%ProgramFiles%\Python311\python.exe"
set CANDIDATE_8="%ProgramFiles%\Python310\python.exe"
set CANDIDATE_9="%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"

for /L %%i in (1,1,9) do (
  if not defined BASE_PY (
    set "CURRENT_CANDIDATE=!CANDIDATE_%%i!"
    !CURRENT_CANDIDATE! -c "import sys; sys.exit(0)" >nul 2>nul
    if !errorlevel! equ 0 (
      set "BASE_PY=!CURRENT_CANDIDATE!"
    )
  )
)

if not defined BASE_PY (
  echo.
  echo [ERROR] No working base Python installation found on system.
  echo Please install Python 3.10+ and ensure it is available on your system.
  echo.
  pause
  exit /b 1
)

echo [1/4] Found base Python: %BASE_PY%

:: 2. Create the dedicated virtual environment if it does not already exist
set "VENV_DIR=%~dp0.venv"
set "VENV_PY=%VENV_DIR%\Scripts\python.exe"

if not exist "%VENV_PY%" (
  echo [2/4] Creating dedicated virtual environment in %VENV_DIR%...
  %BASE_PY% -m venv "%VENV_DIR%"
  if !errorlevel! neq 0 (
    echo [ERROR] Failed to create virtual environment in %VENV_DIR%.
    pause
    exit /b 1
  )
  echo Virtual environment created successfully.
) else (
  echo [2/4] Dedicated virtual environment already exists in %VENV_DIR%.
)

:: 3. Upgrade pip
echo.
echo [3/4] Upgrading pip in dedicated virtual environment...
"%VENV_PY%" -m pip install --upgrade pip

:: 4. Install all core dependencies
echo.
echo [4/4] Installing all Luminary AI dependencies into dedicated environment...
echo - Installing PyTorch with CUDA / official wheel index...
"%VENV_PY%" -m pip install torch torchvision --extra-index-url https://download.pytorch.org/whl/cu121

echo.
echo - Installing Diffusers, Transformers, Accelerate, Safetensors, Office tools, and Core libraries...
"%VENV_PY%" -m pip install diffusers transformers accelerate safetensors requests pillow python-docx python-pptx openpyxl pandas reportlab numpy python-dotenv pydantic

echo.
echo ========================================================
echo   Luminary AI Dedicated Environment Setup Complete!
echo   Interpreter: %VENV_PY%
echo   You can now start the server with: workSTART_LUMINARY_BACKEND.bat
echo ========================================================
echo.
if "%~1"=="" pause
