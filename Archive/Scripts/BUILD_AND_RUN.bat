@echo off
echo ========================================
echo Chess Tree Analyzer - Build and Run Tool
echo ========================================
echo.

REM Check if .NET SDK is installed
dotnet --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: .NET SDK is not installed or not in PATH
    echo Please install .NET 8.0 SDK from https://dotnet.microsoft.com/download
    pause
    exit /b 1
)

echo Detected .NET SDK version:
dotnet --version
echo.

REM Navigate to the ChessTreeAnalyzer directory
cd ChessTreeAnalyzer

echo Building Chess Tree Analyzer...
echo --------------------------------
dotnet build -c Release

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Build failed!
    echo Please check the error messages above.
    pause
    exit /b 1
)

echo.
echo Build successful!
echo.
echo Starting Chess Tree Analyzer...
echo --------------------------------
cd bin\Release\net8.0-windows
start ChessTreeAnalyzer.exe

echo.
echo Application launched!
echo You can close this window.
pause