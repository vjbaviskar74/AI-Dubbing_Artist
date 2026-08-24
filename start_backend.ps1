Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "Starting NATURALDUB-AI FastAPI Backend in Python 3.12..." -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
& "C:\Users\VEDANT\AppData\Local\Programs\Python\Python312\python.exe" -m uvicorn app.main:app --reload --port 8000
