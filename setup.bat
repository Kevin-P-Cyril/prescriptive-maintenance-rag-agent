@echo off
setlocal enabledelayedexpansion
title PMA - Setup

echo ==========================================================
echo  Prescriptive Maintenance Assistant - Setup
echo ==========================================================
echo This installs everything locally and FREE of cost:
echo   - Python virtual environment + backend dependencies
echo   - Node.js frontend dependencies
echo   - Ollama (local LLM) model pull
echo   - Sample manual ingestion into ChromaDB
echo ==========================================================
echo.

REM --- Check Python ---
where python >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Python was not found on PATH. Install Python 3.10+ from https://www.python.org/downloads/
    echo         Make sure to check "Add python.exe to PATH" during installation.
    pause
    exit /b 1
)
echo [OK] Python found.

REM --- Check Node.js ---
where node >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Node.js was not found on PATH. Install it from https://nodejs.org/ (LTS version).
    pause
    exit /b 1
)
echo [OK] Node.js found.

REM --- Check Ollama ---
where ollama >nul 2>nul
if errorlevel 1 (
    echo [WARNING] Ollama was not found on PATH.
    echo           This project uses Ollama to run the LLM locally for FREE, avoiding paid APIs.
    echo           Please install it from https://ollama.com/download , then re-run this script.
    echo           You can continue setup now and pull the model later.
) else (
    echo [OK] Ollama found.
)

echo.
echo ---------- Backend setup ----------
cd backend

if not exist ".venv" (
    echo Creating Python virtual environment...
    python -m venv .venv
)

call .venv\Scripts\activate.bat

echo Upgrading pip...
python -m pip install --upgrade pip >nul

echo Installing backend dependencies (this can take several minutes on first run)...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Backend dependency installation failed. See the log above.
    pause
    exit /b 1
)

if not exist ".env" (
    echo Creating .env from .env.example...
    copy .env.example .env >nul
)

echo.
echo Generating sample maintenance manual (if not already present)...
if not exist "data\manuals\cnc_204_maintenance_manual.pdf" (
    python scripts\generate_sample_manual.py
)

where ollama >nul 2>nul
if not errorlevel 1 (
    echo.
    echo Pulling local LLM model (llama3.2) via Ollama - this is FREE and runs offline...
    ollama pull llama3.2
)

echo.
echo Ingesting sample manual into the local ChromaDB vector store...
python ingest.py

cd ..

echo.
echo ---------- Frontend setup ----------
cd frontend
echo Installing frontend dependencies...
call npm install
if errorlevel 1 (
    echo [ERROR] Frontend dependency installation failed. See the log above.
    pause
    exit /b 1
)
cd ..

echo.
echo ==========================================================
echo  Setup complete!
echo  Run start.bat / run.bat to launch the application.
echo ==========================================================
pause
