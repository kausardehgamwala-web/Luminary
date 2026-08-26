@echo off
title Luminary AI Website and Backend (DeepSeek and Stable Diffusion Connected)
color 0E
echo ========================================================
echo   Luminary AI Website + Backend Running on Port 8000
echo   Website: http://localhost:8000/
echo   Text AI: deepseek-coder:6.7b (Ollama)
echo   Image AI: Stable Diffusion v1-5 (Local CPU)
echo ========================================================
echo.
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do (
  taskkill /PID %%a /F >nul 2>nul
)
"C:\Users\Kausar\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" "%~dp0server.py"
