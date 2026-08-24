def detect_or_assign_genre(text: str, user_genre: str = None) -> dict:
    if user_genre:
        return {
            "genre": user_genre,
            "scene_mood": "neutral",
            "confidence": 1.0
        }
    
    # Very basic heuristic for fallback
    lower_text = text.lower()
    if "kill" in lower_text or "blood" in lower_text:
        genre = "Thriller"
    elif "love" in lower_text:
        genre = "Romance"
    elif "joke" in lower_text or "haha" in lower_text:
        genre = "Comedy"
    else:
        genre = "Drama"

    return {
        "genre": genre,
        "scene_mood": "detected_mood_placeholder",
        "confidence": 0.75
    }
