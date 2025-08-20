@echo off
echo Building Chess Tree Analyzer for Windows...
echo.

REM Navigate to the ChessTreeAnalyzer directory
cd /d "%~dp0"

REM Build the application
echo Building application...
dotnet build ChessTreeAnalyzer.csproj --configuration Release

if errorlevel 1 (
    echo.
    echo Build failed! Press any key to exit...
    pause >nul
    exit /b 1
) else (
    echo.
    echo Build successful!
    echo You can now run the application with: run_windows.bat
    echo Or use: dotnet run --project ChessTreeAnalyzer.csproj --configuration Release
    echo.
    pause
)