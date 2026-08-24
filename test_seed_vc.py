import os
import sys

# Add app to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.tools.synthesis_tools import synthesize_speech

def main():
    print("Running Kokoro + Seed-VC Synthesis Test...")
    text = "नमस्ते, मेरा नाम ब्रूस वेन है। मैं गोथम शहर की रक्षा करता हूँ।"
    output_path = "test_kokoro_seed_vc.wav"
    
    # Needs a reference audio path (use the test one we created earlier)
    reference_audio_path = "test_raw_dial.wav"
    
    if not os.path.exists(reference_audio_path):
        print(f"Error: Could not find reference audio {reference_audio_path}")
        return
        
    speaker_profile = {
        "speaker_id": "SPEAKER_00",
        "gender": "male",
        "median_pitch": 110.0,
        "tempo": 1.0
    }
    
    res = synthesize_speech(text, output_path, speaker_profile, "neutral", reference_audio_path)
    
    if res.get("success"):
        print(f"Success! Audio generated at {output_path} using {res.get('model_used')}")
    else:
        print(f"Failed to synthesize audio!")

if __name__ == "__main__":
    main()
