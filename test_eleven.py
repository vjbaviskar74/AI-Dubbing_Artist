import os
import requests
from dotenv import load_dotenv
load_dotenv()

key = os.environ.get("ELEVENLABS_API_KEY")
print(f"Key present: {bool(key)}")
url_tts = "https://api.elevenlabs.io/v1/text-to-speech/pNInz6obpgDQGcFmaJgB"
payload = {
    "text": "नमस्ते, मैं आपका स्वागत करता हूँ।",
    "model_id": "eleven_multilingual_v2",
    "voice_settings": {"stability": 0.35, "similarity_boost": 0.75}
}
headers = {"xi-api-key": key, "Content-Type": "application/json"}
try:
    res = requests.post(url_tts, headers=headers, json=payload)
    print(f"Status code: {res.status_code}")
    if not res.ok:
        print(f"Error text: {res.text}")
    else:
        print("ElevenLabs succeeded!")
except Exception as e:
    print(f"Request failed: {e}")
