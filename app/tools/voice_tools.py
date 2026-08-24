import numpy as np

def analyze_voice(audio_path: str) -> dict:
    try:
        import librosa
        # Load audio (downsample to 16kHz for faster processing)
        y, sr = librosa.load(audio_path, sr=16000)
        
        # Calculate Pitch (F0)
        f0, voiced_flag, voiced_probs = librosa.pyin(
            y, 
            fmin=librosa.note_to_hz('C2'), 
            fmax=librosa.note_to_hz('C6')
        )
        
        # Get median pitch, ignoring unvoiced segments (NaN)
        valid_f0 = f0[~np.isnan(f0)]
        median_pitch = float(np.median(valid_f0)) if len(valid_f0) > 0 else 150.0
        
        # Calculate Tempo (speaking rate)
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        tempo, _ = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)
        # Extract scalar value from 1D array if necessary
        tempo_val = float(tempo[0]) if isinstance(tempo, np.ndarray) else float(tempo)
        
        duration = float(librosa.get_duration(y=y, sr=sr))
        
        return {
            "median_pitch": median_pitch,
            "tempo": tempo_val,
            "duration": duration,
            "rms_energy": float(np.mean(librosa.feature.rms(y=y)))
        }
    except Exception as e:
        print(f"Voice analysis failed: {e}")
        return {
            "median_pitch": 150.0,
            "tempo": 120.0,
            "duration": 5.0,
            "rms_energy": 0.1
        }
