@echo off
chcp 65001 >nul
rem ============================================================
rem  LifeAfter Wiki 本地服务（3D 预览必须走 HTTP，不能双击 HTML）
rem  双击本文件 → 自动起服务并打开看板
rem  关闭窗口 = 停止服务
rem ============================================================
cd /d "%~dp0"
set PY=C:\Users\Administrator\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe
if not exist "%PY%" set PY=python
echo 正在启动 LifeAfter Wiki 本地服务 (127.0.0.1:8765) ...
start "" http://127.0.0.1:8765/board.html?b=weapon_skin_sfx_text_sources&view=wiki&sort=id&dir=desc
"%PY%" tools\wiki_server.py --host 127.0.0.1 --port 8765
pause
