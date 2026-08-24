import json
import mimetypes
from pathlib import Path
from ..utils.subprocess_utils import run_command
from ..schemas.media import MediaMetadata

class VideoIngestion:
    def __init__(self):
        self.supported_extensions = {".mp4", ".mov", ".mkv", ".webm"}
    
    def validate_and_inspect(self, video_path: str) -> MediaMetadata:
        path = Path(video_path)
        if not path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        ext = path.suffix.lower()
        if ext not in self.supported_extensions:
            raise ValueError(f"Unsupported extension: {ext}. Supported: {self.supported_extensions}")
        
        # Use ffprobe to get media info
        cmd = [
            "ffprobe",
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            video_path
        ]
        
        result = run_command(cmd)
        info = json.loads(result.stdout)
        
        duration = float(info.get("format", {}).get("duration", 0.0))
        if duration <= 0:
            raise ValueError("Invalid media duration. File may be corrupt.")
            
        video_stream = next((s for s in info.get("streams", []) if s["codec_type"] == "video"), None)
        audio_stream = next((s for s in info.get("streams", []) if s["codec_type"] == "audio"), None)
        
        if not audio_stream:
            raise ValueError("No audio stream found in the media file.")
            
        video_codec = video_stream["codec_name"] if video_stream else None
        
        # Get frame rate safely
        frame_rate = None
        if video_stream and "r_frame_rate" in video_stream:
            num, den = video_stream["r_frame_rate"].split('/')
            if int(den) != 0:
                frame_rate = int(num) / int(den)
                
        audio_codec = audio_stream.get("codec_name")
        channels = int(audio_stream.get("channels", 2))
        sample_rate = int(audio_stream.get("sample_rate", 44100))
        
        return MediaMetadata(
            filename=path.name,
            duration=duration,
            video_codec=video_codec,
            audio_codec=audio_codec,
            frame_rate=frame_rate,
            channels=channels,
            sample_rate=sample_rate
        )
