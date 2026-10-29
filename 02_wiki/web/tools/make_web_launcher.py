import sys
# -*- coding: utf-8 -*-
"""生成 GBK 编码的 Windows 启动脚本（cmd 默认代码页 936，UTF-8 中文会乱码）。"""
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402

ROOT = pathlib.Path(PROJ)
BODY = r"""@echo off
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
"""

for name in ("启动Web.bat", "start_web.bat"):
    p = ROOT / name
    p.write_bytes(BODY.replace("\n", "\r\n").encode("gbk", errors="replace"))
    print("写入", p, p.stat().st_size, "字节")
