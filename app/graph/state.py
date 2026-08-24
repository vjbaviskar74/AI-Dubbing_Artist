from typing import TypedDict, List, Dict, Any

class DubbingState(TypedDict):
    job_id: str
    input_video_path: str
    source_language: str
    target_language: str
    consent_verified: bool
    audio_paths: Dict[str, str]
    segments: List[Dict[str, Any]]
    speaker_map: Dict[str, str]
    genre: str
    scene_mood: str
    humor_type: str
    dialogue_intent: str
    cultural_context: Dict[str, Any]
    translations: List[Dict[str, Any]]
    voice_profiles: Dict[str, Any]
    generated_audio_segments: List[Dict[str, Any]]
    timeline_path: str
    mixed_audio_path: str
    final_video_path: str
    evaluation_report_path: str
    errors: List[str]
    warnings: List[str]
    mode: str
