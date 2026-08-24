def predict_quality_score(metrics: dict) -> float:
    return sum(metrics.values()) / len(metrics) if metrics else 0.0
