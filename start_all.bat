@echo off
echo Starting CAREERPILOT Backend API (FastAPI)...
start "CAREERPILOT Backend" cmd /k "cd /d %~dp0 && python -m uvicorn server:app --host 127.0.0.1 --port 8000 --reload"

echo Starting CAREERPILOT Frontend UI (React + Vite)...
start "CAREERPILOT Frontend" cmd /k "cd /d %~dp0\frontend && npm.cmd run dev"

echo Opening browser at http://localhost:5173 ...
timeout /t 3 >nul
start http://localhost:5173
