@echo off
title NATURALDUB-AI Backend Server (Python 3.12)
echo ========================================================
echo Starting NATURALDUB-AI FastAPI Backend in Python 3.12...
echo ========================================================
"C:\Users\VEDANT\AppData\Local\Programs\Python\Python312\python.exe" -m uvicorn app.main:app --reload --port 8000
pause
