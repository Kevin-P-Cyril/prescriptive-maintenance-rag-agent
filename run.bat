@echo off
title PMA - Run

echo ==========================================================
echo  Prescriptive Maintenance Assistant - Launch
echo ==========================================================
echo.

REM --- Make sure Ollama is running (free, local LLM server) ---
where ollama >nul 2>nul
if not errorlevel 1 (
    echo Starting Ollama server in the background (if not already running)...
    start "Ollama Server" /min cmd /c "ollama serve"
    timeout /t 2 >nul
) else (
    echo [WARNING] Ollama not found on PATH - the assistant will not be able to generate
    echo           answers until Ollama is installed and running. See README.md.
)

echo Starting backend (FastAPI) on http://localhost:8000 ...
start "PMA Backend" cmd /k "cd backend && call .venv\Scripts\activate.bat && uvicorn app.main:app --reload --port 8000"

timeout /t 3 >nul

echo Starting frontend (React/Vite) on http://localhost:5173 ...
start "PMA Frontend" cmd /k "cd frontend && npm run dev"

timeout /t 3 >nul
echo.
echo ==========================================================
echo  Both services are starting in separate windows:
echo    Backend API + docs : http://localhost:8000/docs
echo    Frontend UI        : http://localhost:5173
echo  Close those windows to stop the services.
echo ==========================================================

start http://localhost:5173
