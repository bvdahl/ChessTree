@echo off
REM Chess Tree Generator GUI Launcher (No Console Window)
REM This batch file starts the GUI without showing a command window

REM Try to find Python executable
set PYTHON_EXE=
if exist "C:\Program Files\Python312\python.exe" set PYTHON_EXE=C:\Program Files\Python312\python.exe
if exist "C:\Program Files\Python311\python.exe" set PYTHON_EXE=C:\Program Files\Python311\python.exe
if exist "C:\Program Files\Python310\python.exe" set PYTHON_EXE=C:\Program Files\Python310\python.exe
if exist "C:\Python312\python.exe" set PYTHON_EXE=C:\Python312\python.exe
if exist "C:\Python311\python.exe" set PYTHON_EXE=C:\Python311\python.exe
if exist "C:\Python310\python.exe" set PYTHON_EXE=C:\Python310\python.exe

REM If Python not found in common locations, try PATH
if "%PYTHON_EXE%"=="" (
    where python >nul 2>&1
    if errorlevel 1 (
        echo Python not found. Please install Python or add it to your PATH.
        pause
        exit /b 1
    ) else (
        set PYTHON_EXE=python
    )
)

REM Start the GUI without showing console window
start "" "%PYTHON_EXE%" run_gui_silent.pyw

REM Exit immediately without keeping the batch window open
exit