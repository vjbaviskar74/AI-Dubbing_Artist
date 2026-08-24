import os
from dotenv import load_dotenv
load_dotenv()
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # App
    APP_NAME: str = "NATURALDUB-AI"
    DEBUG: bool = True
    
    # DB
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./naturaldub.db")
    
    # ML Models
    ENABLE_ADVANCED_MODELS: bool = os.getenv("ENABLE_ADVANCED_MODELS", "False").lower() == "true"
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "qwen2.5:3b")
    HF_AUTH_TOKEN: str = os.getenv("HF_AUTH_TOKEN", "")
    
    # Storage Paths
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR: str = os.path.join(BASE_DIR, "data")
    ARTIFACTS_DIR: str = os.path.join(BASE_DIR, "artifacts")
    
    # Directories setup
    def create_dirs(self):
        directories = [
            os.path.join(self.DATA_DIR, "bronze"),
            os.path.join(self.DATA_DIR, "silver"),
            os.path.join(self.DATA_DIR, "gold"),
            os.path.join(self.DATA_DIR, "uploads"),
            os.path.join(self.DATA_DIR, "reference_audio"),
            os.path.join(self.DATA_DIR, "glossaries"),
            os.path.join(self.ARTIFACTS_DIR, "extracted_audio"),
            os.path.join(self.ARTIFACTS_DIR, "separated_audio"),
            os.path.join(self.ARTIFACTS_DIR, "transcripts"),
            os.path.join(self.ARTIFACTS_DIR, "translations"),
            os.path.join(self.ARTIFACTS_DIR, "generated_audio"),
            os.path.join(self.ARTIFACTS_DIR, "timelines"),
            os.path.join(self.ARTIFACTS_DIR, "mixed_audio"),
            os.path.join(self.ARTIFACTS_DIR, "final_video"),
            os.path.join(self.ARTIFACTS_DIR, "reports"),
        ]
        for d in directories:
            os.makedirs(d, exist_ok=True)

settings = Settings()
settings.create_dirs()
