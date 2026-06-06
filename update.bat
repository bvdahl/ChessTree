@echo off
setlocal enabledelayedexpansion

REM ============================================================
REM  Chess Tree Analyzer - one-click update & build
REM ------------------------------------------------------------
REM  This file is self-contained. You can drop just this .bat
REM  into an empty folder, double-click it, and it will:
REM    1) download (clone) the whole project the first time,
REM       or update it (git pull) on later runs,
REM    2) install everything it needs,
REM    3) build the Windows installer.
REM  It always works in C:\Apps\ChessTree, no matter where this
REM  .bat file itself is sitting.
REM ============================================================

set "REPO=https://github.com/bvdahl/ChessTree"
set "APPDIR=C:\Apps\ChessTree"

REM --- Re-launch as Administrator (needed so the build can create symlinks) ---
net session >nul 2>&1
if %errorlevel% neq 0 (
  echo Requesting administrator access...
  powershell -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
  exit /b
)

echo.
echo ============================================
echo   Chess Tree Analyzer : update and build
echo ============================================
echo.

REM --- Make sure the tools we need are installed ---
where git >nul 2>&1
if %errorlevel% neq 0 (
  echo ERROR: Git is not installed or not on your PATH.
  echo Install it from https://git-scm.com/download/win then run this again.
  goto :end
)
where npm >nul 2>&1
if %errorlevel% neq 0 (
  echo ERROR: Node.js / npm is not installed or not on your PATH.
  echo Install the LTS version from https://nodejs.org then run this again.
  goto :end
)

REM --- Get the latest code ---
if not exist "C:\Apps" mkdir "C:\Apps"

if exist "%APPDIR%\.git" (
  echo Updating existing copy in %APPDIR% ...
  cd /d "%APPDIR%"
  git pull
) else (
  echo Downloading a fresh copy to %APPDIR% ...
  git clone "%REPO%" "%APPDIR%"
  if %errorlevel% neq 0 ( echo. & echo ERROR: download (git clone) failed. & goto :end )
  cd /d "%APPDIR%"
)
if %errorlevel% neq 0 ( echo. & echo ERROR: getting the code failed. & goto :end )

REM --- Install dependencies ---
REM The shared lock file points at Replit's private servers, so remove it and
REM let npm rebuild it from the public registry.
if exist package-lock.json del /f /q package-lock.json
echo.
echo Installing dependencies (a few minutes the first time) ...
call npm install
if %errorlevel% neq 0 ( echo. & echo ERROR: npm install failed. & goto :end )

REM --- Build the installer ---
echo.
echo Cleaning previous build ...
if exist release rmdir /s /q release
echo.
echo Building the Windows installer (this can take several minutes) ...
call npm run dist
if %errorlevel% neq 0 ( echo. & echo ERROR: build failed. & goto :end )

echo.
echo ============================================
echo   DONE!
echo ============================================
echo Your installer is in: %APPDIR%\release
echo Look for: "Chess Tree Analyzer Setup ....exe"
start "" "%APPDIR%\release"

:end
echo.
pause
