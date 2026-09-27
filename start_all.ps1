Write-Host "Starting getHire Backend API (FastAPI)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python -m uvicorn server:app --host 127.0.0.1 --port 8000 --reload"

Write-Host "Starting getHire Frontend UI (React + Vite)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location frontend; npm.cmd run dev"

Write-Host "Opening browser at http://localhost:5173 ..." -ForegroundColor Green
Start-Sleep -Seconds 3
Start-Process "http://localhost:5173"
