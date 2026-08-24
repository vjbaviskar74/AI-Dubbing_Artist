from pydantic import BaseModel

class AlignmentResult(BaseModel):
    turn_id: int
    target_duration: float
    generated_duration: float
    ratio: float
    method: str
    final_duration: float
