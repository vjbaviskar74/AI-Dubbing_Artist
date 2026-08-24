import os
import shutil
from pathlib import Path
from ..utils.subprocess_utils import run_command
from ..config import settings

class SourceSeparation:
    def separate(self, audio_path: str, run_id: str) -> dict:
        """Separates vocals and background using configured engine."""
        engine = settings.audio.separation.engine.lower()
        output_dir = settings.default.paths.absolute_path(settings.base_dir, "runs_dir") / run_id / "separated"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        vocals_path = output_dir / "vocals.wav"
        instrumental_path = output_dir / "instrumental.wav"
        
        if engine == "demucs":
            self._run_demucs(audio_path, output_dir)
            # Demucs outputs to htdemucs/<filename>/...
            # We need to move them to vocals.wav and instrumental.wav
            filename = Path(audio_path).stem
            demucs_out_dir = output_dir / "htdemucs" / filename
            
            src_vocals = demucs_out_dir / "vocals.wav"
            src_bass = demucs_out_dir / "bass.wav"
            src_drums = demucs_out_dir / "drums.wav"
            src_other = demucs_out_dir / "other.wav"
            
            if src_vocals.exists():
                shutil.copy(src_vocals, vocals_path)
            
            # Combine bass, drums, other into instrumental using ffmpeg
            if src_bass.exists() and src_drums.exists() and src_other.exists():
                cmd = [
                    "ffmpeg", "-y",
                    "-i", str(src_bass),
                    "-i", str(src_drums),
                    "-i", str(src_other),
                    "-filter_complex", "amix=inputs=3:duration=longest",
                    str(instrumental_path)
                ]
                run_command(cmd)
        else:
            raise NotImplementedError(f"Separation engine {engine} is not implemented.")
            
        if not vocals_path.exists() or not instrumental_path.exists():
            raise RuntimeError("Source separation failed to produce expected output files.")
            
        return {
            "vocals_audio": str(vocals_path),
            "background_audio": str(instrumental_path)
        }
        
    def _run_demucs(self, audio_path: str, output_dir: Path):
        cmd = [
            "demucs",
            "--out", str(output_dir),
            audio_path
        ]
        run_command(cmd)
