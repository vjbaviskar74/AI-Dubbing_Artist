import json
import librosa
import soundfile as sf
from pathlib import Path
from ..schemas.translation import TranslationScript
from ..schemas.alignment import AlignmentResult
from ..config import settings

class DurationAlignment:
    def align(self, script: TranslationScript, converted_audios: dict, run_id: str) -> dict:
        output_dir = settings.default.paths.absolute_path(settings.base_dir, "runs_dir") / run_id / "aligned"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        aligned_files = {}
        metadata = []
        
        for seg in script.segments:
            if seg.turn_id not in converted_audios:
                continue
                
            input_audio = converted_audios[seg.turn_id]
            out_path = output_dir / f"turn_{seg.turn_id:03d}.wav"
            
            y, sr = librosa.load(input_audio, sr=settings.audio.audio.sample_rate)
            generated_duration = librosa.get_duration(y=y, sr=sr)
            target_duration = seg.target_duration
            
            ratio = generated_duration / target_duration if target_duration > 0 else 1.0
            
            tolerance = settings.audio.alignment.tolerance_ratio
            max_stretch = settings.audio.alignment.max_stretch_ratio
            min_stretch = settings.audio.alignment.min_stretch_ratio
            
            method = "none"
            final_y = y
            
            if abs(ratio - 1.0) > tolerance:
                if ratio > max_stretch:
                    method = "clipped_or_warned" # For now, mild stretch to max
                    stretch_factor = generated_duration / (target_duration * max_stretch)
                    final_y = librosa.effects.time_stretch(y, rate=stretch_factor)
                elif ratio < min_stretch:
                    method = "mild_expansion"
                    stretch_factor = generated_duration / target_duration
                    final_y = librosa.effects.time_stretch(y, rate=stretch_factor)
                else:
                    method = "time_compression" if ratio > 1.0 else "time_expansion"
                    final_y = librosa.effects.time_stretch(y, rate=ratio)
                    
            sf.write(str(out_path), final_y, sr)
            aligned_files[seg.turn_id] = str(out_path)
            
            metadata.append(AlignmentResult(
                turn_id=seg.turn_id,
                target_duration=target_duration,
                generated_duration=generated_duration,
                ratio=ratio,
                method=method,
                final_duration=librosa.get_duration(y=final_y, sr=sr)
            ))
            
        with open(output_dir / "alignment_metadata.json", "w") as f:
            json.dump([m.model_dump() for m in metadata], f, indent=2)
            
        return aligned_files
