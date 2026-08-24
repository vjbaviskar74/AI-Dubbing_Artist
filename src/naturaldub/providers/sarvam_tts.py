import os
import requests
from .base import BaseTTSProvider

class SarvamTTSProvider(BaseTTSProvider):
    def __init__(self):
        self.api_key = os.environ.get("SARVAM_API_KEY")
        self.url = "https://api.sarvam.ai/text-to-speech"
        
    def synthesize(self, text: str, speaker_id: str, output_path: str):
        if not self.api_key:
            # Fallback mock for testing
            print("SARVAM_API_KEY not set. Creating a mock audio file.")
            with open(output_path, "wb") as f:
                f.write(b"mock_audio_data")
            return
            
        payload = {
            "inputs": [text],
            "target_language_code": "hi-IN",
            "speaker": speaker_id,
            "pitch": 0,
            "pace": 1.0,
            "loudness": 1.5,
            "speech_sample_rate": 24000,
            "enable_preprocessing": True,
            "model": "bulbul:v3"
        }
        
        headers = {
            "api-subscription-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        response = requests.post(self.url, json=payload, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        audio_base64 = data.get("audios", [])[0]
        
        import base64
        audio_bytes = base64.b64decode(audio_base64)
        with open(output_path, "wb") as f:
            f.write(audio_bytes)
