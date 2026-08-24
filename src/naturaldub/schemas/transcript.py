from typing import List, Optional
from pydantic import BaseModel

class Word(BaseModel):
    word: str
    start: float
    end: float
    confidence: Optional[float] = None

class Segment(BaseModel):
    segment_id: int
    start: float
    end: float
    text: str
    words: List[Word] = []

class Transcript(BaseModel):
    run_id: str
    language: str
    duration: float
    segments: List[Segment]
