from app.graph.state import DubbingState
from app.tools.alignment_tools import align_audio_duration
from app.tools.mixing_tools import mix_dialogue_with_background
from app.tools.lipsync_tools import lip_sync_video
from app.tools.evaluation_tools import evaluate_output
import os
import shutil

def run_sync_qa_agent(state: DubbingState) -> DubbingState:
    print(f"Running Sync & QA Agent for job {state['job_id']}")
    
    # True Timeline Alignment using pydub
    timeline_path = f"artifacts/timelines/{state['job_id']}.wav"
    os.makedirs(os.path.dirname(timeline_path), exist_ok=True)
    
    try:
        from pydub import AudioSegment
        
        if state.get('audio_paths', {}).get('extracted') and os.path.exists(state['audio_paths']['extracted']):
            original_audio = AudioSegment.from_wav(state['audio_paths']['extracted'])
            timeline = AudioSegment.silent(duration=len(original_audio))
        else:
            timeline = AudioSegment.silent(duration=60000) # fallback 60 seconds
            
        generated_segs = state.get('generated_audio_segments', [])
        original_segs = state.get('segments', [])
        
        # We assume generated_audio_segments matches 1:1 with state['segments']
        # because translation_agent and voice_emotion_agent iterate over them linearly.
        last_end_ms = 0
        
        for i, gen_audio in enumerate(generated_segs):
            if i < len(original_segs):
                start_ms = int(original_segs[i].get('start', 0) * 1000)
                
                # Prevent overlapping dialog by enforcing a natural pause if the previous segment spilled over
                if start_ms < last_end_ms:
                    start_ms = last_end_ms + 100 # Add a small 100ms natural pause
                    
                try:
                    dub = AudioSegment.from_file(gen_audio['audio_path'])
                    timeline = timeline.overlay(dub, position=start_ms)
                    last_end_ms = start_ms + len(dub)
                except Exception as e:
                    print(f"Failed to overlay segment {i}: {e}")
                    
        print(f"Exporting full timeline to {timeline_path}")
        timeline.export(timeline_path, format="wav")
    except Exception as e:
        print(f"Pydub alignment failed: {e}")
        # Ultimate fallback just concatenates the first one if pydub isn't installed
        if state.get('generated_audio_segments'):
            shutil.copy(state['generated_audio_segments'][0]['audio_path'], timeline_path)
        else:
            open(timeline_path, 'a').close()
            
    state['timeline_path'] = timeline_path
    
    # Mixing
    mixed_path = f"artifacts/mixed_audio/{state['job_id']}.wav"
    os.makedirs(os.path.dirname(mixed_path), exist_ok=True)
    mix_dialogue_with_background(
        timeline_path, 
        state['audio_paths'].get('background', ''), 
        mixed_path
    )
    state['mixed_audio_path'] = mixed_path
    
    # Lip Sync
    final_video_path = f"artifacts/final_video/{state['job_id']}.mp4"
    os.makedirs(os.path.dirname(final_video_path), exist_ok=True)
    lip_sync_video(state['input_video_path'], mixed_path, final_video_path)
    state['final_video_path'] = final_video_path
    
    # Evaluation
    eval_report = evaluate_output(state)
    report_path = f"artifacts/reports/{state['job_id']}.json"
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    import json
    with open(report_path, "w") as f:
        json.dump(eval_report, f, indent=4)
        
    state['evaluation_report_path'] = report_path
    
    return state
