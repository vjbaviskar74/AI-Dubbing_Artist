import os
import json

class ArtifactService:
    @staticmethod
    def save_json(path: str, data: dict):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
            
    @staticmethod
    def load_json(path: str):
        if not os.path.exists(path):
            return {}
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
