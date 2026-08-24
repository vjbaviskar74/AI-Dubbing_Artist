import shutil
import subprocess
from app.services.model_registry import ModelRegistry

def lip_sync_video(video_path: str, audio_path: str, output_path: str) -> dict:
    print("Muxing new dubbed audio into original video...")
    try:
        command = [
            "ffmpeg", "-y", "-i", video_path, "-i", audio_path,
            "-c:v", "copy", "-c:a", "aac", "-map", "0:v:0", "-map", "1:a:0",
            output_path
        ]
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return {"success": True, "output_path": output_path, "message": "Successfully replaced audio track"}
    except Exception as e:
        error_msg = f"FFmpeg muxing failed: {str(e)}"
        print(error_msg)
        raise RuntimeError(error_msg)
