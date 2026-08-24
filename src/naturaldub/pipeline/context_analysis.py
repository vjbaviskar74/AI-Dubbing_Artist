import json
from typing import List, Dict
from ..schemas.diarization import SpeakerTurn
from ..schemas.context import SceneContext
from ..providers.groq_llm import GroqLLMProvider
from ..providers.openrouter_llm import OpenRouterLLMProvider
from ..providers.gemini_llm import GeminiLLMProvider
from ..config import settings

class ContextAnalysis:
    def __init__(self):
        provider_name = settings.models.translation.provider.lower()
        model = settings.models.translation.model
        
        if provider_name == "groq":
            self.provider = GroqLLMProvider(model=model)
        elif provider_name == "gemini":
            self.provider = GeminiLLMProvider(model=model)
        else:
            self.provider = OpenRouterLLMProvider(model=model)
            
    def analyze(self, turns: List[SpeakerTurn], run_id: str) -> SceneContext:
        output_dir = settings.default.paths.absolute_path(settings.base_dir, "runs_dir") / run_id / "context"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_path = output_dir / "context.json"
        
        if output_path.exists():
            try:
                with open(output_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return SceneContext(**data)
            except Exception:
                pass
                
        transcript_text = "\n".join([f"{t.speaker_id} [{t.start:.1f}-{t.end:.1f}]: {t.source_text}" for t in turns])
        
        system_prompt = """You are an expert dialogue analyst. Read the transcript and output a JSON summarizing the scene context.
Return ONLY valid JSON matching this schema:
{
  "scene_summary": "string",
  "genre": "string",
  "tone": "string",
  "characters": {
    "SPEAKER_00": {
      "name": "string or null",
      "role": "string",
      "gender_presentation": "male, female, or unknown",
      "relationship_to_others": {"other_speaker_id": "relationship"},
      "speech_style": "string",
      "pronoun_register": "tu, tum, aap"
    }
  },
  "protected_terms": ["list of terms to not translate"],
  "translation_guidance": ["list of guidance rules"]
}"""
        
        prompt = f"Analyze this transcript:\n\n{transcript_text}"
        
        response_text = self.provider.generate(prompt=prompt, system_prompt=system_prompt)
        
        # Clean response (remove markdown code blocks if any)
        cleaned = response_text.replace("```json", "").replace("```", "").strip()
        
        try:
            data = json.loads(cleaned)
            context = SceneContext(**data)
        except json.JSONDecodeError:
            # Fallback to empty context if parsing fails
            context = SceneContext(scene_summary="Failed to parse LLM response.")
            
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(context.model_dump(), f, indent=2, ensure_ascii=False)
            
        return context
