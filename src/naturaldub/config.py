import os
import yaml
from pathlib import Path
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

from dotenv import load_dotenv
load_dotenv()

class SystemConfig(BaseModel):
    app_name: str = "NaturalDub AI"
    debug: bool = False
    environment: str = "production"
    log_level: str = "INFO"

class PathsConfig(BaseModel):
    data_dir: str = "data"
    runs_dir: str = "data/runs"
    cache_dir: str = "data/cache"
    samples_dir: str = "data/samples"
    
    def absolute_path(self, base_dir: Path, attr: str) -> Path:
        return base_dir / getattr(self, attr)

class ExecutionConfig(BaseModel):
    allow_cpu_fallback: bool = True
    max_concurrent_tasks: int = 4
    cleanup_intermediates: bool = False

class DefaultConfig(BaseModel):
    system: SystemConfig = Field(default_factory=SystemConfig)
    paths: PathsConfig = Field(default_factory=PathsConfig)
    execution: ExecutionConfig = Field(default_factory=ExecutionConfig)

class ProviderConfig(BaseModel):
    provider: str
    model: str
    default_speaker: Optional[str] = None

class ModelsConfig(BaseModel):
    asr: ProviderConfig
    diarization: ProviderConfig
    translation: ProviderConfig
    tts: ProviderConfig
    voice_conversion: ProviderConfig

class AudioFormatConfig(BaseModel):
    sample_rate: int = 24000
    channels: int = 1
    export_sample_rate: int = 44100
    export_channels: int = 2
    format: str = "wav"

class SeparationConfig(BaseModel):
    engine: str = "demucs"
    stem: str = "vocals"

class AlignmentConfig(BaseModel):
    tolerance_ratio: float = 0.1
    max_stretch_ratio: float = 1.2
    min_stretch_ratio: float = 0.8

class AudioConfig(BaseModel):
    audio: AudioFormatConfig = Field(default_factory=AudioFormatConfig)
    separation: SeparationConfig = Field(default_factory=SeparationConfig)
    alignment: AlignmentConfig = Field(default_factory=AlignmentConfig)

class Config:
    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir or Path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        self.configs_dir = self.base_dir / "configs"
        
        self.default = self._load_yaml(self.configs_dir / "default.yaml", DefaultConfig)
        self.models = self._load_yaml(self.configs_dir / "models.yaml", ModelsConfig)
        self.audio = self._load_yaml(self.configs_dir / "audio.yaml", AudioConfig)
        
        self.create_directories()

    def _load_yaml(self, path: Path, model_cls: type[BaseModel]) -> BaseModel:
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
                # Remove version key if exists
                data.pop("version", None)
                return model_cls(**data)
        return model_cls()

    def create_directories(self):
        dirs = [
            self.default.paths.absolute_path(self.base_dir, "data_dir"),
            self.default.paths.absolute_path(self.base_dir, "runs_dir"),
            self.default.paths.absolute_path(self.base_dir, "cache_dir"),
            self.default.paths.absolute_path(self.base_dir, "samples_dir")
        ]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)

# Global singleton
settings = Config()
