@echo off
echo ================================================
echo Chess Tree Generator GUI - Windows Installation
echo ================================================
echo.

echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo Python found! Checking pip...
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: pip is not available
    echo Trying to install pip...
    python -m ensurepip --upgrade
)

echo Installing Python dependencies...
python -m pip install python-chess psutil

if %errorlevel% neq 0 (
    echo.
    echo WARNING: Some dependencies may not have installed correctly
    echo You can try running the GUI anyway, or install manually:
    echo   python -m pip install python-chess psutil
    echo.
) else (
    echo.
    echo Installation successful!
)

echo.
echo Testing GUI startup...
python -c "import tkinter; import chess; import psutil; print('All dependencies OK!')" 2>nul
if %errorlevel% neq 0 (
    echo WARNING: Some imports failed. GUI may not work properly.
    echo Make sure all dependencies are installed.
) else (
    echo All dependencies verified!
)

echo.
echo Installation complete!
echo.
echo To run the GUI:
echo   Double-click launch_gui.bat
echo   OR run: python chess_gui.py
echo.
pause