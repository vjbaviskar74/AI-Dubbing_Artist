import os
import torch
from pyannote.audio import Pipeline
from .base import BaseDiarizationProvider

class PyannoteDiarizationProvider(BaseDiarizationProvider):
    def __init__(self, use_auth_token: str = None):
        auth_token = use_auth_token or os.environ.get("HF_AUTH_TOKEN")
        if not auth_token:
            raise ValueError("Hugging Face auth token required for Pyannote")
            
        self.pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            use_auth_token=auth_token
        )
        
        if torch.cuda.is_available():
            self.pipeline.to(torch.device("cuda"))

    def diarize(self, audio_path: str) -> dict:
        diarization = self.pipeline(audio_path)
        
        turns = []
        for i, (turn, _, speaker) in enumerate(diarization.itertracks(yield_label=True)):
            turns.append({
                "turn_id": i,
                "speaker_id": speaker,
                "start": turn.start,
                "end": turn.end,
                "duration": turn.end - turn.start
            })
            
        return {"turns": turns}
