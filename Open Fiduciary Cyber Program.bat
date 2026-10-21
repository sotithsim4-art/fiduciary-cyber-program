@echo off
cd /d "%~dp0"
where python >nul 2>&1
if errorlevel 1 (
  echo Python was not found.
  echo Install Python from python.org, then double-click this file again.
  pause
  exit /b 1
)
powershell -NoProfile -Command "try { $r = Invoke-WebRequest -UseBasicParsing 'http://127.0.0.1:8765/' -TimeoutSec 2; if ($r.StatusCode -eq 200) { exit 0 } else { exit 1 } } catch { exit 1 }"
if errorlevel 1 (
  start "Close this window to quit" /MIN python app.py
  powershell -NoProfile -Command "$ok = $false; foreach ($i in 1..40) { try { Invoke-WebRequest -UseBasicParsing 'http://127.0.0.1:8765/' -TimeoutSec 1 | Out-Null; $ok = $true; break } catch { Start-Sleep -Milliseconds 250 } }; if ($ok) { exit 0 } else { exit 1 }"
  if errorlevel 1 (
    echo The app did not start.
    pause
    exit /b 1
  )
)
set "EDGE=%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"
if not exist "%EDGE%" set "EDGE=%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"
if exist "%EDGE%" (
  start "" "%EDGE%" --app=http://127.0.0.1:8765/
) else (
  start "" http://127.0.0.1:8765/
)
