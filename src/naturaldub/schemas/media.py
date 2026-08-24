from typing import Optional
from pydantic import BaseModel

class MediaMetadata(BaseModel):
    filename: str
    duration: float
    video_codec: Optional[str] = None
    audio_codec: Optional[str] = None
    frame_rate: Optional[float] = None
    channels: int
    sample_rate: int
    original_audio_path: Optional[str] = None
    vocals_audio_path: Optional[str] = None
    background_audio_path: Optional[str] = None
