from pydub import AudioSegment
from pathlib import Path
from ..config import settings
from ..utils.subprocess_utils import run_command

class Mixing:
    def mix(self, dialogue_track: str, background_track: str, run_id: str) -> str:
        output_dir = settings.default.paths.absolute_path(settings.base_dir, "runs_dir") / run_id / "mixed"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        final_mix_path = output_dir / "final_mix.wav"
        
        # We can use FFmpeg for mixing with a slight ducking effect on background
        # For simplicity, we just amix them here and prevent clipping
        cmd = [
            "ffmpeg", "-y",
            "-i", dialogue_track,
            "-i", background_track,
            "-filter_complex", "[0:a]volume=1.0[a0];[1:a]volume=0.8[a1];[a0][a1]amix=inputs=2:duration=longest[out]",
            "-map", "[out]",
            "-ac", str(settings.audio.audio.export_channels),
            "-ar", str(settings.audio.audio.export_sample_rate),
            str(final_mix_path)
        ]
        
        run_command(cmd)
        return str(final_mix_path)
