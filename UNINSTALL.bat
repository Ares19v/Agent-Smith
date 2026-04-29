@echo off
setlocal
echo ==============================================================
echo   AGENT SMITH — Uninstaller
echo ==============================================================
echo This will remove the Python virtual environment to reclaim space.
echo Your agent data and configurations will NOT be deleted.
set /p "CHOICE=Are you sure you want to uninstall the environment? (Y/N): "
if /I "%CHOICE%" neq "Y" (
    echo [INFO] Uninstall cancelled.
    pause
    exit /b 0
)

if exist venv (
    echo [INFO] Removing virtual environment 'venv'...
    rmdir /s /q venv
    echo [INFO] Uninstallation complete.
) else (
    echo [INFO] Virtual environment not found. Nothing to remove.
)

pause
