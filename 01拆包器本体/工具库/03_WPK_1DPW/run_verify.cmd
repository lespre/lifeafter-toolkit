@echo off
setlocal
py -3 "%~dp0verify_1dpw_entry.py"
exit /b %ERRORLEVEL%
