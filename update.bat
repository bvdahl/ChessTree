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
REM    4) check your GitHub token CAN publish (clear message if not),
REM    5) build the Windows installer AND publish it to GitHub,
REM       so every installed copy of the app updates itself.
REM
REM  Everything you see is ALSO written to a log file
REM  (C:\Apps\chesstree-update-log.txt) so you never lose an error
REM  message even if the window is closed. The window itself is
REM  launched with "cmd /k" so it stays open too.
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

REM --- Set up a log file in a folder that always exists ---
REM (NOT the Desktop, which on many PCs is moved into OneDrive and then a
REM plain file path to it no longer works.)
if not exist "C:\Apps" mkdir "C:\Apps"
set "LOG=C:\Apps\chesstree-update-log.txt"
> "%LOG%" echo Chess Tree Analyzer - update log - %date% %time%

call :say ""
call :say "============================================"
call :say "   Chess Tree Analyzer : update and build"
call :say "============================================"
call :say ""
call :say "A copy of everything below is being saved to:"
call :say "   %LOG%"
call :say "If anything goes wrong, you can open that file later to read it."
call :say ""

REM --- Make sure the tools we need are installed ---
where git >nul 2>&1
if errorlevel 1 (
  call :say "ERROR: Git is not installed or not on your PATH."
  call :say "Install it from https://git-scm.com/download/win then run this again."
  goto :end
)
where npm >nul 2>&1
if errorlevel 1 (
  call :say "ERROR: Node.js / npm is not installed or not on your PATH."
  call :say "Install the LTS version from https://nodejs.org then run this again."
  goto :end
)

REM --- Get the latest code ---
if exist "%APPDIR%\.git" (
  call :say "Updating existing copy in %APPDIR% ..."
  cd /d "%APPDIR%"
  call :runtee git fetch origin
  if errorlevel 1 ( call :say "ERROR: could not download the latest code." & goto :end )
  call :runtee git reset --hard origin/main
  if errorlevel 1 ( call :say "ERROR: could not update the files." & goto :end )
) else (
  if exist "%APPDIR%" (
    call :say "Folder %APPDIR% already exists but is not a project copy - clearing it ..."
    rmdir /s /q "%APPDIR%"
  )
  call :say "Downloading a fresh copy to %APPDIR% ..."
  call :runtee git clone "%REPO%" "%APPDIR%"
  if errorlevel 1 ( call :say "ERROR: download (git clone) failed." & goto :end )
  cd /d "%APPDIR%"
)

REM --- Give this build an ever-increasing version number ---
REM Auto-update only notices a NEW version number, so we base it on the number
REM of commits, which always goes up each time you push a change.
for /f "delims=" %%i in ('git rev-list --count HEAD') do set "BUILDNO=%%i"
if "%BUILDNO%"=="" set "BUILDNO=0"
call :say ""
call :say "This build will be version 1.0.%BUILDNO%"
call npm version 1.0.%BUILDNO% --no-git-tag-version --allow-same-version >nul 2>&1

REM --- Make sure the GitHub token can actually publish BEFORE the long build ---
REM (Published versions are what let every installed app update itself.)
call :ensure_token
if errorlevel 1 goto :end

REM --- Install dependencies ---
REM The shared lock file points at Replit's private servers, so remove it and
REM let npm rebuild it from the public registry.
if exist package-lock.json del /f /q package-lock.json
call :say ""
call :say "Installing dependencies (a few minutes the first time) ..."
REM --no-audit / --no-fund keep routine noise (the "N vulnerabilities" report
REM and the funding notice) off the screen. They are not actionable here, and
REM "npm audit fix --force" can break the Electron build, so we never run it.
REM A real install failure still sets a non-zero exit code and stops below.
call :runtee npm install --no-audit --no-fund
if errorlevel 1 ( call :say "ERROR: npm install failed." & goto :end )

REM --- Build the installer AND publish it for auto-update ---
call :say ""
call :say "Cleaning previous build ..."
if exist release rmdir /s /q release
call :say ""
call :say "Building and publishing version 1.0.%BUILDNO% (this can take several minutes) ..."
call :runtee npm run release
if errorlevel 1 (
  call :say ""
  call :say "------------------------------------------------------------"
  call :say "ERROR: the build or publish step failed."
  call :say ""
  call :say "The most common cause is the GitHub token not being allowed to"
  call :say "publish. If the messages above mention 404, Not Found, or"
  call :say "authentication, make a NEW classic token with the 'repo' box"
  call :say "ticked at https://github.com/settings/tokens and run this again"
  call :say "(it will offer to replace the saved token)."
  call :say ""
  call :say "The full details are saved in:"
  call :say "   %LOG%"
  call :say "------------------------------------------------------------"
  goto :end
)

call :say ""
call :say "============================================"
call :say "   DONE!"
call :say "============================================"
call :say "Version 1.0.%BUILDNO% was published to GitHub."
call :say "Installed copies of the app will now update themselves automatically."
call :say ""
call :say "The installer is also here if you need it: %APPDIR%\release"
call :say "Look for: Chess Tree Analyzer Setup ....exe"
start "" "%APPDIR%\release"

:end
call :say ""
call :say "------------------------------------------------------------"
call :say "A full copy of these messages was saved to:"
call :say "   %LOG%"
call :say "This window will stay open so you can read the messages above."
call :say "When you are finished, just close it."
call :say "------------------------------------------------------------"
echo.
pause
exit /b

REM ============================================================
REM  Helpers
REM ============================================================

