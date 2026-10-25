@echo off
chcp 936 >nul
setlocal enabledelayedexpansion
cd /d "%~dp0"

set "ROOT=%~dp0"
set "PY=%ROOT%00_规范与工具\环境\venv\Scripts\python.exe"
set "APPDIR=%ROOT%02_wiki\web"
set "PORT=8765"
set "URL=http://127.0.0.1:%PORT%/index.html"

powershell -NoProfile -Command "try{(Invoke-WebRequest -UseBasicParsing -TimeoutSec 2 '%URL%')|Out-Null;exit 0}catch{exit 1}" >nul 2>&1
if %errorlevel%==0 goto open

echo 正在启动 wiki 服务，端口 %PORT% ...
pushd "%APPDIR%"
start "wiki_server" /min "%PY%" tools\wiki_server.py --host 0.0.0.0 --port %PORT%
popd

for /l %%i in (1,1,20) do (
  powershell -NoProfile -Command "try{(Invoke-WebRequest -UseBasicParsing -TimeoutSec 2 '%URL%')|Out-Null;exit 0}catch{exit 1}" >nul 2>&1
  if !errorlevel!==0 goto open
  timeout /t 1 >nul
)

echo 服务没起来：请检查 02_wiki\web\tools\wiki_server.py
pause
exit /b 1

:open
echo 已就绪：%URL%
start "" "%URL%"
exit /b 0
