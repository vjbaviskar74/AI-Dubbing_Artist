# NATURALDUB-AI Architecture

The system is built on a multi-agent LangGraph workflow coordinated by a FastAPI backend, interacting via a Streamlit UI.

1. **Media Agent**: Extracts audio, separates stems, transcribes, and diarizes.
2. **Translation & Context Agent**: Handles translation, genre detection, humor preservation, and cultural adaptation.
3. **Voice & Emotion Agent**: Handles emotion detection and TTS generation (with OpenVoice placeholder).
4. **Sync & QA Agent**: Mixes audio, aligns duration, handles lip sync, and generates evaluation reports.
