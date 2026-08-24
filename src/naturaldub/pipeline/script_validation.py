from typing import List
from ..schemas.translation import TranslationScript
from ..schemas.diarization import SpeakerTurn

class ScriptValidation:
    def validate(self, script: TranslationScript, original_turns: List[SpeakerTurn]) -> bool:
        """
        Validates the generated script against original turns.
        Checks for missing turns, duplicate turns, and unknown turn IDs.
        """
        original_ids = {t.turn_id for t in original_turns}
        script_ids = set()
        
        for seg in script.segments:
            if seg.turn_id not in original_ids:
                raise ValueError(f"Unknown turn_id in script: {seg.turn_id}")
            if seg.turn_id in script_ids:
                raise ValueError(f"Duplicate turn_id in script: {seg.turn_id}")
            script_ids.add(seg.turn_id)
            
        missing = original_ids - script_ids
        if missing:
            raise ValueError(f"Missing turn_ids in script: {missing}")
            
        # Basic duration limit check
        for seg in script.segments:
            orig = next(t for t in original_turns if t.turn_id == seg.turn_id)
            # Roughly assuming 2.5 words per second in Hindi for estimation if not provided by LLM
            if seg.estimated_duration == 0.0:
                words = len(seg.translated_text.split())
                seg.estimated_duration = words / 2.5
                
            if seg.estimated_duration > orig.duration * 1.5:
                seg.timing_status = "exceeds_limit"
            else:
                seg.timing_status = "within_limit"
                
        return True
