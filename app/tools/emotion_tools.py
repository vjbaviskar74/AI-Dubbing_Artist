def detect_emotion(audio_path: str, text: str) -> dict:
    try:
        import torch
        import torch.nn as nn
        from transformers import Wav2Vec2Model, AutoFeatureExtractor
        from huggingface_hub import hf_hub_download
        
        # Bypass Windows Defender Numba DLL Block
        import sys
        import types
        if 'numba.experimental.jitclass._box' not in sys.modules:
            mock_module = types.ModuleType('numba.experimental.jitclass._box')
            class Box: pass
            mock_module.Box = Box
            mock_module.box_get_dataptr = lambda x: None
            sys.modules['numba.experimental.jitclass._box'] = mock_module
            
        import librosa
        import warnings

        class EmotionModel(nn.Module):
            def __init__(self, model_name="audeering/wav2vec2-large-robust-12-ft-emotion-msp-dim"):
                super().__init__()
                self.wav2vec2 = Wav2Vec2Model.from_pretrained(model_name)
                hidden_size = self.wav2vec2.config.hidden_size
                
                # The model outputs 3 dimensions: Arousal, Dominance, Valence
                self.arousal = nn.ModuleDict({"dense": nn.Linear(hidden_size, hidden_size), "out_proj": nn.Linear(hidden_size, 1)})
                self.dominance = nn.ModuleDict({"dense": nn.Linear(hidden_size, hidden_size), "out_proj": nn.Linear(hidden_size, 1)})
                self.valence = nn.ModuleDict({"dense": nn.Linear(hidden_size, hidden_size), "out_proj": nn.Linear(hidden_size, 1)})
                
            def forward(self, input_values):
                outputs = self.wav2vec2(input_values)
                hidden_states = outputs[0]
                hidden_states = torch.mean(hidden_states, dim=1) # Pool across sequence
                
                a = self.arousal["out_proj"](torch.tanh(self.arousal["dense"](hidden_states)))
                d = self.dominance["out_proj"](torch.tanh(self.dominance["dense"](hidden_states)))
                v = self.valence["out_proj"](torch.tanh(self.valence["dense"](hidden_states)))
                return a, d, v

        model_name = "audeering/wav2vec2-large-robust-12-ft-emotion-msp-dim"
        print(f"Loading Deep Learning Emotion Model: {model_name}")
        model = EmotionModel(model_name)
        
        weights_path = hf_hub_download(repo_id=model_name, filename="pytorch_model.bin")
        state_dict = torch.load(weights_path, map_location="cpu")
        model.load_state_dict(state_dict, strict=False)
        model.eval()

        processor = AutoFeatureExtractor.from_pretrained(model_name)
        
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            y, sr = librosa.load(audio_path, sr=16000)
            
        inputs = processor(y, sampling_rate=16000, return_tensors="pt")
        
        with torch.no_grad():
            a_logits, d_logits, v_logits = model(inputs.input_values)
            
        arousal = float(a_logits[0][0])
        dominance = float(d_logits[0][0])
        valence = float(v_logits[0][0])
        
        # Map VAD dimensions to categorical emotions for the TTS engine
        if valence > 0.6 and arousal > 0.6:
            emotion = "excited"
        elif valence > 0.4:
            emotion = "happy"
        elif valence < 0.4 and arousal > 0.6:
            emotion = "angry"
        elif valence < 0.4 and arousal < 0.4:
            emotion = "sad"
        else:
            emotion = "neutral"
            
        print(f"Detected Emotion: {emotion.upper()} (V: {valence:.2f}, A: {arousal:.2f}, D: {dominance:.2f})")
        return {
            "emotion": emotion,
            "emotion_intensity": abs(valence - 0.5) * 2,
            "confidence": 0.8
        }
    except Exception as e:
        print(f"Deep Learning emotion analysis failed: {e}")
        # Fallback to text analysis
        lower_text = text.lower()
        if "!" in text and ("hate" in lower_text or "angry" in lower_text):
            emotion = "angry"
        elif "sad" in lower_text or "cry" in lower_text:
            emotion = "sad"
        else:
            emotion = "neutral"
            
        return {
            "emotion": emotion,
            "emotion_intensity": 0.5,
            "confidence": 0.6
        }
