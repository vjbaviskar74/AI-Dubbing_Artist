from pathlib import Path
from ..utils.subprocess_utils import run_command
from ..config import settings

class AudioExtraction:
    def extract_audio(self, video_path: str, run_id: str) -> str:
        """Extracts high quality original audio from video."""
        output_dir = settings.default.paths.absolute_path(settings.base_dir, "runs_dir") / run_id / "extracted"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_path = output_dir / "original_audio.wav"
        
        # We extract as a high-quality wav, preserving sample rate if possible, 
        # or forcing to the config sample_rate if we want consistency early.
        # The prompt says: "Avoid destructive normalization at the beginning."
        cmd = [
            "ffmpeg", "-y", 
            "-i", video_path,
            "-vn", # No video
            "-acodec", "pcm_s16le",
            str(output_path)
        ]
        
        run_command(cmd)
        
        if not output_path.exists():
            raise RuntimeError(f"Audio extraction failed. File not found at {output_path}")
            
        return str(output_path)
