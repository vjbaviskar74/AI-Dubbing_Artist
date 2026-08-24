from fastapi import APIRouter
from fastapi.responses import FileResponse
from app.api.routes_jobs import get_job_state
import os

router = APIRouter()

@router.get("/{job_id}/download/{artifact_type}")
def download_artifact(job_id: str, artifact_type: str):
    state = get_job_state(job_id)
    
    path_map = {
        "video": state.get('final_video_path'),
        "audio": state.get('mixed_audio_path'),
        "report": state.get('evaluation_report_path')
    }
    
    file_path = path_map.get(artifact_type)
    if not file_path or not os.path.exists(file_path):
        return {"error": "Artifact not found"}
        
    return FileResponse(file_path, filename=os.path.basename(file_path))
