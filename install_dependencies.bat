@echo off
echo ===================================================
echo Installing Luminary AI Dependencies...
echo ===================================================

set PYTHON_EXE="C:\Users\Kausar\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"

echo [1/2] Installing PyTorch with CUDA 12.1 acceleration...
%PYTHON_EXE% -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

echo [2/2] Installing Diffusers, Transformers, Accelerate, Safetensors, and Requests...
%PYTHON_EXE% -m pip install diffusers transformers accelerate safetensors requests pillow

echo ===================================================
echo Luminary dependencies installation complete!
echo ===================================================
pause
