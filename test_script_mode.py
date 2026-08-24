import sys
sys.stdout.reconfigure(encoding='utf-8')
from app.tools.script_alignment_tools import align_and_proofread_with_script

# Simulate a case where Mode 1 fallback clustering lumped both characters into SPEAKER_00!
test_segments = [
    {"start": 0.0, "end": 2.5, "speaker": "SPEAKER_00", "original_tag": "SPEAKER_00", "text": "I'll be pack."},
    {"start": 3.0, "end": 5.5, "speaker": "SPEAKER_00", "original_tag": "SPEAKER_00", "text": "Why so serious?"},
    {"start": 6.0, "end": 8.5, "speaker": "SPEAKER_00", "original_tag": "SPEAKER_00", "text": "Where are thay?"}
]

test_speaker_map = {
    "SPEAKER_00": {"speaker_id": "SPEAKER_00", "gender": "male", "median_pitch": 115.0}
}

official_script = """
BATMAN: I'll be back.
JOKER: Why so serious?
BATMAN: Where are they?!
"""

new_segs, new_map = align_and_proofread_with_script(test_segments, test_speaker_map, official_script)

print("\n--- FINAL ALIGNED SEGMENTS ---")
for s in new_segs:
    print(f"[{s['start']}s - {s['end']}s] {s['speaker']}: {s['text']} (orig ASR: {s.get('original_asr_text', '')})")

print("\n--- FINAL SPEAKER MAP ---")
for k, v in new_map.items():
    print(f"{k} => {v}")
