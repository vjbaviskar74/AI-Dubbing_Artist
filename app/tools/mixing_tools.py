import shutil

def mix_dialogue_with_background(dialogue_path: str, background_path: str, output_path: str) -> dict:
    import subprocess
    import os
    try:
        # Check if background file exists and has size
        if os.path.exists(background_path) and os.path.getsize(background_path) > 100:
            print("Mixing dialogue and background audio using Broadcast Vocal Clarity Chain...")
            command = [
                "ffmpeg", "-y", "-i", background_path, "-i", dialogue_path,
                "-filter_complex", "[0:a]volume=0.18[bg];[1:a]highpass=f=80,treble=g=3,volume=2.2,acompressor=threshold=-14dB:ratio=3:attack=5:release=50[dial];[bg][dial]amix=inputs=2:duration=first:dropout_transition=2:normalize=0",
                output_path
            ]
            subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            print("No valid background audio found. Applying Broadcast Vocal Clarity Chain to dialogue...")
            command = [
                "ffmpeg", "-y", "-i", dialogue_path,
                "-af", "highpass=f=80,treble=g=3,volume=1.6,acompressor=threshold=-14dB:ratio=3:attack=5:release=50",
                output_path
            ]
            subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
        return {
            "success": True,
            "output_path": output_path,
            "message": "Audio mixed and clarified successfully"
        }
    except Exception as e:
        print(f"Audio mixing failed: {e}")
        shutil.copy(dialogue_path, output_path)
        return {
            "success": False,
            "output_path": output_path,
            "message": f"Mixing failed: {e}"
        }
