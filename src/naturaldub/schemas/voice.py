from pydantic import BaseModel

class VoiceReference(BaseModel):
    speaker_id: str
    reference_audio_path: str
    duration: float
