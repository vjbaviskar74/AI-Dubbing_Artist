from pydub import AudioSegment
from pathlib import Path
from ..schemas.translation import TranslationScript
from ..config import settings

class TimelineAssembly:
    def assemble(self, script: TranslationScript, aligned_audios: dict, total_duration: float, run_id: str) -> str:
        output_dir = settings.default.paths.absolute_path(settings.base_dir, "runs_dir") / run_id / "mixed"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_path = output_dir / "dialogue_track.wav"
        
        if output_path.exists():
            return str(output_path)
            
        # Create silent track
        timeline = AudioSegment.silent(duration=int(total_duration * 1000), frame_rate=settings.audio.audio.export_sample_rate)
        timeline = timeline.set_channels(settings.audio.audio.export_channels)
        
        for seg in script.segments:
            if seg.turn_id in aligned_audios:
                audio_path = aligned_audios[seg.turn_id]
                segment_audio = AudioSegment.from_file(audio_path)
                
                # Convert format if needed
                if segment_audio.frame_rate != settings.audio.audio.export_sample_rate:
                    segment_audio = segment_audio.set_frame_rate(settings.audio.audio.export_sample_rate)
                if segment_audio.channels != settings.audio.audio.export_channels:
                    segment_audio = segment_audio.set_channels(settings.audio.audio.export_channels)
                    
                start_ms = int(seg.start * 1000)
                timeline = timeline.overlay(segment_audio, position=start_ms)
                
        timeline.export(str(output_path), format="wav")
        return str(output_path)
