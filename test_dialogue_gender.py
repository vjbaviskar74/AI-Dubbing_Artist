import sys
sys.stdout.reconfigure(encoding='utf-8')

def detect_gender_from_dialogue(text: str, fallback_gender: str = "male") -> str:
    """Scans Hindi dialogue formations for grammatical gender conjugations."""
    female_markers = [
        "रही हूँ", "रही है", "रही थी", "करती हूँ", "करती है", "गई", "आई हूँ", 
        "बेटी", "लड़की", "मम्मी", "चाची", "दीदी", "बहन", "सकती हूँ", "चाहती हूँ",
        "मेरी बात", "मैं अकेली", "थकी हुई"
    ]
    male_markers = [
        "रहा हूँ", "रहा है", "रहा था", "करता हूँ", "करता है", "गया", "आया हूँ", 
        "बेटा", "लड़का", "पापा", "चाचा", "भैया", "भाई", "सकता हूँ", "चाहता हूँ",
        "मेरा बात", "मैं अकेला", "थका हुआ"
    ]
    
    text_lower = text.lower()
    f_score = sum(1 for m in female_markers if m in text_lower)
    m_score = sum(1 for m in male_markers if m in text_lower)
    
    if f_score > m_score:
        return "female"
    elif m_score > f_score:
        return "male"
    return fallback_gender

# Test cases
test_dialogues = [
    "भगवान, मैं अपने पिताजी जैसा लग रहा हूँ।", # Male
    "मैं आज बहुत थक गई हूँ, घर जा रही हूँ।", # Female
    "ठीक है, हम इसे सुलझा लेंगे।" # Neutral (falls back to acoustic gender)
]

for i, d in enumerate(test_dialogues):
    res = detect_gender_from_dialogue(d, 'male').upper()
    print(f"Test {i+1} => Detected Grammatical Gender: {res}")
