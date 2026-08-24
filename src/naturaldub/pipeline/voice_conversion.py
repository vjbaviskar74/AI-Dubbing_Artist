from pathlib import Path
from ..schemas.translation import TranslationScript
from ..providers.seed_vc import SeedVCProvider
from ..config import settings

class VoiceConversion:
    def __init__(self):
        self.provider = SeedVCProvider()
        
    def convert(self, script: TranslationScript, base_audios: dict, references: dict, run_id: str) -> dict:
        output_dir = settings.default.paths.absolute_path(settings.base_dir, "runs_dir") / run_id / "converted"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        converted_files = {}
        for seg in script.segments:
            if seg.turn_id not in base_audios:
                continue
                
            base_audio_path = base_audios[seg.turn_id]
            speaker_id = seg.speaker_id
            
            ref_info = references.get(speaker_id)
            if not ref_info:
                # No reference, fallback to base audio
                converted_files[seg.turn_id] = base_audio_path
                continue
                
            ref_audio_path = ref_info["reference_audio_path"]
            out_path = output_dir / f"turn_{seg.turn_id:03d}.wav"
            
            if out_path.exists():
                converted_files[seg.turn_id] = str(out_path)
                continue
                
            try:
                self.provider.convert(base_audio_path, ref_audio_path, str(out_path))
                converted_files[seg.turn_id] = str(out_path)
            except Exception as e:
                print(f"VC failed for turn {seg.turn_id}, falling back. Error: {e}")
                converted_files[seg.turn_id] = base_audio_path
                
        return converted_files
