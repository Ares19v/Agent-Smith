@echo off
setlocal
echo ==============================================================
echo   AGENT SMITH — Installer
echo ==============================================================
echo [INFO] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH. Please install Python 3.10+.
    pause
    exit /b 1
)

if not exist venv (
    echo [INFO] Virtual environment not found. Creating 'venv'...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
)

echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

echo [INFO] Upgrading pip...
python -m pip install --upgrade pip > nul 2>&1

echo [INFO] Installing backend requirements...
pip install -r backend\requirements.txt

echo ==============================================================
echo [INFO] Installation Complete! You can now run Run_Project.bat.
echo ==============================================================
pause
