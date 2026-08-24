from app.tools.synthesis_tools import synthesize_speech
import os

profile1 = {"speaker_id": "SPEAKER_00", "gender": "male", "age": "adult", "median_pitch": 110.0}
profile2 = {"speaker_id": "SPEAKER_01", "gender": "male", "age": "adult", "median_pitch": 140.0}
profile3 = {"speaker_id": "SPEAKER_02", "gender": "female", "age": "adult", "median_pitch": 210.0}

print("Testing Speaker 0:")
res1 = synthesize_speech("नमस्ते, मैं पहला वक्ता हूँ।", "test_spk0.wav", profile1, "neutral")
print("Result 0:", res1)

print("Testing Speaker 1:")
res2 = synthesize_speech("नमस्ते, मैं दूसरा वक्ता हूँ।", "test_spk1.wav", profile2, "neutral")
print("Result 1:", res2)

print("Testing Speaker 2:")
res3 = synthesize_speech("नमस्ते, मैं तीसरी वक्ता हूँ।", "test_spk2.wav", profile3, "neutral")
print("Result 2:", res3)
