from app.config import settings

class ModelRegistry:
    @staticmethod
    def is_available(model_name: str) -> bool:
        if not settings.ENABLE_ADVANCED_MODELS:
            return False
            
        # Placeholder logic
        available_models = ["demucs", "faster-whisper", "pyannote", "indictrans2", "openvoice", "wav2lip"]
        return model_name in available_models
