from typing import List
from pydantic import BaseModel

class TranslatedSegment(BaseModel):
    turn_id: int
    speaker_id: str
    start: float
    end: float
    source_text: str
    translated_text: str
    meaning_summary: str = ""
    emotion: str = ""
    delivery: str = ""
    target_duration: float
    estimated_duration: float
    timing_status: str = "within_limit"
    protected_terms_used: List[str] = []
    is_approved: bool = False

class TranslationScript(BaseModel):
    segments: List[TranslatedSegment]
