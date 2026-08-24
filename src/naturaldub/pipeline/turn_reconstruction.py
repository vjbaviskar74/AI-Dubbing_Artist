import json
from typing import List
from pathlib import Path
from ..schemas.transcript import Transcript
from ..schemas.diarization import Diarization, SpeakerTurn
from ..config import settings

class TurnReconstruction:
    def reconstruct(self, transcript: Transcript, diarization: Diarization, run_id: str) -> List[SpeakerTurn]:
        """
        Aligns ASR words/segments with diarization intervals to reconstruct meaningful conversational turns.
        """
        output_dir = settings.default.paths.absolute_path(settings.base_dir, "runs_dir") / run_id / "transcripts"
        output_path = output_dir / "speaker_turns.json"
        
        if output_path.exists():
            try:
                with open(output_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return [SpeakerTurn(**t) for t in data]
            except Exception:
                pass
                
        # Simple alignment logic:
        # For each ASR segment, find the diarization turn with maximum overlap.
        # Then group consecutive segments by the same speaker into a single turn.
        
        assigned_segments = []
        for seg in transcript.segments:
            best_speaker = "SPEAKER_UNKNOWN"
            max_overlap = 0.0
            
            for turn in diarization.turns:
                overlap_start = max(seg.start, turn.start)
                overlap_end = min(seg.end, turn.end)
                overlap = max(0.0, overlap_end - overlap_start)
                
                if overlap > max_overlap:
                    max_overlap = overlap
                    best_speaker = turn.speaker_id
            
            assigned_segments.append({
                "speaker": best_speaker,
                "text": seg.text,
                "start": seg.start,
                "end": seg.end
            })
            
        # Group consecutive segments
        turns = []
        if not assigned_segments:
            return []
            
        current_turn = {
            "turn_id": 0,
            "speaker_id": assigned_segments[0]["speaker"],
            "character_name": None,
            "start": assigned_segments[0]["start"],
            "end": assigned_segments[0]["end"],
            "texts": [assigned_segments[0]["text"]]
        }
        
        turn_idx = 0
        for seg in assigned_segments[1:]:
            # If same speaker and gap is less than 2 seconds, merge
            if seg["speaker"] == current_turn["speaker_id"] and (seg["start"] - current_turn["end"]) < 2.0:
                current_turn["end"] = seg["end"]
                current_turn["texts"].append(seg["text"])
            else:
                current_turn["source_text"] = " ".join(current_turn["texts"])
                current_turn["duration"] = current_turn["end"] - current_turn["start"]
                del current_turn["texts"]
                turns.append(SpeakerTurn(**current_turn))
                
                turn_idx += 1
                current_turn = {
                    "turn_id": turn_idx,
                    "speaker_id": seg["speaker"],
                    "character_name": None,
                    "start": seg["start"],
                    "end": seg["end"],
                    "texts": [seg["text"]]
                }
                
        # Handle last turn
        if "texts" in current_turn:
            current_turn["source_text"] = " ".join(current_turn["texts"])
            current_turn["duration"] = current_turn["end"] - current_turn["start"]
            del current_turn["texts"]
            turns.append(SpeakerTurn(**current_turn))
            
        # Add pause information
        for i in range(len(turns)):
            if i > 0:
                turns[i].pause_before = max(0.0, turns[i].start - turns[i-1].end)
            if i < len(turns) - 1:
                turns[i].pause_after = max(0.0, turns[i+1].start - turns[i].end)
                
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump([t.model_dump() for t in turns], f, indent=2, ensure_ascii=False)
            
        return turns
