from app.tools.synthesis_tools import synthesize_speech
import os

profile = {"speaker_id": "SPEAKER_00", "gender": "male", "age": "adult", "median_pitch": 120.0}
res = synthesize_speech("नमस्ते, हम इसे सुलझा लेंगे।", "test_final_synth.wav", profile, "neutral", target_duration=2.5)
print("Synthesis result:", res)
print("File exists and size:", os.path.exists("test_final_synth.wav"), os.path.getsize("test_final_synth.wav"))
