#!/usr/bin/env python3
"""
10x Canva Skills - Setup Script
Run this ONCE before using the skills.

Creates a virtual environment to keep your system Python clean.

Usage:
    python setup.py
    python setup.py --force  # Force reinstall even if already set up
"""

import subprocess
import sys
import os
from pathlib import Path

# Configuration
BASE_DIR = Path(__file__).parent
VENV_DIR = BASE_DIR / '.venv'
SETUP_MARKER_FILE = BASE_DIR / '.setup_complete'


def is_setup_complete():
    """Check if setup has already been completed"""
    return SETUP_MARKER_FILE.exists() and VENV_DIR.exists()


def mark_setup_complete():
    """Create marker file to indicate setup is complete"""
    # Get venv python path for reference
    if sys.platform == 'win32':
        venv_python = VENV_DIR / 'Scripts' / 'python.exe'
    else:
        venv_python = VENV_DIR / 'bin' / 'python'

    SETUP_MARKER_FILE.write_text(
        f"Setup completed successfully.\n"
        f"Virtual environment: {VENV_DIR}\n"
        f"Python: {venv_python}\n"
        f"\n"
        f"Delete this file to force reinstallation.\n"
        f"Or run: python setup.py --force\n"
    )
    print(f"\n[OK] Created setup marker: {SETUP_MARKER_FILE.name}")


def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print(f"[X] Python 3.9+ required. You have Python {version.major}.{version.minor}")
        return False
    print(f"[OK] Python {version.major}.{version.minor}.{version.micro} detected")
    return True


def create_virtual_environment():
    """Create virtual environment"""
    print("\n[*] Creating virtual environment...")

    if VENV_DIR.exists():
        print(f"    Virtual environment already exists at: {VENV_DIR}")
        return True

    try:
        subprocess.check_call([
            sys.executable, '-m', 'venv', str(VENV_DIR)
        ])
        print(f"[OK] Virtual environment created at: {VENV_DIR}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[X] Failed to create virtual environment: {e}")
        return False


def get_venv_python():
    """Get path to Python in virtual environment"""
    if sys.platform == 'win32':
        return VENV_DIR / 'Scripts' / 'python.exe'
    else:
        return VENV_DIR / 'bin' / 'python'


def get_venv_pip():
    """Get path to pip in virtual environment"""
    if sys.platform == 'win32':
        return VENV_DIR / 'Scripts' / 'pip.exe'
    else:
        return VENV_DIR / 'bin' / 'pip'


def install_requirements():
    """Install required packages into virtual environment"""
    print("\n[*] Installing Python dependencies into virtual environment...")
    print("-" * 50)

    requirements_file = BASE_DIR / 'requirements.txt'

    if not requirements_file.exists():
        print("[X] requirements.txt not found!")
        return False

    venv_pip = get_venv_pip()

    if not venv_pip.exists():
        print("[X] Virtual environment pip not found!")
        return False

    try:
        # Upgrade pip first (ignore errors as venv pip works fine)
        subprocess.run(
            [str(venv_pip), 'install', '--upgrade', 'pip'],
            capture_output=True
        )

        # Install requirements
        result = subprocess.run(
            [str(venv_pip), 'install', '-r', str(requirements_file)],
            capture_output=False
        )

        if result.returncode == 0:
            print("\n[OK] All dependencies installed successfully!")
            return True
        else:
            print("\n[X] Some packages failed to install")
            return False
    except Exception as e:
        print(f"\n[X] Failed to install dependencies: {e}")
        return False


def create_directories():
    """Create necessary directories"""
    print("\n[*] Creating directories...")

    directories = [
        BASE_DIR / 'input',
        BASE_DIR / 'output' / 'working',
        BASE_DIR / 'output' / 'pdf',
        BASE_DIR / 'output' / 'pptx',
        BASE_DIR / 'output' / 'docx',
        BASE_DIR / 'output' / 'xlsx',
        BASE_DIR / 'output' / 'exports',
        BASE_DIR / 'output' / 'logs',
    ]

    for dir_path in directories:
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"  + {dir_path.relative_to(BASE_DIR)}")

    print("[OK] Directories created!")
    return True


