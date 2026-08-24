# NaturalDub AI
### Context-Aware, Timing-Aware and Voice-Preserving AI Video Dubbing System

NaturalDub AI is an end-to-end multimodal video-localization pipeline that accepts a short English or foreign-language movie/video clip and generates a naturally dubbed Hindi or Hinglish version.

## Architecture

The system is built on a robust, modular 3-Agent LangGraph orchestration:
1. **Media Intelligence Agent**: Handles ASR (Groq Whisper), Diarization (Pyannote), Audio Separation (Demucs), and Speaker Turn Reconstruction.
2. **Transcreation Director Agent**: Performs Context Analysis and Isochronous (timing-aware) Hindi/Hinglish Transcreation using configurable LLMs (OpenRouter/Groq/Gemini).
3. **Voice & Mastering Agent**: Generates base Hindi TTS (Sarvam API), runs Zero-Shot Voice Conversion (Seed-VC), Duration Alignment, and mixes the final output with preserved original background music.

## Setup Instructions

1. Clone the repository.
2. Create a Python 3.11 virtual environment.
3. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and fill in your API keys (GROQ, HF_AUTH_TOKEN, SARVAM, etc).

## Execution

### Streamlit UI (Recommended)
Launch the phased Streamlit interface for human-in-the-loop review:
```bash
streamlit run src/naturaldub/app.py
```

### CLI Execution
Run the full pipeline directly (requires all API keys set):
```bash
python -m src.naturaldub.cli --video path/to/video.mp4
```

## Known Limitations
- Seed-VC processing requires significant VRAM; CPU fallback is extremely slow.
- Timings are approximated and time-stretched; highly compressed durations may sound robotic.
- Pyannote speaker diarization can struggle with heavy background noise.

## Ethics and Consent
This tool uses Voice Conversion technology. You must have authorization and consent to clone or imitate a person's voice.
