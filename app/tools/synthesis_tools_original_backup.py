import shutil
from app.services.model_registry import ModelRegistry
from app.tools.alignment_tools import align_audio_duration

def synthesize_speech(text: str, output_path: str, speaker_profile: dict, emotion: str, reference_audio_path: str = None, target_duration: float = None) -> dict:
    
    # Try ElevenLabs Voice Cloning if API key is provided
    import os
    from dotenv import load_dotenv
    load_dotenv() # Force reload of the .env file so the user doesn't need to restart the server!
    elevenlabs_key = os.environ.get("ELEVENLABS_API_KEY")
    
    if elevenlabs_key and reference_audio_path:
        try:
            print(f"Running ElevenLabs Voice Cloning to {output_path}")
            import requests
            import json
            
            headers = {
                "xi-api-key": elevenlabs_key
            }
            
            # 1. True Instant Voice Cloning with ElevenLabs API
            speaker_id = speaker_profile.get("speaker_id", "SPEAKER_00")
            voice_id = None
            
            try:
                print(f"🎙️ Cloning voice from reference audio {reference_audio_path} via ElevenLabs IVC...")
                url_clone = "https://api.elevenlabs.io/v1/voices/add"
                with open(reference_audio_path, "rb") as audio_file:
                    files_payload = [("files", (os.path.basename(reference_audio_path), audio_file, "audio/wav"))]
                    data_payload = {"name": f"Clone_{speaker_id}_{os.path.basename(reference_audio_path)}"}
                    res_clone = requests.post(url_clone, headers={"xi-api-key": elevenlabs_key}, files=files_payload, data=data_payload)
                    if res_clone.ok:
                        voice_id = res_clone.json().get("voice_id")
                        print(f"🎯 Voice Cloned Successfully! Voice ID: {voice_id}")
                    else:
                        print(f"ElevenLabs IVC failed ({res_clone.status_code}: {res_clone.text}). Falling back to standard voice.")
            except Exception as ivc_err:
                print(f"ElevenLabs IVC exception: {ivc_err}")
                
            if not voice_id:
                # Fallback to standard ElevenLabs voice mapping
                gender = speaker_profile.get("gender", "male")
                male_voices = ["pNInz6obpgDQGcFmaJgB", "VR6AewLTigWG4xSOukaG", "ErXwobaYiN019PkySvjV"]
                female_voices = ["21m00Tcm4TlvDq8ikWAM", "AZnzlk1XvdvUeBnXmlld", "EXAVITQu4vr4xnSDxMaL"]
                try:
                    speaker_idx = int(str(speaker_id).split("_")[-1])
                except:
                    speaker_idx = abs(hash(str(speaker_id)))
                voice_id = female_voices[speaker_idx % len(female_voices)] if gender == "female" else male_voices[speaker_idx % len(male_voices)]
                print(f"Using fallback ElevenLabs voice ID: {voice_id}")
                
            # 2. Generate the Hindi speech with the cloned/mapped voice ID
            url_tts = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            payload = {
                "text": text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {
                    "stability": 0.40,
                    "similarity_boost": 0.85, # High similarity boost for cloned voices
                    "style": 0.5,
                    "use_speaker_boost": True
                }
            }
            headers["Content-Type"] = "application/json"
            
            res_tts = requests.post(url_tts, headers=headers, json=payload)
            if not res_tts.ok:
                raise Exception(f"TTS failed: {res_tts.text}")
                
            # 3. Save output
            with open(output_path, "wb") as f:
                f.write(res_tts.content)
            
            # 4. Mathematically match the original speaker's exact pitch frequency gracefully
            try:
                from app.tools.alignment_tools import match_voice_frequency
                original_pitch = speaker_profile.get("median_pitch", 110.0 if gender == "male" else 190.0)
                base_pitch = 110.0 if gender == "male" else 190.0
                match_voice_frequency(output_path, original_pitch, base_pitch, output_path)
            except Exception as pitch_err:
                print(f"Skipping ElevenLabs pitch match: {pitch_err}")
            
            # 5. Align speed dynamically using librosa gracefully
            if target_duration:
                try:
                    align_audio_duration(output_path, target_duration, output_path)
                except Exception as align_err:
                    print(f"Skipping ElevenLabs speed align: {align_err}")
                
            return {
                "success": True,
                "output_path": output_path,
                "model_used": "elevenlabs_cloned"
            }
        except Exception as e:
            print(f"ElevenLabs Cloning failed: {e}")
            
    # Try AI4Bharat IndicF5 (Zero-Shot Local Indic Voice Cloning)
    if reference_audio_path and os.path.exists(reference_audio_path):
        try:
            print(f"🎙️ Attempting Zero-Shot Voice Cloning via AI4Bharat IndicF5 to {output_path}...")
            import soundfile as sf
            
            # Support both local f5_tts library and Gradio/HuggingFace API client
            try:
                from f5_tts.api import F5TTS
                if not hasattr(ModelRegistry, "_indic_f5_model"):
                    print("Loading AI4Bharat IndicF5 local weights...")
                    ModelRegistry._indic_f5_model = F5TTS(model="ai4bharat/IndicF5")
                f5_model = ModelRegistry._indic_f5_model
                wav, sr, _ = f5_model.infer(
                    ref_file=reference_audio_path,
                    ref_text="",
                    gen_text=text
                )
                sf.write(output_path, wav, sr)
            except ImportError:
                # Fallback to HuggingFace Gradio Client if local f5-tts is not installed
                from gradio_client import Client, handle_file
                client = Client("ai4bharat/IndicF5")
                result = client.predict(
                    ref_audio=handle_file(reference_audio_path),
                    ref_text="",
                    gen_text=text,
                    model="IndicF5",
                    speed=speaker_profile.get("tempo", 1.0),
                    api_name="/infer"
                )
                res_audio = result[0] if isinstance(result, tuple) else result
                shutil.copyfile(res_audio, output_path)
                
            print(f"🎯 AI4Bharat IndicF5 Voice Cloning Successful! Saved to {output_path}")
            if target_duration:
                align_audio_duration(output_path, target_duration, output_path)
            return {
                "success": True,
                "output_path": output_path,
                "model_used": "ai4bharat-indicF5-cloned"
            }
        except Exception as f5_err:
            print(f"AI4Bharat IndicF5 cloning unavailable or failed ({f5_err}). Falling back to Kokoro-TTS...")

    # Try Kokoro-TTS
    try:
        import sys, types, importlib.machinery
        if 'torchcodec' not in sys.modules or getattr(sys.modules['torchcodec'], '__spec__', None) is None:
            mock_mod = types.ModuleType('torchcodec')
            mock_mod.__spec__ = importlib.machinery.ModuleSpec('torchcodec', None)
            sys.modules['torchcodec'] = mock_mod
        if 'torchcodec.decoders' not in sys.modules or getattr(sys.modules.get('torchcodec.decoders'), '__spec__', None) is None:
            mock_dec = types.ModuleType('torchcodec.decoders')
            mock_dec.__spec__ = importlib.machinery.ModuleSpec('torchcodec.decoders', None)
            sys.modules['torchcodec.decoders'] = mock_dec
            
        from kokoro import KPipeline
        import soundfile as sf
        import numpy as np
        print(f"Generating hyper-realistic Kokoro-TTS audio to {output_path}")
        
        pipeline = KPipeline(lang_code='h')
        
        speaker_id = speaker_profile.get("speaker_id", "SPEAKER_00")
        gender = speaker_profile.get("gender", "male")
        age = speaker_profile.get("age", "adult")
        
        # Kokoro native Hindi voices
        male_voices = ["hm_omega", "hm_psi"]
        female_voices = ["hf_alpha", "hf_beta"]
        
        try:
            speaker_idx = int(speaker_id.split("_")[-1])
        except:
            speaker_idx = 0
            
        if gender == "female" or age == "child":
            voice = female_voices[speaker_idx % len(female_voices)]
        else:
            voice = male_voices[speaker_idx % len(male_voices)]
            
        # Speed adjustment based on tempo and age
        tempo_ratio = speaker_profile.get("tempo", 1.0)
        speed = tempo_ratio
        if age == "child":
            speed += 0.2
        elif age == "elderly":
            speed -= 0.2
        speed = max(0.5, min(2.0, speed))
            
        generator = pipeline(
            text, voice=voice,
            speed=speed, split_pattern=r'\n+'
        )
        
        audio_chunks = []
        for i, (gs, ps, audio) in enumerate(generator):
            audio_chunks.append(audio)
            
        if not audio_chunks:
            raise Exception("Kokoro generated no audio.")
            
        final_audio = np.concatenate(audio_chunks)
        sf.write(output_path, final_audio, 24000)
        
        # Match original pitch frequency
        from app.tools.alignment_tools import match_voice_frequency
        original_pitch = speaker_profile.get("median_pitch", 110.0 if gender == "male" else 190.0)
        base_pitch = 110.0 if gender == "male" else 190.0
        match_voice_frequency(output_path, original_pitch, base_pitch, output_path)
        
        # Align speed
        if target_duration:
            align_audio_duration(output_path, target_duration, output_path)
            
        return {
            "success": True,
            "output_path": output_path,
            "model_used": "kokoro-tts"
        }
    except Exception as e:
        print(f"Kokoro-TTS failed ({e}), falling back to Microsoft Azure Neural Voice...")
        try:
            import asyncio
            import edge_tts
            
            speaker_id = speaker_profile.get("speaker_id", "SPEAKER_00")
            gender = speaker_profile.get("gender", "male")
            
            # Dynamic Multi-Speaker Voice Selection for Azure Neural TTS
            male_voices = [
                "hi-IN-MadhurNeural",
                "en-US-BrianMultilingualNeural",
                "en-US-AndrewMultilingualNeural",
                "fr-FR-RemyMultilingualNeural"
            ]
            female_voices = [
                "hi-IN-SwaraNeural",
                "en-US-AvaMultilingualNeural",
                "en-US-EmmaMultilingualNeural",
                "fr-FR-VivienneMultilingualNeural"
            ]
            
            try:
                speaker_idx = int(speaker_id.split("_")[-1])
            except:
                speaker_idx = 0
                
            if gender == "female":
                voice = female_voices[speaker_idx % len(female_voices)]
            else:
                voice = male_voices[speaker_idx % len(male_voices)]
                
            print(f"Assigning Azure Neural Voice '{voice}' to {speaker_id} ({gender})")
                
            async def _generate():
                communicate = edge_tts.Communicate(text, voice)
                await communicate.save(output_path)
                
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(_generate())
            finally:
                loop.close()
                
            # Match original pitch frequency gracefully
            try:
                from app.tools.alignment_tools import match_voice_frequency
                original_pitch = speaker_profile.get("median_pitch", 110.0 if gender == "male" else 190.0)
                base_pitch = 110.0 if gender == "male" else 190.0
                match_voice_frequency(output_path, original_pitch, base_pitch, output_path)
            except Exception as pitch_err:
                print(f"Skipping pitch match: {pitch_err}")
            
            # Align speed gracefully
            if target_duration:
                try:
                    align_audio_duration(output_path, target_duration, output_path)
                except Exception as align_err:
                    print(f"Skipping speed align: {align_err}")
                
            return {
                "success": True,
                "output_path": output_path,
                "model_used": "azure-neural-tts"
            }
        except Exception as fallback_e:
            print(f"Azure Neural TTS failed: {fallback_e}, falling back to gTTS...")
            import gtts
            tts = gtts.gTTS(text=text, lang='hi')
            tts.save(output_path)
            return {
                "success": True,
                "output_path": output_path,
                "model_used": "google-gtts"
            }
