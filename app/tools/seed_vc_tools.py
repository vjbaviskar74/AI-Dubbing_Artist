import os
import sys
import soundfile as sf
from app.services.model_registry import ModelRegistry

def convert_voice_with_seed_vc(source_audio_path: str, reference_audio_path: str, output_path: str) -> dict:
    """
    Zero-Shot Voice Conversion using Seed-VC natively.
    Takes a base synthesized TTS audio (source) and a human reference audio (target),
    and converts the timbre of the TTS audio to match the human perfectly.
    """
    print(f"Running Seed-VC Voice Conversion natively...")
    print(f"Source (Base TTS): {source_audio_path}")
    print(f"Target (Reference): {reference_audio_path}")
    
    source_audio_path = os.path.abspath(source_audio_path)
    reference_audio_path = os.path.abspath(reference_audio_path)
    output_path = os.path.abspath(output_path)
    
    seed_vc_dir = os.path.join(os.path.dirname(__file__), "..", "third_party", "seed_vc")
    
    if seed_vc_dir not in sys.path:
        sys.path.append(seed_vc_dir)
        
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        
    try:
        if not hasattr(ModelRegistry, "_seed_vc_wrapper"):
            print("[Seed-VC] Loading models into GPU memory for the first time... (This may take a minute)")
            import torch
            
            original_cwd = os.getcwd()
            os.chdir(seed_vc_dir)
            try:
                from seed_vc_wrapper import SeedVCWrapper
                ModelRegistry._seed_vc_wrapper = SeedVCWrapper()
            finally:
                os.chdir(original_cwd)
                
            print("[Seed-VC] Models loaded successfully!")
            
        wrapper = ModelRegistry._seed_vc_wrapper
        
        print("[Seed-VC] Generating voice conversion...")
        
        original_cwd = os.getcwd()
        os.chdir(seed_vc_dir)
        
        try:
            gen = wrapper.convert_voice(
                source=source_audio_path,
                target=reference_audio_path,
                diffusion_steps=25,
                length_adjust=1.0,
                inference_cfg_rate=0.7,
                f0_condition=False,
                auto_f0_adjust=False,
                pitch_shift=0,
                stream_output=False
            )
            import types
            if isinstance(gen, types.GeneratorType):
                audio_array = None
                try:
                    for _ in gen: pass
                except StopIteration as e:
                    audio_array = e.value
            else:
                audio_array = gen
        finally:
            os.chdir(original_cwd)
            
        if audio_array is None or len(audio_array) == 0:
            raise Exception("Seed-VC generated an empty audio array.")
            
        # SeedVC uses 22050Hz for non-F0 conditioning
        sr = 22050
        
        if audio_array.ndim == 2:
            audio_array = audio_array.T
            
        sf.write(output_path, audio_array, sr)
        
        print(f"Seed-VC Native Conversion successful! Output saved to {output_path}")
        return {"success": True, "output_path": output_path}
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}
