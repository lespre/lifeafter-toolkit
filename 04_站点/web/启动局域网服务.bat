@echo off
chcp 65001 >nul
title Lifeafter Wiki 局域网服务 (8766)
echo ============================================
echo   明日之后 Wiki · 局域网访问
echo ============================================
echo.
echo   本机： http://127.0.0.1:8765/zhanshen.html
echo   手机： http://192.168.1.100:8765/zhanshen.html
echo   首页： http://192.168.1.100:8765/wiki.html
echo.
echo   （手机须与本机同一 WiFi；此窗口不能关，关了服务就停）
echo   首次使用需管理员放行一次防火墙：
echo     netsh advfirewall firewall add rule name="LifeafterWiki8765" dir=in action=allow protocol=TCP localport=8765
echo ============================================
echo.
cd /d "%~dp0"
"C:\Users\<user>\py312_env\Scripts\python.exe" tools\wiki_server.py --host 0.0.0.0 --port 8765
pause
