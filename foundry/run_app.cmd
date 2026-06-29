@echo off
REM Launcher for the local Retail Router demo app (Foundry)
REM Opens http://localhost:5000
cd /d "%~dp0"
echo Starting the Retail Router app...
echo Open your browser at http://localhost:5000
start "" http://localhost:5000
".venv\Scripts\python.exe" app.py
pause
