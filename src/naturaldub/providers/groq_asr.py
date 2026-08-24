import os
import json
from groq import Groq
from .base import BaseASRProvider

class GroqASRProvider(BaseASRProvider):
    def __init__(self, model: str = "whisper-large-v3"):
        self.model = model
        self.client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    def transcribe(self, audio_path: str) -> dict:
        with open(audio_path, "rb") as file:
            translation = self.client.audio.transcriptions.create(
                file=(audio_path, file.read()),
                model=self.model,
                response_format="verbose_json",
                language="en"
            )
        
        # Parse into standard format
        segments = []
        for i, segment in enumerate(translation.segments):
            words = []
            if hasattr(segment, 'words') and segment.words:
                for w in segment.words:
                    words.append({
                        "word": w.word,
                        "start": w.start,
                        "end": w.end
                    })
            segments.append({
                "segment_id": i,
                "start": segment.start,
                "end": segment.end,
                "text": segment.text.strip(),
                "words": words
            })
            
        return {
            "language": translation.language if hasattr(translation, 'language') else 'en',
            "duration": translation.duration if hasattr(translation, 'duration') else 0.0,
            "segments": segments
        }
