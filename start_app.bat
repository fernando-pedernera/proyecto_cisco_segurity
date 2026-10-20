@echo off
title Cisco Security AI Enablement Suite
echo ========================================================
echo   Iniciando Cisco Security AI Enablement Suite (FastAPI)
echo   Puerto: http://localhost:8020
echo ========================================================
start "" http://localhost:8020
python -m uvicorn app.main:app --host 127.0.0.1 --port 8020 --reload
pause
