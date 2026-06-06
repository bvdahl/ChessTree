@echo off
setlocal enabledelayedexpansion

REM ============================================================
REM  Chess Tree Analyzer - one-click update & build
REM ------------------------------------------------------------
REM  Double-click this file. It will:
REM    1) ask for administrator access (click "Yes" once),
REM    2) download or update the project in C:\Apps\ChessTree,
REM    3) install everything it needs,
REM    4) build the Windows installer.
REM
REM  The work runs in a window launched with "cmd /k", so the
REM  window STAYS OPEN no matter what happens. You will always be
REM  able to read any error message instead of it flashing closed.
REM ============================================================

REM If this is our elevated, stay-open window, go straight to work.
if "%~1"=="elevated" goto :run

REM First launch: relaunch as Administrator in a window that stays open.
REM A tiny VBScript is used so the file path and the "/k" flag are passed
REM through reliably (this is the part that kept failing before).
echo Requesting administrator access (please click "Yes") ...
set "VBS=%temp%\chesstree_elevate.vbs"
echo Set UAC = CreateObject^("Shell.Application"^) > "%VBS%"
echo UAC.ShellExecute "cmd.exe", "/k ""%~f0"" elevated", "", "runas", 1 >> "%VBS%"
cscript //nologo "%VBS%"
del "%VBS%" >nul 2>&1
exit /b

:run
set "REPO=https://github.com/bvdahl/ChessTree"
set "APPDIR=C:\Apps\ChessTree"

echo.
echo ============================================
echo   Chess Tree Analyzer : update and build
echo ============================================
echo.

REM --- Make sure the tools we need are installed ---
where git >nul 2>&1
if errorlevel 1 (
  echo ERROR: Git is not installed or not on your PATH.
  echo Install it from https://git-scm.com/download/win then run this again.
  goto :end
)
where npm >nul 2>&1
if errorlevel 1 (
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
  if errorlevel 1 ( echo. & echo ERROR: download ^(git clone^) failed. & goto :end )
  cd /d "%APPDIR%"
)
if errorlevel 1 ( echo. & echo ERROR: getting the code failed. & goto :end )

REM --- Install dependencies ---
REM The shared lock file points at Replit's private servers, so remove it and
REM let npm rebuild it from the public registry.
if exist package-lock.json del /f /q package-lock.json
echo.
echo Installing dependencies (a few minutes the first time) ...
call npm install
if errorlevel 1 ( echo. & echo ERROR: npm install failed. & goto :end )

REM --- Build the installer ---
echo.
echo Cleaning previous build ...
if exist release rmdir /s /q release
echo.
echo Building the Windows installer (this can take several minutes) ...
call npm run dist
if errorlevel 1 ( echo. & echo ERROR: build failed. & goto :end )

echo.
echo ============================================
echo   DONE!
echo ============================================
echo Your installer is in: %APPDIR%\release
echo Look for: "Chess Tree Analyzer Setup ....exe"
start "" "%APPDIR%\release"

:end
echo.
echo ------------------------------------------------------------
echo This window will stay open so you can read the messages above.
echo When you are finished, just close it.
echo ------------------------------------------------------------
echo.
pause
exit /b
