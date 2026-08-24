from typing import List, Optional
from pydantic import BaseModel

class SpeakerTurn(BaseModel):
    turn_id: int
    speaker_id: str
    character_name: Optional[str] = None
    start: float
    end: float
    duration: float
    source_text: str
    pause_before: float = 0.0
    pause_after: float = 0.0

class Diarization(BaseModel):
    turns: List[SpeakerTurn]
