#!/usr/bin/env bash
echo "Starting getHire Backend API (FastAPI)..."
python3 -m uvicorn server:app --host 127.0.0.1 --port 8000 --reload &
BACKEND_PID=$!

echo "Starting getHire Frontend UI (React + Vite)..."
cd frontend && npm run dev &
FRONTEND_PID=$!

sleep 3
if which xdg-open > /dev/null 2>&1; then
  xdg-open http://localhost:5173
elif which open > /dev/null 2>&1; then
  open http://localhost:5173
fi

wait  
