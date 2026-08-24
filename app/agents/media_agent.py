from app.graph.state import DubbingState
from app.tools.ffmpeg_tools import extract_audio
from app.tools.separation_tools import separate_dialogue_background
from app.tools.transcription_tools import transcribe_audio
from app.tools.diarization_tools import diarize_speakers

def run_media_agent(state: DubbingState) -> DubbingState:
    print(f"Running Media Agent for job {state['job_id']}")
    
    # 1. Extract audio
    extracted_path = f"artifacts/extracted_audio/{state['job_id']}.wav"
    ext_res = extract_audio(state['input_video_path'], extracted_path)
    state['audio_paths'] = {'extracted': ext_res['output_path']}
    
    # 2. Separate
    sep_dir = f"artifacts/separated_audio/{state['job_id']}"
    import os
    os.makedirs(sep_dir, exist_ok=True)
    sep_res = separate_dialogue_background(ext_res['output_path'], sep_dir)
    state['audio_paths']['dialogue'] = sep_res['dialogue']
    state['audio_paths']['background'] = sep_res['background']
    
    # 3. Transcribe
    trans_res = transcribe_audio(sep_res['dialogue'], state['source_language'])
    state['segments'] = trans_res.get('segments', [])
    
    # 4. Diarize
    diarize_res = diarize_speakers(sep_res['dialogue'])
    
    # 5. Map Speakers to Transcript and Detect Gender/Acoustics
    speaker_map = {}
    from app.tools.diarization_tools import analyze_speaker_acoustics
    
    if diarize_res.get('success') and diarize_res.get('segments'):
        pyannote_segs = diarize_res['segments']
        
        for w_seg in state['segments']:
            w_start = w_seg.get('start', 0)
            w_end = w_seg.get('end', 0)
            
            # Find the pyannote segment with the highest overlap
            best_speaker = "SPEAKER_00"
            max_overlap = 0
            
            for p_seg in pyannote_segs:
                overlap_start = max(w_start, p_seg['start'])
                overlap_end = min(w_end, p_seg['end'])
                overlap = max(0, overlap_end - overlap_start)
                
                if overlap > max_overlap:
                    max_overlap = overlap
                    best_speaker = p_seg['speaker']
            
            w_seg['speaker'] = best_speaker
            
            # Extract acoustics for the speaker if we haven't already
            if best_speaker not in speaker_map:
                acoustics = analyze_speaker_acoustics(sep_res['dialogue'], p_seg['start'], p_seg['end'])
                speaker_map[best_speaker] = {
                    "speaker_id": best_speaker,
                    "median_pitch": acoustics["median_pitch"],
                    "tempo": acoustics["tempo"],
                    "age": acoustics.get("age", "adult")
                }
                print(f"\\n🎯 SPEAKER DETECTED [{best_speaker}]:")
                print(f"   => Age: {acoustics.get('age', 'adult').upper()}\\n")
    else:
        print("Pyannote DLL blocked by Windows! Engaging Native Deep-Learning Acoustic Clustering...")
        # Pure native clustering using Whisper timestamps + Wav2Vec2 Acoustics
        speaker_map = {}
        speaker_counter = 0
        
        for w_seg in state['segments']:
            w_start = w_seg.get('start', 0)
            w_end = w_seg.get('end', 0)
            
            # 1. Analyze the exact acoustics of this sentence
            acoustics = analyze_speaker_acoustics(sep_res['dialogue'], w_start, w_end)
            pitch = acoustics['median_pitch']
            
            # 2. Find if this matches an existing speaker in our map
            matched_speaker_id = None
            for s_id, s_profile in speaker_map.items():
                # A speaker matches if pitch is within ~40Hz
                if abs(s_profile['median_pitch'] - pitch) < 40.0:
                    matched_speaker_id = s_id
                    break
                    
            # 3. If no match, create a new speaker!
            if not matched_speaker_id:
                speaker_counter += 1
                matched_speaker_id = f"SPEAKER_{speaker_counter:02d}"
                speaker_map[matched_speaker_id] = {
                    "speaker_id": matched_speaker_id,
                    "median_pitch": pitch,
                    "tempo": acoustics['tempo'],
                    "age": acoustics.get("age", "adult")
                }
                print(f"\\n🎯 NATIVE SPEAKER CLUSTERED [{matched_speaker_id}]:")
                print(f"   => Age: {acoustics.get('age', 'adult').upper()}")
                print(f"   => Base Pitch: {pitch:.1f}Hz\\n")
                
            w_seg['speaker'] = matched_speaker_id
            
    state['speaker_map'] = speaker_map
    
    # 6. Studio Mode: Script Alignment & AI Proofreading (if script uploaded)
    if state.get('script_text'):
        from app.tools.script_alignment_tools import align_and_proofread_with_script
        aligned_segs, aligned_map = align_and_proofread_with_script(
            state['segments'], 
            state['speaker_map'], 
            state['script_text']
        )
        state['segments'] = aligned_segs
        state['speaker_map'] = aligned_map
        state['studio_mode'] = True
        
    return state