REM ---- :say "message" : print to the screen AND append to the log ----
:say
setlocal
set "MSG=%~1"
echo(%MSG%
>>"%LOG%" echo(%MSG%
endlocal
exit /b

REM ---- :runtee <command...> : run a command, showing its output on screen
REM      AND appending it to the log, while preserving the real exit code ----
REM
REM      The "2>&1" is placed INSIDE the inner "cmd /c '...'" on purpose. Tools
REM      like git and npm write their normal status lines and warnings to the
REM      error stream (stderr). If we merged that stream at the PowerShell layer
REM      instead, PowerShell would paint every such line red and wrap it in a
REM      scary "NativeCommandError", making a perfectly successful run look like
REM      it is full of errors. Merging inside cmd turns those lines into plain
REM      text BEFORE PowerShell sees them, so PowerShell just relays ordinary
REM      output. The real exit code is still cmd's (git/npm) exit code, so
REM      genuine failures are still detected via $LASTEXITCODE below.
:runtee
powershell -NoProfile -ExecutionPolicy Bypass -Command "& cmd /c '%* 2>&1' | Tee-Object -FilePath '%LOG%' -Append; exit $LASTEXITCODE"
exit /b

REM ---- :ensure_token : make sure we have a token that can publish.
REM      Returns errorlevel 0 to continue, 1 to abort. ----
:ensure_token
if "%GH_TOKEN%"=="" call :ask_token
if "%GH_TOKEN%"=="" (
  call :say "ERROR: no GitHub token was given, so the update cannot be published."
  exit /b 1
)

call :say ""
call :say "Checking that your GitHub token is allowed to publish ..."
call :validate_token
if "!TOKEN_OK!"=="1" (
  call :say "Token looks good - it has permission to publish."
  exit /b 0
)

REM Could we not verify it (no internet / unexpected reply)? Warn but carry on.
if "!VREASON!"=="nonet" (
  call :say "Note: could not reach GitHub to verify the token right now."
  call :say "Continuing - if publishing fails, check your internet and the token."
  exit /b 0
)
if "!VREASON!"=="other" (
  call :say "Note: could not clearly verify the token. Continuing anyway."
  exit /b 0
)

REM Definite problems: explain in plain language.
if "!VREASON!"=="badtoken" (
  call :say ""
  call :say "PROBLEM: GitHub rejected this token. It is probably wrong or expired."
)
if "!VREASON!"=="noscope" (
  call :say ""
  call :say "PROBLEM: this token works, but it does NOT have the 'repo' permission,"
  call :say "so GitHub will not let it publish a new version."
)
call :say ""
call :say "To fix it, make a fresh token:"
call :say "  1) Go to  https://github.com/settings/tokens"
call :say "  2) Click  Generate new token (classic)"
call :say "  3) TICK the box labelled  repo"
call :say "  4) Generate the token and copy it"
call :say ""
choice /c RCA /n /m "Press R to enter a new token, C to try anyway, or A to abort: "
if errorlevel 3 ( call :say "Aborted." & exit /b 1 )
if errorlevel 2 ( call :say "Continuing with the current token ..." & exit /b 0 )
REM errorlevel 1 = R = re-enter
call :ask_token
goto :ensure_token

REM ---- :ask_token : prompt for a token and remember it ----
:ask_token
call :say ""
call :say "------------------------------------------------------------"
call :say " A GitHub token is needed to publish updates."
call :say "  1) Go to  https://github.com/settings/tokens"
call :say "  2) Click  Generate new token (classic)"
call :say "  3) TICK the box labelled  repo"
call :say "  4) Generate the token and copy it"
call :say "------------------------------------------------------------"
set "GH_TOKEN="
set /p "GH_TOKEN=Paste the token here and press Enter: "
if not "!GH_TOKEN!"=="" (
  setx GH_TOKEN "!GH_TOKEN!" >nul
  call :say "Saved - it will be remembered on this computer."
)
exit /b

REM ---- :validate_token : sets TOKEN_OK=1 if the token can publish.
REM      Otherwise sets VREASON to one of:
REM        noscope  - authenticated but missing the repo permission
REM        badtoken - GitHub rejected it (401/403)
REM        nonet    - could not reach GitHub
REM        other    - some other unexpected response
REM
REM      A tiny PowerShell check asks GitHub for the token's scopes and
REM      matches them EXACTLY (comma-separated), so look-alike scopes such as
REM      repo:status or admin:repo_hook are NOT mistaken for the real "repo".
REM      The token is read from the environment (GH_TOKEN), never put on the
REM      command line, so it cannot end up in the log. ----
:validate_token
set "TOKEN_OK="
set "VREASON="
powershell -NoProfile -ExecutionPolicy Bypass -Command "try { $h=@{Authorization=('Bearer '+$env:GH_TOKEN);'User-Agent'='chesstree-update'}; $r=Invoke-WebRequest -Uri 'https://api.github.com/rate_limit' -Headers $h -UseBasicParsing -ErrorAction Stop; $s=$r.Headers['X-OAuth-Scopes']; if($null -eq $s){$s=''}; $l=$s -split ',' | ForEach-Object { $_.Trim().ToLower() }; if(($l -contains 'repo') -or ($l -contains 'public_repo')){exit 0}else{exit 3} } catch { $resp=$_.Exception.Response; if($resp -ne $null){ $c=[int]$resp.StatusCode; if($c -eq 401 -or $c -eq 403){exit 2}else{exit 5} } exit 4 }"
set "RC=%errorlevel%"
if "%RC%"=="0" ( set "TOKEN_OK=1" & exit /b )
if "%RC%"=="2" ( set "VREASON=badtoken" & exit /b )
if "%RC%"=="3" ( set "VREASON=noscope" & exit /b )
if "%RC%"=="4" ( set "VREASON=nonet" & exit /b )
set "VREASON=other"
exit /b
