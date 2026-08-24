import sys
import os

# Self-healing: Force script to use Python 3.12 if launched with Python 3.11 by mistake
if sys.version_info < (3, 12):
    print("⚠️ Detected older Python version! Auto-redirecting to Python 3.12 environment...")
    python312_path = r"C:\Users\VEDANT\AppData\Local\Programs\Python\Python312\python.exe"
    if os.path.exists(python312_path):
        os.execl(python312_path, python312_path, *sys.argv)
    else:
        print("❌ Could not find Python 3.12 path!")

import uvicorn
from app.main import app
import os

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    print(f"Starting FastAPI backend on {host}:{port}")
    uvicorn.run("app.main:app", host=host, port=port, reload=True)
