@echo off
echo Starting Chess Tree Analyzer...
echo.

REM Navigate to the ChessTreeAnalyzer directory
cd /d "%~dp0"

REM Run the C# application specifying the correct project file
dotnet run --project ChessTreeAnalyzer.csproj --configuration Release

REM Keep window open if there's an error
if errorlevel 1 (
    echo.
    echo Error occurred. Press any key to exit...
    pause >nul
)