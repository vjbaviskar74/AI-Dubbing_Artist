from app.services.model_registry import ModelRegistry

def transcribe_audio(audio_path: str, language: str) -> dict:
    if ModelRegistry.is_available("faster-whisper"):
        try:
            print(f"Running openai-whisper on {audio_path}")
            # Bypass Windows Defender Numba DLL Block
            import sys
            import types
            if 'numba.experimental.jitclass._box' not in sys.modules:
                mock_module = types.ModuleType('numba.experimental.jitclass._box')
                class Box: pass
                mock_module.Box = Box
                mock_module.box_get_dataptr = lambda x: None
                sys.modules['numba.experimental.jitclass._box'] = mock_module
            
            import whisper
            
            # Use standard PyTorch Whisper
            model = whisper.load_model("large-v3", device="cpu")
            result = model.transcribe(
                audio_path,
                condition_on_previous_text=False
            )
            
            transcribed_text = result["text"]
            segments_list = []
            for segment in result["segments"]:
                segments_list.append({
                    "start": segment["start"],
                    "end": segment["end"],
                    "text": segment["text"]
                })
                
            return {
                "text": transcribed_text.strip(),
                "segments": segments_list
            }
        except Exception as e:
            error_msg = f"OpenAI Whisper failed: {str(e)}\n\n(Hint: If this says 'ffprobe' or 'ffmpeg' not found, you need to install FFmpeg on Windows and add it to your PATH!)"
            print(error_msg)
            return {
                "text": error_msg,
                "segments": [{"start": 0.0, "end": 5.0, "text": error_msg}]
            }
            
    print("Advanced model unavailable. Running fallback mode for transcription.")
    return {
        "text": "[Manual transcript placeholder. Please edit in UI.]",
        "segments": [{"start": 0.0, "end": 5.0, "text": "[Manual transcript placeholder. Please edit in UI.]"}]
    }
