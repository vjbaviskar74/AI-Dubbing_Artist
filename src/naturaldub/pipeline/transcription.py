import json
from pathlib import Path
from ..schemas.transcript import Transcript, Segment, Word
from ..providers.groq_asr import GroqASRProvider
from ..config import settings

class Transcription:
    def __init__(self):
        self.provider = GroqASRProvider(model=settings.models.asr.model)
        
    def transcribe(self, audio_path: str, run_id: str) -> Transcript:
        output_dir = settings.default.paths.absolute_path(settings.base_dir, "runs_dir") / run_id / "transcripts"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_path = output_dir / "transcript.json"
        
        # In a real run, check cache
        if output_path.exists():
            try:
                with open(output_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return Transcript(**data)
            except Exception:
                pass # Re-run if cache is invalid
        
        raw_result = self.provider.transcribe(audio_path)
        
        transcript = Transcript(
            run_id=run_id,
            language=raw_result["language"],
            duration=raw_result["duration"],
            segments=[Segment(**s) for s in raw_result["segments"]]
        )
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(transcript.model_dump(), f, indent=2, ensure_ascii=False)
            
        return transcript
