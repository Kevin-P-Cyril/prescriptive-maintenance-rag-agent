#!/usr/bin/env bash
set -e

echo "=========================================================="
echo " Prescriptive Maintenance Assistant - Setup"
echo "=========================================================="
echo "This installs everything locally and FREE of cost:"
echo "  - Python virtual environment + backend dependencies"
echo "  - Node.js frontend dependencies"
echo "  - Ollama (local LLM) model pull"
echo "  - Sample manual ingestion into ChromaDB"
echo "=========================================================="

command -v python3 >/dev/null 2>&1 || { echo "[ERROR] python3 not found. Install Python 3.10+."; exit 1; }
echo "[OK] Python found."

command -v node >/dev/null 2>&1 || { echo "[ERROR] node not found. Install Node.js LTS."; exit 1; }
echo "[OK] Node.js found."

if ! command -v ollama >/dev/null 2>&1; then
  echo "[WARNING] Ollama not found. Install it from https://ollama.com/download to run the LLM for free."
else
  echo "[OK] Ollama found."
fi

echo
echo "---------- Backend setup ----------"
cd backend
[ -d ".venv" ] || python3 -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate
pip install --upgrade pip >/dev/null
pip install -r requirements.txt

[ -f ".env" ] || cp .env.example .env

if [ ! -f "data/manuals/cnc_204_maintenance_manual.pdf" ]; then
  python scripts/generate_sample_manual.py
fi

if command -v ollama >/dev/null 2>&1; then
  echo "Pulling local LLM model (llama3.2) via Ollama - this is FREE and runs offline..."
  ollama pull llama3.2
fi

echo "Ingesting sample manual into the local ChromaDB vector store..."
python ingest.py
cd ..

echo
echo "---------- Frontend setup ----------"
cd frontend
npm install
cd ..

echo
echo "=========================================================="
echo " Setup complete! Run ./run.sh to launch the application."
echo "=========================================================="
