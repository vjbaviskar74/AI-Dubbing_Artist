import json
from pathlib import Path
from ..config import settings
from ..schemas.state import NaturalDubState

class QualityAssurance:
    def generate_report(self, state: NaturalDubState) -> dict:
        run_id = state.get("run_id")
        output_dir = settings.default.paths.absolute_path(settings.base_dir, "runs_dir") / run_id / "output"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        report_path = output_dir / "qa_report.json"
        
        # Build basic QA report based on state
        translations = state.get("approved_script", [])
        total_duration_error = 0.0
        
        if state.get("aligned_audio_files"):
            # Mock calculation for QA metric
            pass
            
        report = {
            "run_id": run_id,
            "asr": {
                "duration_transcribed": state.get("transcript", {}).get("duration", 0)
            },
            "diarization": {
                "num_speakers": len(state.get("speaker_references", {}))
            },
            "translation": {
                "total_turns": len(translations)
            },
            "warnings": state.get("warnings", []),
            "errors": state.get("errors", [])
        }
        
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
            
        return report
