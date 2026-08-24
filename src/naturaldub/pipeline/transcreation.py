import json
from typing import List
from pathlib import Path
from ..schemas.diarization import SpeakerTurn
from ..schemas.context import SceneContext
from ..schemas.translation import TranslatedSegment, TranslationScript
from ..providers.groq_llm import GroqLLMProvider
from ..providers.openrouter_llm import OpenRouterLLMProvider
from ..providers.gemini_llm import GeminiLLMProvider
from ..config import settings

class Transcreation:
    def __init__(self):
        provider_name = settings.models.translation.provider.lower()
        model = settings.models.translation.model
        
        if provider_name == "groq":
            self.provider = GroqLLMProvider(model=model)
        elif provider_name == "gemini":
            self.provider = GeminiLLMProvider(model=model)
        else:
            self.provider = OpenRouterLLMProvider(model=model)
            
    def translate(self, turns: List[SpeakerTurn], context: SceneContext, run_id: str) -> TranslationScript:
        output_dir = settings.default.paths.absolute_path(settings.base_dir, "runs_dir") / run_id / "translations"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_path = output_dir / "script.json"
        
        if output_path.exists():
            try:
                with open(output_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return TranslationScript(**data)
            except Exception:
                pass
                
        transcript_text = "\n".join([f"[{t.turn_id}] {t.speaker_id} ({t.duration:.1f}s): {t.source_text}" for t in turns])
        
        system_prompt = f"""You are an expert Hindi/Hinglish dubbing translator.
Scene Context:
{json.dumps(context.model_dump(), indent=2)}

Translate the dialogue into natural Hindi/Hinglish.
Keep translations proportionate to the original duration. Do NOT hallucinate extra dialogue to fill silence.

Return ONLY valid JSON matching this schema:
{{
  "segments": [
    {{
      "turn_id": integer,
      "speaker_id": "string",
      "start": float,
      "end": float,
      "source_text": "string",
      "translated_text": "string (Hindi/Hinglish)",
      "meaning_summary": "string",
      "emotion": "string",
      "delivery": "string",
      "target_duration": float,
      "estimated_duration": float,
      "timing_status": "within_limit",
      "protected_terms_used": [],
      "is_approved": false
    }}
  ]
}}"""
        
        prompt = f"Translate these turns:\n\n{transcript_text}"
        
        response_text = self.provider.generate(prompt=prompt, system_prompt=system_prompt)
        cleaned = response_text.replace("```json", "").replace("```", "").strip()
        
        try:
            data = json.loads(cleaned)
            script = TranslationScript(**data)
        except Exception as e:
            raise RuntimeError(f"Translation parsing failed: {e}\nRaw output: {cleaned}")
            
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(script.model_dump(), f, indent=2, ensure_ascii=False)
            
        return script
