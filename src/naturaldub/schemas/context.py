from typing import Dict, List, Optional
from pydantic import BaseModel

class CharacterContext(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    gender_presentation: str = "unknown"
    relationship_to_others: Dict[str, str] = {}
    speech_style: Optional[str] = None
    pronoun_register: Optional[str] = None

class SceneContext(BaseModel):
    scene_summary: str = ""
    genre: str = ""
    tone: str = ""
    characters: Dict[str, CharacterContext] = {}
    protected_terms: List[str] = []
    translation_guidance: List[str] = []
