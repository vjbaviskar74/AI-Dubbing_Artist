import sys
sys.stdout.reconfigure(encoding='utf-8')
from app.tools.script_alignment_tools import align_and_proofread_with_script

test_segments = [
    {"start": 0.0, "end": 2.5, "speaker": "SPEAKER_00", "original_tag": "SPEAKER_00", "text": "I am Mike."},
    {"start": 3.0, "end": 5.5, "speaker": "SPEAKER_00", "original_tag": "SPEAKER_00", "text": "Actings what I live for."},
    {"start": 6.0, "end": 8.5, "speaker": "SPEAKER_00", "original_tag": "SPEAKER_00", "text": "Got to have faith."},
    {"start": 9.0, "end": 12.0, "speaker": "SPEAKER_00", "original_tag": "SPEAKER_00", "text": "You need to show everyone."}
]

test_speaker_map = {
    "SPEAKER_00": {"speaker_id": "SPEAKER_00", "gender": "male", "median_pitch": 120.0}
}

user_script = """
00:02.600 [SPEAKER 2 - Mike] I'm Mike.
00:04.760 [SPEAKER 2 - Mike] Acting's what I live and breathe for.
00:07.840 [SPEAKER 2 - Mike] And they got to have faith in myself.
00:10.640 [SPEAKER 3 - Love Interest] You need to show everyone who you are.
"""

new_segs, new_map = align_and_proofread_with_script(test_segments, test_speaker_map, user_script)

print("\n--- FINAL ALIGNED SEGMENTS FOR UI ---")
for s in new_segs:
    print(f"[{s['start']}s - {s['end']}s] SPEAKER: '{s['speaker']}' | TEXT: '{s['text']}'")

print("\n--- FINAL SPEAKER MAP ---")
for k, v in new_map.items():
    print(f"{k} => {v}")
