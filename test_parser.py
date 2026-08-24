import re

test_lines = [
    "00:02.600 [SPEAKER 2 - Mike] I'm Mike.",
    "00:04.760 [SPEAKER 2 - Mike] Acting's what I live and breathe for.",
    "00:07.840 [SPEAKER 2 - Mike] And they got to have faith in myself.",
    "00:10.640 [SPEAKER 3 - Love Interest] You need to show everyone who you are.",
    "BATMAN: I'll be back.",
    "[JOKER] Why so serious?",
    "01:23.456 Narrator - Previously on NaturalDub."
]

print("Testing Improved Script Line Parser...")
for line in test_lines:
    line_clean = line.strip()
    
    # 1. Strip leading timestamp (e.g., 00:04.760, [00:04.760], 01:23:45.678)
    line_no_ts = re.sub(r'^\[?(\d{1,2}:)?\d{2}:\d{2}(?:\.\d{1,3})?\]?\s*', '', line_clean)
    
    char_name = "UNKNOWN"
    dialogue = line_no_ts
    
    # 2. Check for bracketed or parenthesized character names: [SPEAKER 2 - Mike] or (Mike)
    bracket_match = re.match(r'^[\[\(]([^\]\)]+)[\]\)]\s*(.*)$', line_no_ts)
    if bracket_match and len(bracket_match.group(1).strip()) < 50:
        char_name = bracket_match.group(1).strip().upper()
        dialogue = bracket_match.group(2).strip()
    else:
        # 3. Check for CHARACTER: dialogue or CHARACTER - dialogue
        colon_match = re.match(r'^([A-Za-z0-9\s_-]{2,30}?)(?::|\s+-\s+)(.*)$', line_no_ts)
        if colon_match and len(colon_match.group(2).strip()) > 1:
            char_name = colon_match.group(1).strip().upper()
            dialogue = colon_match.group(2).strip()
            
    print(f"RAW: '{line}' -> CHAR: '{char_name}' | DIALOGUE: '{dialogue}'")
