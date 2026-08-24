import os
import torch
from app.services.model_registry import ModelRegistry
from app.tools.alignment_tools import align_audio_duration

def clone_voice_xtts_v2(text: str, reference_audio_path: str, output_path: str, target_duration: float = None, language: str = "hi") -> dict:
    """
    Dedicated Coqui XTTS-v2 Zero-Shot Voice Cloning Engine.
    Clones the speaker's exact vocal timbre, identity, and fundamental frequency directly from reference_audio_path.
    NOTE: Frequency checks (match_voice_frequency) are strictly disabled here because XTTS-v2 naturally copies the speaker's pitch!
    """
    if not os.path.exists(reference_audio_path):
        return {"success": False, "message": f"Reference audio not found at {reference_audio_path}"}
        
    try:
        from TTS.api import TTS
        print(f"🎙️ [Coqui XTTS v2] Starting Zero-Shot Voice Cloning into {language}...")
        if not hasattr(ModelRegistry, "_xtts_v2_model"):
            print("Loading Coqui XTTS v2 neural weights (first time load may take a moment)...")
            device = "cuda" if torch.cuda.is_available() else "cpu"
            ModelRegistry._xtts_v2_model = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
            
        xtts_model = ModelRegistry._xtts_v2_model
        xtts_model.tts_to_file(
            text=text,
            speaker_wav=reference_audio_path,
            language=language,
            file_path=output_path
        )
        
        print(f"🎯 [Coqui XTTS v2] Voice cloned successfully to {output_path} without frequency manipulation!")
        
        # We only align time duration so that dialogue fits the video timestamp!
        if target_duration:
            align_audio_duration(output_path, target_duration, output_path)
            
        return {
            "success": True,
            "output_path": output_path,
            "model_used": "coqui-xtts-v2-cloned"
        }
    except Exception as e:
        print(f"❌ [Coqui XTTS v2] Cloning failed: {e}")
        return {"success": False, "message": str(e)}
