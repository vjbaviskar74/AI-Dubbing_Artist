import json
import os
from pathlib import Path
from ..schemas.diarization import Diarization
from ..utils.subprocess_utils import run_command
from ..config import settings

class ReferenceExtraction:
    def extract(self, audio_path: str, diarization: Diarization, run_id: str) -> dict:
        """Extracts clean reference audio clips for each speaker."""
        output_dir = settings.default.paths.absolute_path(settings.base_dir, "runs_dir") / run_id / "references"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        references = {}
        
        # We find the longest continuous turn for each speaker
        speaker_turns = {}
        for turn in diarization.turns:
            if turn.speaker_id not in speaker_turns:
                speaker_turns[turn.speaker_id] = []
            speaker_turns[turn.speaker_id].append(turn)
            
        for speaker_id, turns in speaker_turns.items():
            # Get longest turn
            longest = max(turns, key=lambda t: t.duration)
            ref_path = output_dir / f"{speaker_id}.wav"
            
            # Avoid too short references
            if longest.duration < 1.0:
                print(f"Warning: Longest turn for {speaker_id} is very short ({longest.duration}s)")
                
            # Use ffmpeg to slice the audio
            cmd = [
                "ffmpeg", "-y",
                "-i", audio_path,
                "-ss", str(longest.start),
                "-t", str(longest.duration),
                "-acodec", "pcm_s16le",
                "-ar", "24000",
                "-ac", "1",
                str(ref_path)
            ]
            run_command(cmd)
            
            if ref_path.exists():
                references[speaker_id] = {
                    "speaker_id": speaker_id,
                    "reference_audio_path": str(ref_path),
                    "duration": longest.duration
                }
                
        metadata_path = output_dir / "reference_metadata.json"
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(references, f, indent=2)
            
        return references
