from typing import Dict, Any
from ..schemas.state import NaturalDubState
from ..pipeline.ingestion import VideoIngestion
from ..pipeline.audio_extraction import AudioExtraction
from ..pipeline.source_separation import SourceSeparation
from ..pipeline.transcription import Transcription
from ..pipeline.diarization import SpeakerDiarization
from ..pipeline.turn_reconstruction import TurnReconstruction
from ..pipeline.reference_extraction import ReferenceExtraction

def media_intelligence_node(state: NaturalDubState) -> Dict[str, Any]:
    run_id = state["run_id"]
    video_path = state["input_video"]
    
    # Init tools
    ingestion = VideoIngestion()
    extractor = AudioExtraction()
    separator = SourceSeparation()
    transcriber = Transcription()
    diarizer = SpeakerDiarization()
    reconstructor = TurnReconstruction()
    ref_extractor = ReferenceExtraction()
    
    # 1. Ingestion
    metadata = ingestion.validate_and_inspect(video_path)
    
    # 2. Extract Audio
    original_audio = extractor.extract_audio(video_path, run_id)
    
    # 3. Separate Audio
    separated = separator.separate(original_audio, run_id)
    
    # 4. Transcription
    transcript = transcriber.transcribe(separated["vocals_audio"], run_id)
    
    # 5. Diarization
    diarization = diarizer.diarize(separated["vocals_audio"], run_id)
    
    # 6. Reconstruct Turns
    turns = reconstructor.reconstruct(transcript, diarization, run_id)
    
    # 7. Extract references
    references = ref_extractor.extract(separated["vocals_audio"], diarization, run_id)
    
    return {
        "media_metadata": metadata.model_dump(),
        "original_audio": original_audio,
        "vocals_audio": separated["vocals_audio"],
        "background_audio": separated["background_audio"],
        "transcript": transcript.model_dump(),
        "diarization": diarization.model_dump(),
        "speaker_turns": [t.model_dump() for t in turns],
        "speaker_references": references,
        "current_phase": "media_intelligence",
        "completed_phases": state.get("completed_phases", []) + ["media_intelligence"]
    }
