def predict_emotion(features: dict) -> str:
    if features.get("energy", 0) > 0.8:
        return "angry"
    return "neutral"
