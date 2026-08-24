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

import subprocess
import sys

if __name__ == "__main__":
    print("Starting Streamlit frontend...")
    ui_path = os.path.join(os.path.dirname(__file__), "ui", "streamlit_app.py")
    subprocess.run([sys.executable, "-m", "streamlit", "run", ui_path])
