import re
import difflib
from typing import List, Dict, Any, Tuple

def align_and_proofread_with_script(segments: List[Dict[str, Any]], speaker_map: Dict[str, Any], script_text: str) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Studio Mode Phase 2 Tool (Chronological Sequential Matching):
    1. Automatic Character Naming: Strictly maps each segment to its exact script character line by line.
    2. Perfect Text Correction: Replaces Whisper ASR transcriptions with official script dialogue while preserving exact timestamps.
    """
    if not script_text or not segments:
        return segments, speaker_map
        
    print("\n🎬 Engaging Studio Mode: Chronological Script Alignment & AI Proofreading...")
    
    # 1. Parse official script into character lines
    # Supports formats like:
    # BATMAN: I'll be back.
    # [Batman] I'll be back.
    # Batman - I'll be back.
    script_lines = []
    lines = script_text.strip().split('\n')
    current_char = "SPEAKER_00"
    
    for line in lines:
        line_clean = line.strip()
        if not line_clean:
            continue
            
        # 1. Strip leading timestamp (e.g., 00:04.760, [00:04.760], 01:23:45.678)
        line_no_ts = re.sub(r'^\[?(\d{1,2}:)?\d{2}:\d{2}(?:\.\d{1,3})?\]?\s*', '', line_clean)
        
        # 2. Check for bracketed or parenthesized character names: [SPEAKER 2 - Mike] or (Mike)
        bracket_match = re.match(r'^[\[\(]([^\]\)]+)[\]\)]\s*(.*)$', line_no_ts)
        if bracket_match and len(bracket_match.group(1).strip()) < 50:
            current_char = bracket_match.group(1).strip().upper()
            dialogue = bracket_match.group(2).strip()
            script_lines.append({"character": current_char, "text": dialogue})
        else:
            # 3. Check for CHARACTER: dialogue or CHARACTER - dialogue
            colon_match = re.match(r'^([A-Za-z0-9\s_-]{2,30}?)(?::|\s+-\s+)(.*)$', line_no_ts)
            if colon_match and len(colon_match.group(2).strip()) > 1:
                current_char = colon_match.group(1).strip().upper()
                dialogue = colon_match.group(2).strip()
                script_lines.append({"character": current_char, "text": dialogue})
            else:
                # Continue dialogue for current character
                script_lines.append({"character": current_char, "text": line_no_ts})
            
    if not script_lines:
        print("Could not extract character structures from script. Returning original segments.")
        return segments, speaker_map
        
    # 2. Chronological Sequential Window Matching
    # Steps through audio segments and aligns with official script lines in order
    script_idx = 0
    num_script_lines = len(script_lines)
    
    for i, seg in enumerate(segments):
        whisper_text = seg.get("text", "").strip()
        if not whisper_text:
            continue
            
        best_match_ratio = -1.0
        best_line_idx = script_idx
        
        # Search a chronological window of script lines (from current script_idx up to script_idx + 6)
        search_end = min(num_script_lines, script_idx + 6)
        for idx in range(script_idx, search_end):
            s_text = script_lines[idx]["text"]
            ratio = difflib.SequenceMatcher(None, whisper_text.lower(), s_text.lower()).ratio()
            if ratio > best_match_ratio:
                best_match_ratio = ratio
                best_line_idx = idx
                
        # Also check all script lines as a fallback if window ratio was too low (< 0.25)
        if best_match_ratio < 0.25:
            for idx, s_line in enumerate(script_lines):
                ratio = difflib.SequenceMatcher(None, whisper_text.lower(), s_line["text"].lower()).ratio()
                if ratio > best_match_ratio:
                    best_match_ratio = ratio
                    best_line_idx = idx
                    
        matched_line = script_lines[best_line_idx]
        real_char = matched_line["character"]
        
        print(f"   => Line {i+1} ASR: '{whisper_text}'")
        print(f"   => Studio Assigned: [{real_char}] -> '{matched_line['text']}' [Match: {int(best_match_ratio*100)}%]\n")
        
        # Save original acoustic speaker tag before overwriting with script character name
        if "original_tag" not in seg:
            seg["original_tag"] = seg.get("speaker", "SPEAKER_00")
            
        # Assign real character directly to this segment (NO majority voting override!)
        seg["speaker"] = real_char
        seg["text"] = matched_line["text"]
        seg["original_asr_text"] = whisper_text
        
        # Advance chronological script pointer (so next audio line matches next script line)
        script_idx = min(num_script_lines - 1, best_line_idx + 1)
        
    # 3. Build Studio Mode Speaker Map for all unique characters detected
    new_speaker_map = {}
    unique_chars = set(seg.get("speaker", "SPEAKER_00") for seg in segments)
    
    # Inherit acoustic profile from original speaker tags in Phase 1 without gender detection
    char_profile_map = {}
    for seg in segments:
        char = seg.get("speaker")
        orig_tag = seg.get("original_tag", "SPEAKER_00")
        if char not in char_profile_map and orig_tag in speaker_map:
            char_profile_map[char] = speaker_map[orig_tag]
            
    for char_name in unique_chars:
        orig_profile = char_profile_map.get(char_name, {})
        base_pitch = orig_profile.get("median_pitch", 120.0)
        gender = orig_profile.get("gender", "original")
        
        # In Mode 2: Do NOT detect gender or alter pitch. Directly prepare profile for zero-shot voice cloning!
        new_speaker_map[char_name] = {
            "speaker_id": char_name,
            "gender": gender,
            "median_pitch": base_pitch,
            "tempo": orig_profile.get("tempo", 1.0),
            "age": orig_profile.get("age", "adult"),
            "studio_mode": True
        }
        print(f"🎯 Studio Mode Roster Created: [{char_name}] => Exact Original Video Acoustics Inherited (Pitch: {base_pitch:.1f}Hz, Voice Cloning Ready)")
        
    return segments, new_speaker_map
