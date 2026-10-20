# PowerShell Launcher for Cisco Security AI Enablement Suite
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  Iniciando Cisco Security AI Enablement Suite (FastAPI)  " -ForegroundColor White
Write-Host "  URL: http://localhost:8020                              " -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Cyan

Start-Process "http://localhost:8020"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8020 --reload
