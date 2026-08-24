from pathlib import Path
from ..utils.subprocess_utils import run_command
from ..config import settings

class Multiplexing:
    def multiplex(self, video_path: str, final_audio_path: str, run_id: str) -> str:
        output_dir = settings.default.paths.absolute_path(settings.base_dir, "runs_dir") / run_id / "output"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_path = output_dir / f"NaturalDub_{run_id}_Hindi_Dubbed.mp4"
        
        cmd = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-i", final_audio_path,
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "192k",
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-shortest",
            str(output_path)
        ]
        
        run_command(cmd)
        
        if not output_path.exists():
            raise RuntimeError("Multiplexing failed to create output video.")
            
        return str(output_path)
