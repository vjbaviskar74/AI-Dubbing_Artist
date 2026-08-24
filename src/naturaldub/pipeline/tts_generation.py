import json
from pathlib import Path
from ..schemas.translation import TranslationScript
from ..providers.sarvam_tts import SarvamTTSProvider
from ..config import settings

class TTSGeneration:
    def __init__(self):
        self.provider = SarvamTTSProvider()
        
    def generate(self, script: TranslationScript, run_id: str) -> dict:
        output_dir = settings.default.paths.absolute_path(settings.base_dir, "runs_dir") / run_id / "generated" / "base"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        generated_files = {}
        for seg in script.segments:
            if not seg.is_approved:
                # In full pipeline, we might skip or fail if not approved. For now, generate anyway.
                pass
                
            out_path = output_dir / f"turn_{seg.turn_id:03d}.wav"
            
            if out_path.exists():
                generated_files[seg.turn_id] = str(out_path)
                continue
                
            # Default speaker for sarvam (aditya or amartya, etc.)
            speaker = settings.models.tts.default_speaker or "aditya"
            
            try:
                self.provider.synthesize(seg.translated_text, speaker, str(out_path))
                generated_files[seg.turn_id] = str(out_path)
            except Exception as e:
                print(f"TTS failed for turn {seg.turn_id}: {e}")
                
        return generated_files
