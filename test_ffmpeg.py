import shutil
import sys
import os

ffmpeg_path = shutil.which("ffmpeg")
if ffmpeg_path:
    print(f"\nSUCCESS! Python can see FFmpeg at: {ffmpeg_path}\n")
    print("If you are still getting errors in Streamlit, the error is NOT about missing FFmpeg.")
else:
    print("\nFAILURE! Python CANNOT see FFmpeg.")
    print("This means the terminal window you are currently using has a 'stale' PATH variable.")
    print("You MUST restart your terminal application completely (e.g. restart VS Code).")
    print(f"Current PATH: {os.environ.get('PATH')[:200]}...\n")
