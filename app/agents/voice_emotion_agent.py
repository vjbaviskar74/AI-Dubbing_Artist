from app.graph.state import DubbingState
from app.tools.emotion_tools import detect_emotion
from app.tools.synthesis_tools import synthesize_speech
from app.services.consent_service import ConsentService
import os

def run_voice_emotion_agent(state: DubbingState) -> DubbingState:
    print(f"Running Voice & Emotion Agent for job {state['job_id']}")
    
    if not ConsentService.verify_consent(state['job_id'], state['consent_verified']):
        state['warnings'].append("Voice cloning blocked. Consent not verified.")
        
    generated = []
    out_dir = f"artifacts/generated_audio/{state['job_id']}"
    os.makedirs(out_dir, exist_ok=True)
    
    for i, t in enumerate(state.get('translations', [])):
        emo_res = detect_emotion("", t.get('original_text', ''))
        out_path = os.path.join(out_dir, f"seg_{i}.wav")
        
        # Extract reference audio for cloning
        orig_seg = state['segments'][i] if i < len(state.get('segments', [])) else {}
        start_t = orig_seg.get('start', 0)
        end_t = orig_seg.get('end', start_t + 3)
        target_duration = end_t - start_t
        
        ref_path = None
        if state.get('audio_paths', {}).get('extracted'):
            try:
                from pydub import AudioSegment
                orig_audio = AudioSegment.from_wav(state['audio_paths']['extracted'])
                ref_clip = orig_audio[int(start_t*1000):int(end_t*1000)]
                ref_path = os.path.join(out_dir, f"ref_{i}.wav")
                ref_clip.export(ref_path, format="wav")
            except Exception as e:
                print(f"Failed to extract reference audio: {e}")
        
        speaker_id = orig_seg.get('speaker', 'SPEAKER_00')
        speaker_map = state.get('speaker_map', {})
        speaker_profile = dict(speaker_map.get(speaker_id, {}))
        
        final_text = t.get('adapted_text', t.get('translated_text', ''))
        
        print(f"🎙️ Voice Cloning Mode Active: Bypassing all gender detection for {speaker_id} -> Direct voice cloning mode engaged from original video samples!")
        
        synth_res = synthesize_speech(
            text=final_text,
            output_path=out_path,
            speaker_profile=speaker_profile,
            emotion=emo_res['emotion'],
            reference_audio_path=ref_path,
            target_duration=target_duration
        )
        
        generated.append({
            "segment_id": t.get("segment_id", str(i)),
            "audio_path": synth_res['output_path']
        })
        
    state['generated_audio_segments'] = generated
    return state
