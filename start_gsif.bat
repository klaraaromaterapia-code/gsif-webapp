@echo off
chcp 65001 > nul
echo.
echo  ╔═══════════════════════════════════════════════╗
echo  ║  ✦  GSIF — Global Spiritual Identity Foundation ║
echo  ║      Every Soul Has a Map                      ║
echo  ╚═══════════════════════════════════════════════╝
echo.
echo  Pornind aplicatia web...
echo  URL: http://localhost:5000
echo.
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
start "" "http://localhost:5000"
python -X utf8 app.py
pause
