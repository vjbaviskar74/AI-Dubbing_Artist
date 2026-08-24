from typing import TypedDict, Optional, List, Dict

class NaturalDubState(TypedDict, total=False):
    run_id: str
    input_video: str
    media_metadata: dict
    original_audio: str
    vocals_audio: str
    background_audio: str
    transcript: dict
    diarization: dict
    speaker_turns: list
    scene_context: dict
    translations: list
    approved_script: list
    speaker_references: dict
    base_audio_files: dict
    converted_audio_files: dict
    aligned_audio_files: dict
    final_dialogue_track: str
    final_mix: str
    output_video: str
    qa_report: dict
    current_phase: str
    completed_phases: list
    warnings: list
    errors: list
