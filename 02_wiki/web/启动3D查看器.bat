@echo off
title Lifeafter 3D Viewer Server
cd /d "%~dp0"
powershell -NoProfile -Command "try { $c=New-Object Net.Sockets.TcpClient; $c.Connect('127.0.0.1',8770); $c.Close(); exit 0 } catch { exit 1 }"
if not errorlevel 1 (
  echo Server already running on port 8770. Opening browser...
  start "" "http://127.0.0.1:8770/fashion3d.html"
  exit /b 0
)
echo.
echo  Lifeafter 3D viewer
echo  Serving: %CD%
echo  URL: http://127.0.0.1:8770/fashion3d.html
echo  Keep this window OPEN while viewing. Close it to stop the server.
echo.
start "" /b powershell -NoProfile -Command "Start-Sleep -Seconds 2; Start-Process 'http://127.0.0.1:8770/fashion3d.html'"
python --version >nul 2>nul
if errorlevel 1 (
  py -3 -m http.server 8770 --bind 127.0.0.1
) else (
  python -m http.server 8770 --bind 127.0.0.1
)
