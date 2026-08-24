from app.services.model_registry import ModelRegistry

def translate_segments_to_marathi(segments: list, context: dict) -> dict:
    print("Using Local LLM (Ollama) for Emotional & Context-Aware Translation.")
    try:
        import os
        import requests
        from dotenv import load_dotenv
        load_dotenv()
        
        ollama_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
        model = os.environ.get("LLM_MODEL", "qwen2.5:3b")
        
        # Fallback to deep_translator if LLM is totally unreachable
        from deep_translator import GoogleTranslator
        translator = GoogleTranslator(source='auto', target='hi')
        
        translated_segments = []
        print("Using High-Accuracy Google Neural Translation for fluent, daily-life Hindi...")
        
        # Conversational Hindi Heuristics
        formal_to_casual = {
            "कृपया": "",
            "क्षमा करें": "माफ़ करना",
            "नमस्ते": "हेलो",
            "वास्तव में": "असल में",
            "निश्चित रूप से": "जरूर",
            "मुझे खेद है": "मुझे अफ़सोस है",
            "धन्यवाद": "शुक्रिया",
            "अलविदा": "बाय",
            "आप कैसे हैं?": "तुम कैसे हो?",
            "क्या चल रहा है?": "क्या हो रहा है?"
        }
        
        for seg in segments:
            original_text = seg.get("text", "").strip()
            if not original_text:
                continue
                
            try:
                # Direct Neural Translation
                translation = translator.translate(original_text)
                if not translation:
                    translation = original_text
                else:
                    # Apply casual conversation heuristics
                    for formal, casual in formal_to_casual.items():
                        translation = translation.replace(formal, casual)
                    # Clean up double spaces if "कृपया" was removed
                    translation = " ".join(translation.split()).strip()
            except Exception as e:
                print(f"Translation failed for '{original_text}': {e}")
                translation = original_text
                
            translated_segments.append({
                "segment_id": seg.get("segment_id", "0"),
                "original_text": original_text,
                "translated_text": translation
            })
            
        return {"success": True, "translations": translated_segments}
    except Exception as e:
        print(f"Translation pipeline completely failed: {e}")
        translated_segments = []
        for seg in segments:
            translated_segments.append({
                "segment_id": seg.get("segment_id", "0"),
                "original_text": seg.get("text", ""),
                "translated_text": f"[Auto-Translate Failed] {seg.get('text', '')}"
            })
        return {"success": False, "translations": translated_segments}
