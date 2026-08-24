from typing import Dict, Any
from ..schemas.state import NaturalDubState
from ..schemas.diarization import SpeakerTurn
from ..pipeline.context_analysis import ContextAnalysis
from ..pipeline.transcreation import Transcreation

def transcreation_director_node(state: NaturalDubState) -> Dict[str, Any]:
    run_id = state["run_id"]
    turns_data = state["speaker_turns"]
    
    turns = [SpeakerTurn(**t) for t in turns_data]
    
    # Init tools
    analyzer = ContextAnalysis()
    translator = Transcreation()
    
    # 1. Context Analysis
    context = analyzer.analyze(turns, run_id)
    
    # 2. Transcreation
    script = translator.translate(turns, context, run_id)
    
    return {
        "scene_context": context.model_dump(),
        "translations": script.model_dump()["segments"],
        "current_phase": "transcreation_director",
        "completed_phases": state.get("completed_phases", []) + ["transcreation_director"]
    }
