from typing import Dict, Any
from ..schemas.state import NaturalDubState
from ..schemas.translation import TranslationScript, TranslatedSegment
from ..pipeline.tts_generation import TTSGeneration
from ..pipeline.voice_conversion import VoiceConversion
from ..pipeline.duration_alignment import DurationAlignment
from ..pipeline.timeline_assembly import TimelineAssembly
from ..pipeline.mixing import Mixing
from ..pipeline.multiplexing import Multiplexing
from ..pipeline.quality_assurance import QualityAssurance

def voice_mastering_node(state: NaturalDubState) -> Dict[str, Any]:
    run_id = state["run_id"]
    script_data = state.get("approved_script", state.get("translations", []))
    script = TranslationScript(segments=[TranslatedSegment(**s) for s in script_data])
    
    total_duration = state["media_metadata"]["duration"]
    background_track = state["background_audio"]
    video_path = state["input_video"]
    references = state["speaker_references"]
    
    # Init tools
    tts = TTSGeneration()
    vc = VoiceConversion()
    aligner = DurationAlignment()
    assembler = TimelineAssembly()
    mixer = Mixing()
    muxer = Multiplexing()
    qa = QualityAssurance()
    
    # 1. TTS Generation
    base_audios = tts.generate(script, run_id)
    
    # 2. Voice Conversion
    converted_audios = vc.convert(script, base_audios, references, run_id)
    
    # 3. Duration Alignment
    aligned_audios = aligner.align(script, converted_audios, run_id)
    
    # 4. Timeline Assembly
    dialogue_track = assembler.assemble(script, aligned_audios, total_duration, run_id)
    
    # 5. Mixing
    final_mix = mixer.mix(dialogue_track, background_track, run_id)
    
    # 6. Multiplexing
    final_video = muxer.multiplex(video_path, final_mix, run_id)
    
    # 7. QA
    qa_report = qa.generate_report(state)
    
    return {
        "base_audio_files": base_audios,
        "converted_audio_files": converted_audios,
        "aligned_audio_files": aligned_audios,
        "final_dialogue_track": dialogue_track,
        "final_mix": final_mix,
        "output_video": final_video,
        "qa_report": qa_report,
        "current_phase": "voice_mastering",
        "completed_phases": state.get("completed_phases", []) + ["voice_mastering"]
    }
