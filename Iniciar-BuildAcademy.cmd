@echo off
cd /d "%~dp0"
echo BuildAcademy: abri http://127.0.0.1:8765/ en tu navegador.
echo Para detener el servidor, presiona Ctrl+C.
python -m http.server 8765 --bind 127.0.0.1 --directory dist
pause
