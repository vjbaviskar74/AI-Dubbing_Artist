import pytest
from naturaldub.pipeline.script_validation import ScriptValidation
from naturaldub.schemas.translation import TranslationScript, TranslatedSegment
from naturaldub.schemas.diarization import SpeakerTurn

def test_script_validation_success():
    validator = ScriptValidation()
    
    script = TranslationScript(segments=[
        TranslatedSegment(
            turn_id=1,
            speaker_id="SPEAKER_00",
            start=0.0,
            end=2.0,
            source_text="Hello",
            translated_text="Namaste",
            target_duration=2.0,
            estimated_duration=1.0
        )
    ])
    
    turns = [
        SpeakerTurn(
            turn_id=1,
            speaker_id="SPEAKER_00",
            start=0.0,
            end=2.0,
            duration=2.0,
            source_text="Hello"
        )
    ]
    
    assert validator.validate(script, turns) == True

def test_script_validation_missing_turn():
    validator = ScriptValidation()
    script = TranslationScript(segments=[])
    turns = [
        SpeakerTurn(
            turn_id=1,
            speaker_id="SPEAKER_00",
            start=0.0,
            end=2.0,
            duration=2.0,
            source_text="Hello"
        )
    ]
    
    with pytest.raises(ValueError, match="Missing turn_ids"):
        validator.validate(script, turns)
