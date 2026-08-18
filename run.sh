#!/usr/bin/env bash
set -e

echo "=========================================================="
echo " Prescriptive Maintenance Assistant - Launch"
echo "=========================================================="

if command -v ollama >/dev/null 2>&1; then
  if ! curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
    echo "Starting Ollama server in the background..."
    nohup ollama serve > /tmp/ollama.log 2>&1 &
    sleep 2
  fi
else
  echo "[WARNING] Ollama not found - answers will not generate until it's installed."
fi

echo "Starting backend (FastAPI) on http://localhost:8000 ..."
(
  cd backend
  # shellcheck disable=SC1091
  source .venv/bin/activate
  uvicorn app.main:app --reload --port 8000 &
)

sleep 2

echo "Starting frontend (React/Vite) on http://localhost:5173 ..."
(
  cd frontend
  npm run dev &
)

sleep 2
echo
echo "=========================================================="
echo " Backend API + docs : http://localhost:8000/docs"
echo " Frontend UI        : http://localhost:5173"
echo " Press Ctrl+C to stop watching this script (services keep running in background)."
echo "=========================================================="
wait
