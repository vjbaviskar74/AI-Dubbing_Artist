import shutil
import subprocess
import soundfile as sf
import os
import tempfile
import math

def align_audio_duration(audio_path: str, target_duration: float, output_path: str) -> dict:
    try:
        print(f"Aligning {audio_path} to {target_duration} seconds.")
        
        # Trim leading and trailing silence first using ffmpeg
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_trimmed:
            trimmed_path = tmp_trimmed.name
            
        # -35dB threshold for trimming silence
        cmd_trim = [
            "ffmpeg", "-y", "-i", audio_path, 
            "-af", "silenceremove=start_periods=1:start_duration=0:start_threshold=-35dB,areverse,silenceremove=start_periods=1:start_duration=0:start_threshold=-35dB,areverse", 
            trimmed_path
        ]
        subprocess.run(cmd_trim, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Get trimmed duration
        info = sf.info(trimmed_path)
        current_duration = info.duration
        
        # Calculate speed factor required
        speed_factor = current_duration / target_duration
        
        # Clamp speed factor to avoid extreme phase blurring and speech stuttering
        speed_factor = max(0.75, min(1.35, speed_factor))
        
        print(f"Original duration (trimmed): {current_duration:.2f}s, Target: {target_duration:.2f}s, Speed factor: {speed_factor:.2f}x")
        
        # Stretch time without changing pitch using atempo
        cmd_stretch = [
            "ffmpeg", "-y", "-i", trimmed_path,
            "-filter:a", f"atempo={speed_factor}",
            output_path
        ]
        subprocess.run(cmd_stretch, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        if os.path.exists(trimmed_path):
            os.remove(trimmed_path)
            
        return {
            "success": True,
            "output_path": output_path,
            "aligned_duration": target_duration,
            "speed_factor": speed_factor
        }
    except Exception as e:
        print(f"FFmpeg alignment failed: {e}")
        # Fallback to just copying
        if audio_path != output_path:
            shutil.copy(audio_path, output_path)
        return {
            "success": False,
            "output_path": output_path,
            "aligned_duration": target_duration,
            "speed_factor": 1.0
        }

def match_voice_frequency(audio_path: str, original_pitch: float, generated_base_pitch: float, output_path: str) -> dict:
    """Pitch-shifts the generated audio to mathematically match the original speaker's frequency."""
    try:
        # Calculate the shift in semitones
        # formula: n_steps = 12 * log2(f_target / f_base)
        n_steps = 12 * math.log2(original_pitch / generated_base_pitch)
        
        # Cap the shift to +/- 2.2 semitones to preserve natural vocal resonance
        n_steps = max(-2.2, min(2.2, n_steps))
        
        if abs(n_steps) < 0.1:
            # Shift is negligible, just copy
            if audio_path != output_path:
                shutil.copy(audio_path, output_path)
            return {"success": True, "n_steps": 0.0}
            
        print(f"Applying acoustic pitch shift: {n_steps:.2f} semitones to match {original_pitch:.1f}Hz")
        
        # Calculate pitch shift factor
        pitch_factor = 2 ** (n_steps / 12.0)
        
        info = sf.info(audio_path)
        sr = info.samplerate
        
        new_sr = int(sr * pitch_factor)
        # asetrate makes it 1/pitch_factor faster, atempo stretches it back to original length
        tempo_factor = 1.0 / pitch_factor 
        
        cmd = [
            "ffmpeg", "-y", "-i", audio_path,
            "-filter:a", f"asetrate={new_sr},atempo={tempo_factor},aresample={sr}",
            output_path
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        return {
            "success": True,
            "output_path": output_path,
            "n_steps": n_steps
        }
    except Exception as e:
        print(f"FFmpeg pitch shifting failed: {e}")
        if audio_path != output_path:
            shutil.copy(audio_path, output_path)
        return {"success": False, "n_steps": 0.0}
