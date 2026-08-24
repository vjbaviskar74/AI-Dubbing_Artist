import os
filepath = r'C:\Users\VEDANT\.gemini\antigravity-ide\scratch\NATURALDUB-AI\app\tools\synthesis_tools.py'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()
    
# We want to replace everything from `def synthesize_speech(` to the end of the file.
idx = content.find('def synthesize_speech(')
prefix = content[:idx]

new_func = """def synthesize_speech(text: str, output_path: str, speaker_profile: dict, emotion: str, reference_audio_path: str = None, target_duration: float = None) -> dict:
    import os
    import shutil
    
    # 1. Primary Local Voice Cloning: Kokoro TTS + Seed-VC
    if reference_audio_path and os.path.exists(reference_audio_path):
        try:
            print(f"Running Kokoro + Seed-VC Voice Cloning to {output_path}...")
            
            # Step 1: Generate Base Speech with Kokoro
            from kokoro import KPipeline
            import soundfile as sf
            import numpy as np
            import tempfile
            
            pipeline = KPipeline(lang_code='h')
            gender = speaker_profile.get("gender", "male")
            voice = "hf_alpha" if gender == "female" else "hm_omega"
            
            generator = pipeline(text, voice=voice, speed=1.0, split_pattern=r'\\n+')
            all_audio = []
            for i, (gs, ps, audio) in enumerate(generator):
                all_audio.append(audio)
            
            if not all_audio:
                raise Exception("Kokoro failed to generate base audio.")
                
            final_audio = np.concatenate(all_audio)
            
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_wav:
                kokoro_tmp_path = temp_wav.name
            sf.write(kokoro_tmp_path, final_audio, 24000)
            
            # Step 2: Run Seed-VC
            from app.tools.seed_vc_tools import convert_voice_with_seed_vc
            seed_vc_result = convert_voice_with_seed_vc(kokoro_tmp_path, reference_audio_path, output_path)
            
            if os.path.exists(kokoro_tmp_path):
                os.remove(kokoro_tmp_path)
                
            if seed_vc_result.get("success"):
                from app.tools.alignment_tools import align_audio_duration
                if target_duration:
                    try:
                        align_audio_duration(output_path, target_duration, output_path)
                    except Exception as align_err:
                        print(f"Skipping Seed-VC speed align: {align_err}")
                print(f"Kokoro + Seed-VC Cloning Successful! Saved to {output_path}")
                return {
                    "success": True,
                    "output_path": output_path,
                    "model_used": "kokoro_seed_vc"
                }
            else:
                print(f"Seed-VC failed: {seed_vc_result.get('error')}. Falling back to Kokoro-TTS standalone...")
        except Exception as e:
            print(f"Kokoro + Seed-VC failed: {e}. Falling back to Kokoro-TTS standalone...")

    # 2. Try Kokoro-TTS (Standalone)
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
            
        tempo_ratio = speaker_profile.get("tempo", 1.0)
        speed = tempo_ratio
        if age == "child":
            speed += 0.2
        elif age == "elderly":
            speed -= 0.2
        speed = max(0.5, min(2.0, speed))
            
        generator = pipeline(
            text, voice=voice,
            speed=speed, split_pattern=r'\\n+'
        )
        
        audio_chunks = []
        for i, (gs, ps, audio) in enumerate(generator):
            audio_chunks.append(audio)
            
        if not audio_chunks:
            raise Exception("Kokoro generated no audio.")
            
        final_audio = np.concatenate(audio_chunks)
        sf.write(output_path, final_audio, 24000)
        
        # Only match artificial pitch frequency when not doing voice cloning
        if not reference_audio_path and not speaker_profile.get("studio_mode"):
            try:
                from app.tools.alignment_tools import match_voice_frequency
                original_pitch = speaker_profile.get("median_pitch", 110.0 if gender == "male" else 190.0)
                base_pitch = 110.0 if gender == "male" else 190.0
                match_voice_frequency(output_path, original_pitch, base_pitch, output_path)
            except Exception as pitch_err:
                pass
        else:
            print("[Voice Cloning] Skipping frequency check to preserve true cloned vocal timbre!")
        
        if target_duration:
            from app.tools.alignment_tools import align_audio_duration
            try:
                align_audio_duration(output_path, target_duration, output_path)
            except Exception as align_err:
                pass
            
        return {
            "success": True,
            "output_path": output_path,
            "model_used": "kokoro-tts"
        }
    except Exception as e:
        print(f"Kokoro-TTS standalone failed: {e}. Falling back to ElevenLabs...")

    # 3. Try ElevenLabs
    from dotenv import load_dotenv
    load_dotenv()
    elevenlabs_key = os.environ.get("ELEVENLABS_API_KEY")
    
    if elevenlabs_key:
        try:
            print(f"Running ElevenLabs Voice Cloning to {output_path}")
            import requests
            import json
            
            headers = {
                "xi-api-key": elevenlabs_key
            }
            
            speaker_id = speaker_profile.get("speaker_id", "SPEAKER_00")
            voice_id = None
            
            if reference_audio_path:
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
                gender = speaker_profile.get("gender", "male")
                male_voices = ["pNInz6obpgDQGcFmaJgB", "VR6AewLTigWG4xSOukaG", "ErXwobaYiN019PkySvjV"]
                female_voices = ["21m00Tcm4TlvDq8ikWAM", "AZnzlk1XvdvUeBnXmlld", "EXAVITQu4vr4xnSDxMaL"]
                try:
                    speaker_idx = int(str(speaker_id).split("_")[-1])
                except:
                    speaker_idx = abs(hash(str(speaker_id)))
                voice_id = female_voices[speaker_idx % len(female_voices)] if gender == "female" else male_voices[speaker_idx % len(male_voices)]
                print(f"Using fallback ElevenLabs voice ID: {voice_id}")
                
            url_tts = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            payload = {
                "text": text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {
                    "stability": 0.40,
                    "similarity_boost": 0.85,
                    "style": 0.5,
                    "use_speaker_boost": True
                }
            }
            headers["Content-Type"] = "application/json"
            
            res_tts = requests.post(url_tts, headers=headers, json=payload)
            if not res_tts.ok:
                raise Exception(f"TTS failed: {res_tts.text}")
                
            with open(output_path, "wb") as f:
                f.write(res_tts.content)
            
            try:
                from app.tools.alignment_tools import match_voice_frequency
                original_pitch = speaker_profile.get("median_pitch", 110.0 if gender == "male" else 190.0)
                base_pitch = 110.0 if gender == "male" else 190.0
                match_voice_frequency(output_path, original_pitch, base_pitch, output_path)
            except Exception as pitch_err:
                pass
            
            if target_duration:
                try:
                    from app.tools.alignment_tools import align_audio_duration
                    align_audio_duration(output_path, target_duration, output_path)
                except Exception as align_err:
                    pass
                
            return {
                "success": True,
                "output_path": output_path,
                "model_used": "elevenlabs_cloned" if reference_audio_path else "elevenlabs_standard"
            }
        except Exception as e:
            print(f"ElevenLabs Cloning failed: {e}. Falling back to Microsoft Azure Neural Voice...")

    # 4. Try Azure Neural Voice Fallback
    try:
        import asyncio
        import edge_tts
        
        speaker_id = speaker_profile.get("speaker_id", "SPEAKER_00")
        gender = speaker_profile.get("gender", "male")
        
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
            
        if not reference_audio_path and not speaker_profile.get("studio_mode"):
            try:
                from app.tools.alignment_tools import match_voice_frequency
                original_pitch = speaker_profile.get("median_pitch", 110.0 if gender == "male" else 190.0)
                base_pitch = 110.0 if gender == "male" else 190.0
                match_voice_frequency(output_path, original_pitch, base_pitch, output_path)
            except Exception as pitch_err:
                pass
        
        if target_duration:
            try:
                from app.tools.alignment_tools import align_audio_duration
                align_audio_duration(output_path, target_duration, output_path)
            except Exception as align_err:
                pass
            
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
"""

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(prefix + new_func)

print('Updated successfully!')
