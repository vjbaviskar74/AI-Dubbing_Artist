import subprocess
import os

def extract_audio(video_path: str, output_path: str) -> dict:
    try:
        # Use FFmpeg command if available
        command = [
            "ffmpeg", "-y", "-i", video_path, 
            "-q:a", "0", "-map", "a", output_path
        ]
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Calculate duration roughly
        # (In a real app, use ffprobe to get exact duration)
        
        return {
            "success": True,
            "output_path": output_path,
            "duration": 30.0, # Placeholder
            "message": "Audio extracted"
        }
    except Exception as e:
        error_msg = f"FFmpeg error: {str(e)}"
        print(error_msg)
        # Raise the error so the higher level agent knows it failed
        raise RuntimeError(error_msg)
