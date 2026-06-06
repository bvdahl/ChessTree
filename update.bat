@echo off
setlocal enabledelayedexpansion

REM ============================================================
REM  Chess Tree Analyzer - one-click update, build & publish
REM ------------------------------------------------------------
REM  Double-click this file (from ANY folder - even from inside
REM  C:\Apps\ChessTree). It will:
REM    1) ask for administrator access (click "Yes" once),
REM    2) download or update the project in C:\Apps\ChessTree,
REM    3) install everything it needs,
REM    4) build the Windows installer AND publish it to GitHub,
REM       so every installed copy of the app updates itself.
REM
REM  The work runs in a window launched with "cmd /k", so the
REM  window STAYS OPEN no matter what happens. You will always be
REM  able to read any error message instead of it flashing closed.
REM ============================================================

REM "go" means: we are already in the elevated, stay-open window.
if "%~1"=="go" goto :run

REM First launch: relaunch as Administrator in a window that stays open.
REM A tiny VBScript is used so the file path and the "/k" flag are passed
REM through reliably.
echo Requesting administrator access (please click "Yes") ...
set "VBS=%temp%\chesstree_elevate.vbs"
echo Set UAC = CreateObject^("Shell.Application"^) > "%VBS%"
echo UAC.ShellExecute "cmd.exe", "/k ""%~f0"" go", "", "runas", 1 >> "%VBS%"
cscript //nologo "%VBS%"
del "%VBS%" >nul 2>&1
exit /b

:run
set "REPO=https://github.com/bvdahl/ChessTree"
set "APPDIR=C:\Apps\ChessTree"

REM If we are running from INSIDE the folder we manage, continue from a temp
REM copy of ourselves. That way we can freely clear/re-create the folder
REM (and overwrite this very script) without breaking the running batch.
if /i "%~dp0"=="%APPDIR%\" (
  echo Preparing ...
  copy /y "%~f0" "%temp%\chesstree_update.bat" >nul
  "%temp%\chesstree_update.bat" go
  exit /b
)

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
  git fetch origin
  if errorlevel 1 ( echo. & echo ERROR: could not download the latest code. & goto :end )
  git reset --hard origin/main
  if errorlevel 1 ( echo. & echo ERROR: could not update the files. & goto :end )
) else (
  if exist "%APPDIR%" (
    echo Folder %APPDIR% already exists but is not a project copy - clearing it ...
    rmdir /s /q "%APPDIR%"
  )
  echo Downloading a fresh copy to %APPDIR% ...
  git clone "%REPO%" "%APPDIR%"
  if errorlevel 1 ( echo. & echo ERROR: download ^(git clone^) failed. & goto :end )
  cd /d "%APPDIR%"
)

REM --- Give this build an ever-increasing version number ---
REM Auto-update only notices a NEW version number, so we base it on the number
REM of commits, which always goes up each time you push a change.
for /f "delims=" %%i in ('git rev-list --count HEAD') do set "BUILDNO=%%i"
if "%BUILDNO%"=="" set "BUILDNO=0"
echo.
echo This build will be version 1.0.%BUILDNO%
call npm version 1.0.%BUILDNO% --no-git-tag-version --allow-same-version >nul 2>&1

REM --- Install dependencies ---
REM The shared lock file points at Replit's private servers, so remove it and
REM let npm rebuild it from the public registry.
if exist package-lock.json del /f /q package-lock.json
echo.
echo Installing dependencies (a few minutes the first time) ...
call npm install
if errorlevel 1 ( echo. & echo ERROR: npm install failed. & goto :end )

REM --- Make sure we have a GitHub token so the new version can be published ---
REM (Published versions are what let every installed app update itself.)
if "%GH_TOKEN%"=="" (
  echo.
  echo ------------------------------------------------------------
  echo  One-time setup: a GitHub token is needed to publish updates.
  echo  Create one at  https://github.com/settings/tokens
  echo  ^(use a "classic" token with the "repo" checkbox ticked^).
  echo ------------------------------------------------------------
  set /p "GH_TOKEN=Paste the token here and press Enter: "
  if not "!GH_TOKEN!"=="" (
    setx GH_TOKEN "!GH_TOKEN!" >nul
    echo Saved - you will not be asked for it again on this computer.
  )
)
if "%GH_TOKEN%"=="" ( echo. & echo ERROR: no GitHub token given, so the update cannot be published. & goto :end )

REM --- Build the installer AND publish it for auto-update ---
echo.
echo Cleaning previous build ...
if exist release rmdir /s /q release
echo.
echo Building and publishing version 1.0.%BUILDNO% (this can take several minutes) ...
call npm run release
if errorlevel 1 ( echo. & echo ERROR: build or publish failed. & goto :end )

echo.
echo ============================================
echo   DONE!
echo ============================================
echo Version 1.0.%BUILDNO% was published to GitHub.
echo Installed copies of the app will now update themselves automatically.
echo.
echo The installer is also here if you need it: %APPDIR%\release
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
