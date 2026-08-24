def detect_humor_type(text: str, genre: str) -> dict:
    if genre == "Comedy" or "joke" in text.lower():
        return {
            "humor_present": True,
            "humor_type": "sarcasm",
            "punchline_candidate": text[-10:] if len(text) > 10 else text,
            "confidence": 0.70
        }
    
    return {
        "humor_present": False,
        "humor_type": "no_humor",
        "punchline_candidate": None,
        "confidence": 0.90
    }
