import numpy as np
import soundfile as sf
from app.tools.diarization_tools import analyze_speaker_acoustics
import os

# Create a dummy 200 Hz female-pitch sine wave audio file
sr = 16000
t = np.linspace(0, 2.0, int(2.0 * sr), endpoint=False)
y_female = 0.5 * np.sin(2 * np.pi * 210.0 * t)
sf.write("test_female_sine.wav", y_female, sr)

# Create a dummy 110 Hz male-pitch sine wave audio file
y_male = 0.5 * np.sin(2 * np.pi * 115.0 * t)
sf.write("test_male_sine.wav", y_male, sr)

print("Testing 210Hz Female Sine Wave:")
res_f = analyze_speaker_acoustics("test_female_sine.wav", 0.0, 2.0)
print("Result Female:", res_f)

print("\nTesting 115Hz Male Sine Wave:")
res_m = analyze_speaker_acoustics("test_male_sine.wav", 0.0, 2.0)
print("Result Male:", res_m)