def check_env_file():
    """Check .env file exists and remind user to configure"""
    env_file = BASE_DIR / '.env'

    if env_file.exists():
        print("\n[*] .env file found")
        print("    Edit .env to add your Canva API credentials (optional for local file editing)")
    else:
        print("\n[!] .env file not found!")
        print("    Create a .env file with your Canva API credentials if you want to use Canva features")


def verify_installation():
    """Verify key packages are installed in virtual environment"""
    print("\n[*] Verifying installation...")

    venv_python = get_venv_python()

    packages = [
        ('requests', 'Canva API'),
        ('PyPDF2', 'PDF editing'),
        ('pptx', 'PowerPoint editing'),
        ('docx', 'Word editing'),
        ('openpyxl', 'Excel editing'),
        ('PIL', 'Image processing'),
    ]

    all_good = True
    for package, purpose in packages:
        try:
            # Check import in venv
            result = subprocess.run(
                [str(venv_python), '-c', f'import {package}'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print(f"  [OK] {package} ({purpose})")
            else:
                print(f"  [X] {package} ({purpose}) - NOT INSTALLED")
                all_good = False
        except Exception:
            print(f"  [X] {package} ({purpose}) - CHECK FAILED")
            all_good = False

    return all_good


def create_run_script():
    """Create helper scripts to run Python with venv"""
    # Windows batch file
    if sys.platform == 'win32':
        bat_content = f'''@echo off
"{VENV_DIR}\\Scripts\\python.exe" %*
'''
        bat_file = BASE_DIR / 'run_python.bat'
        bat_file.write_text(bat_content)
        print(f"[OK] Created {bat_file.name} - use this to run Python scripts")


def main():
    # Check for --force flag
    force_reinstall = '--force' in sys.argv or '-f' in sys.argv

    # Check if setup already done
    if is_setup_complete() and not force_reinstall:
        print("=" * 60)
        print("10x CANVA SKILLS - ALREADY SET UP")
        print("=" * 60)
        print("\nSetup has already been completed.")
        print(f"Virtual environment: {VENV_DIR}")
        print("\nAll dependencies are installed and ready to use.")
        print("\nTo force reinstallation, run:")
        print("  python setup.py --force")
        print("\nOr delete the .setup_complete file and run again.")
        return

    print("=" * 60)
    print("10x CANVA SKILLS - SETUP")
    print("=" * 60)

    if force_reinstall:
        print("\n[FORCE MODE] Reinstalling all dependencies...\n")
    else:
        print("\nThis script will set up everything you need to use the skills.")
        print("A virtual environment will be created to keep your system clean.\n")

    # Check Python version
    if not check_python_version():
        sys.exit(1)

    # Create virtual environment
    if not create_virtual_environment():
        print("\n[X] Failed to create virtual environment")
        sys.exit(1)

    # Install requirements
    if not install_requirements():
        print("\n[!] Some packages failed to install.")
        print("Try running manually:")
        print(f"  {get_venv_pip()} install -r requirements.txt")

    # Create directories
    create_directories()

    # Check .env file
    check_env_file()

    # Create helper scripts
    create_run_script()

    # Verify installation
    if verify_installation():
        # Mark setup as complete only if verification passes
        mark_setup_complete()

    print("\n" + "=" * 60)
    print("SETUP COMPLETE!")
    print("=" * 60)

    # Platform-specific instructions
    if sys.platform == 'win32':
        activate_cmd = f".venv\\Scripts\\activate"
        python_cmd = ".venv\\Scripts\\python.exe"
    else:
        activate_cmd = "source .venv/bin/activate"
        python_cmd = ".venv/bin/python"

    print(f"""
Virtual Environment Created!
----------------------------
Location: {VENV_DIR}

To run scripts manually:
  {python_cmd} scripts/script_name.py

Or activate the environment first:
  {activate_cmd}

Next steps:

1. (Optional) Configure Canva API:
   - Edit .env file with your Canva credentials
   - Only needed if you want to use Canva cloud features

2. Start Claude Code in this folder:
   - The skills will be automatically available
   - Claude Code will use the virtual environment

3. Try these commands:
   - "Edit my presentation.pptx"  (local file editing)
   - "Show my Canva designs"      (requires Canva API)
   - "Export my report as PDF"    (local conversion)

Note: Your system Python packages remain UNCHANGED.
All skill dependencies are isolated in the .venv folder.
""")


if __name__ == '__main__':
    main()
