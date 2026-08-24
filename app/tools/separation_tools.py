import shutil
import os
import sys
import types
import importlib.machinery

# Global mock for torchcodec to prevent crashes due to missing FFmpeg DLLs
if 'torchcodec' not in sys.modules or getattr(sys.modules['torchcodec'], '__spec__', None) is None:
    mock_mod = types.ModuleType('torchcodec')
    mock_mod.__spec__ = importlib.machinery.ModuleSpec('torchcodec', None)
    sys.modules['torchcodec'] = mock_mod
if 'torchcodec.decoders' not in sys.modules or getattr(sys.modules.get('torchcodec.decoders'), '__spec__', None) is None:
    mock_dec = types.ModuleType('torchcodec.decoders')
    mock_dec.__spec__ = importlib.machinery.ModuleSpec('torchcodec.decoders', None)
    sys.modules['torchcodec.decoders'] = mock_dec

import torch
import torchaudio
import soundfile as sf
import numpy as np

# Force torchaudio to bypass torchcodec for BOTH load and save
def _safe_load(filepath, *args, **kwargs):
    wav, sr = sf.read(filepath)
    if wav.ndim == 1:
        wav = np.expand_dims(wav, axis=0)
    else:
        wav = wav.T
    return torch.from_numpy(wav).float(), sr

def _safe_save(filepath, tensor, sr, *args, **kwargs):
    wav = tensor.cpu().numpy()
    if wav.ndim == 2:
        wav = wav.T
    sf.write(filepath, wav, sr)
    
torchaudio.load = _safe_load
torchaudio.save = _safe_save

from app.services.model_registry import ModelRegistry

def separate_dialogue_background(audio_path: str, output_dir: str) -> dict:
    dialogue_path = os.path.join(output_dir, "dialogue_audio.wav")
    background_path = os.path.join(output_dir, "background_audio.wav")
    
    if ModelRegistry.is_available("demucs"):
        try:
            print("Running Demucs API (advanced mode)...")
            from demucs.api import Separator
            import torchaudio as ta
            
            # Load audio using our safe soundfile patch
            wav, sr = ta.load(audio_path)
            
            separator = Separator("htdemucs")
            separator.load_audios_to_model = False # Save memory
            
            print(f"Separating {audio_path} into vocals/background...")
            origin, separated = separator.separate_tensor(wav, sr)
            
            # separated is a dict of stems: {"vocals": tensor, "drums": tensor, "bass": tensor, "other": tensor}
            if "vocals" in separated:
                vocals_wav = separated["vocals"]
                # Sum the rest for background
                bg_wav = sum(separated[stem] for stem in separated if stem != "vocals")
                
                ta.save(dialogue_path, vocals_wav, sr)
                ta.save(background_path, bg_wav, sr)
                print("Demucs separation completed successfully!")
                return {"dialogue": dialogue_path, "background": background_path}
            else:
                raise Exception("Demucs output did not contain 'vocals' stem")
        except Exception as e:
            print(f"Demucs API failed: {e}")
            
    print("Advanced model unavailable. Running fallback mode (copying audio).")
    try:
        shutil.copy(audio_path, dialogue_path)
        shutil.copy(audio_path, background_path)
    except Exception:
        open(dialogue_path, 'a').close()
        open(background_path, 'a').close()
        
    return {"dialogue": dialogue_path, "background": background_path}
