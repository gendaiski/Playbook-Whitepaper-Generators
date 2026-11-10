@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  py -3 -m venv .venv
  if errorlevel 1 goto failed
)
if not exist ".venv\opendraft-installed" (
  ".venv\Scripts\python.exe" -m pip install -e "engine[pdf]" -r requirements.txt
  if errorlevel 1 goto failed
  echo installed > ".venv\opendraft-installed"
)
echo Open http://127.0.0.1:8877 in your browser. Keep this window open.
".venv\Scripts\python.exe" codex-web\server.py
pause
exit /b
:failed
echo Installation failed. Read INSTALLATION-CODEX.md for Python and PDF requirements.
pause
exit /b 1
