import subprocess
import os
import numpy as np
import soundfile as sf

# Create a test dialogue tone (440Hz + 1000Hz speech-like mix)
sr = 24000
t = np.linspace(0, 3.0, int(3.0 * sr), endpoint=False)
y_dial = 0.4 * np.sin(2 * np.pi * 300.0 * t) + 0.3 * np.sin(2 * np.pi * 1200.0 * t)
sf.write("test_raw_dial.wav", y_dial, sr)

# Create a test background rumble/noise
y_bg = 0.3 * np.random.normal(0, 1, len(t))
sf.write("test_raw_bg.wav", y_bg, sr)

print("Testing FFmpeg Vocal Clarity Chain with Background Mixing...")
cmd = [
    "ffmpeg", "-y", "-i", "test_raw_bg.wav", "-i", "test_raw_dial.wav",
    "-filter_complex", "[0:a]volume=0.18[bg];[1:a]highpass=f=80,treble=g=3,volume=2.2,acompressor=threshold=-14dB:ratio=3:attack=5:release=50[dial];[bg][dial]amix=inputs=2:duration=first:dropout_transition=2:normalize=0",
    "test_clarity_mixed.wav"
]

res = subprocess.run(cmd, capture_output=True, text=True)
if res.returncode == 0:
    print("SUCCESS! FFmpeg Vocal Clarity Chain generated test_clarity_mixed.wav cleanly!")
else:
    print("FAILED! Error:", res.stderr)
