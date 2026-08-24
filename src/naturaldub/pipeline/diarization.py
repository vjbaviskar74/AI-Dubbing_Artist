import json
from pathlib import Path
from ..schemas.diarization import Diarization, SpeakerTurn
from ..providers.pyannote_diarization import PyannoteDiarizationProvider
from ..config import settings

class SpeakerDiarization:
    def __init__(self):
        # Allow disabling pyannote if no token provided during dev mock
        self.provider = None
        try:
            self.provider = PyannoteDiarizationProvider()
        except ValueError:
            print("Warning: Pyannote auth token missing. Diarization will fail if called without mock.")
            
    def diarize(self, audio_path: str, run_id: str) -> Diarization:
        output_dir = settings.default.paths.absolute_path(settings.base_dir, "runs_dir") / run_id / "diarization"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_path = output_dir / "diarization.json"
        
        if output_path.exists():
            try:
                with open(output_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return Diarization(**data)
            except Exception:
                pass
                
        if not self.provider:
            raise RuntimeError("Diarization provider not initialized (check HF_AUTH_TOKEN).")
            
        raw_result = self.provider.diarize(audio_path)
        
        diarization = Diarization(
            turns=[SpeakerTurn(**t, source_text="") for t in raw_result["turns"]]
        )
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(diarization.model_dump(), f, indent=2, ensure_ascii=False)
            
        return diarization
