from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
from app.api.routes_jobs import get_job_state, save_job_state

router = APIRouter()

class SegmentUpdate(BaseModel):
    segment_id: str
    original_text: str = None
    translated_text: str = None
    adapted_text: str = None
    speaker: str = None

@router.post("/{job_id}/transcript")
def update_transcript(job_id: str, updates: List[SegmentUpdate]):
    state = get_job_state(job_id)
    for update in updates:
        for seg in state['segments']:
            # Depending on how segment_id is stored
            if str(seg.get('segment_id', '')) == update.segment_id or str(seg.get('id', '')) == update.segment_id:
                if update.original_text:
                    seg['text'] = update.original_text
                if update.speaker:
                    seg['speaker'] = update.speaker
    save_job_state(job_id, state)
    return {"status": "success"}

@router.post("/{job_id}/translation")
def update_translation(job_id: str, updates: List[SegmentUpdate]):
    state = get_job_state(job_id)
    for update in updates:
        for trans in state['translations']:
            if str(trans.get('segment_id', '')) == update.segment_id:
                if update.translated_text:
                    trans['translated_text'] = update.translated_text
                if update.adapted_text:
                    trans['adapted_text'] = update.adapted_text
    save_job_state(job_id, state)
    return {"status": "success"}
