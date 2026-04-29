@echo off
setlocal
echo ==============================================================
echo   AGENT SMITH — Local Server
echo ==============================================================

if not exist venv (
    echo [ERROR] Virtual environment 'venv' not found. Please run INSTALL.bat first.
    pause
    exit /b 1
)

echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

echo [INFO] Starting Agent Smith...
echo [INFO] Press CTRL+C to stop the server.

:: Open browser automatically
start http://127.0.0.1:8000

:: Run the server from the backend directory
cd backend
uvicorn app:app --host 127.0.0.1 --port 8000 --reload

pause
