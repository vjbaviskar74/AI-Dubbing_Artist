from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional
import uuid
import os
import json

from app.database.connection import get_db
from app.database import crud
from app.graph.dubbing_graph import graph
from app.config import settings
from app.services.artifact_service import ArtifactService

router = APIRouter()

# Simple dict to hold in-memory state for MVP (normally you'd use a robust state store like redis)
# Key: job_id, Value: DubbingState
JOB_STATES = {}

def get_job_state(job_id: str):
    if job_id not in JOB_STATES:
        # Try to load from artifacts
        state_path = f"artifacts/reports/{job_id}_state.json"
        state = ArtifactService.load_json(state_path)
        if not state:
            raise HTTPException(status_code=404, detail="Job state not found")
        JOB_STATES[job_id] = state
    return JOB_STATES[job_id]

def save_job_state(job_id: str, state: dict):
    JOB_STATES[job_id] = state
    ArtifactService.save_json(f"artifacts/reports/{job_id}_state.json", state)

@router.post("/")
async def create_job(
    file: UploadFile = File(...),
    source_language: str = Form(...),
    target_language: str = Form(...),
    consent_verified: bool = Form(...),
    script_file: Optional[UploadFile] = File(None),
    script_text: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    job_id = str(uuid.uuid4())
    upload_path = os.path.join(settings.DATA_DIR, "uploads", f"{job_id}_{file.filename}")
    
    with open(upload_path, "wb") as buffer:
        buffer.write(await file.read())
        
    script_content = ""
    if script_file and script_file.filename:
        try:
            content_bytes = await script_file.read()
            script_content = content_bytes.decode("utf-8", errors="ignore")
        except Exception as e:
            print(f"Failed to read uploaded script file: {e}")
    elif script_text:
        script_content = script_text
        
    crud.create_job(db, job_id, upload_path, source_language, target_language, consent_verified)
    
    initial_state = {
        "job_id": job_id,
        "input_video_path": upload_path,
        "source_language": source_language,
        "target_language": target_language,
        "consent_verified": consent_verified,
        "script_text": script_content,
        "studio_mode": bool(script_content),
        "audio_paths": {},
        "segments": [],
        "speaker_map": {},
        "genre": "",
        "scene_mood": "",
        "humor_type": "",
        "dialogue_intent": "",
        "cultural_context": {},
        "translations": [],
        "voice_profiles": {},
        "generated_audio_segments": [],
        "timeline_path": "",
        "mixed_audio_path": "",
        "final_video_path": "",
        "evaluation_report_path": "",
        "errors": [],
        "warnings": [],
        "mode": "advanced" if settings.ENABLE_ADVANCED_MODELS else "mvp"
    }
    save_job_state(job_id, initial_state)
    
    return {"job_id": job_id, "status": "created"}

@router.post("/{job_id}/process-media")
def process_media(job_id: str, db: Session = Depends(get_db)):
    state = get_job_state(job_id)
    # Using the media node directly for step-by-step
    from app.agents.media_agent import run_media_agent
    new_state = run_media_agent(state)
    save_job_state(job_id, new_state)
    crud.update_job_status(db, job_id, "media_processed")
    return {"status": "success", "segments": new_state['segments']}

@router.post("/{job_id}/translate")
def translate(job_id: str, genre: str = "Drama", db: Session = Depends(get_db)):
    state = get_job_state(job_id)
    state['genre'] = genre
    from app.agents.translation_agent import run_translation_agent
    new_state = run_translation_agent(state)
    save_job_state(job_id, new_state)
    crud.update_job_status(db, job_id, "translated")
    return {"status": "success", "translations": new_state['translations']}

@router.post("/{job_id}/generate-voice")
def generate_voice(job_id: str, db: Session = Depends(get_db)):
    state = get_job_state(job_id)
    from app.agents.voice_emotion_agent import run_voice_emotion_agent
    new_state = run_voice_emotion_agent(state)
    save_job_state(job_id, new_state)
    crud.update_job_status(db, job_id, "voice_generated")
    return {"status": "success", "audio_segments": new_state['generated_audio_segments']}

@router.post("/{job_id}/sync-mix-export")
def sync_mix_export(job_id: str, db: Session = Depends(get_db)):
    state = get_job_state(job_id)
    from app.agents.sync_qa_agent import run_sync_qa_agent
    new_state = run_sync_qa_agent(state)
    save_job_state(job_id, new_state)
    crud.update_job_status(db, job_id, "completed")
    return {"status": "success", "final_video": new_state['final_video_path'], "report": new_state['evaluation_report_path']}

@router.post("/{job_id}/transcript")
def update_transcript(job_id: str, segments: str = Form(...), db: Session = Depends(get_db)):
    state = get_job_state(job_id)
    state['segments'] = json.loads(segments)
    save_job_state(job_id, state)
    return {"status": "success"}

@router.post("/{job_id}/translations-update")
def update_translations(job_id: str, translations: str = Form(...), db: Session = Depends(get_db)):
    state = get_job_state(job_id)
    state['translations'] = json.loads(translations)
    save_job_state(job_id, state)
    return {"status": "success"}

@router.get("/{job_id}")
def get_job_status(job_id: str, db: Session = Depends(get_db)):
    job = crud.get_job(db, job_id)
    state = JOB_STATES.get(job_id, {})
    return {"db_job": job, "state": state}
