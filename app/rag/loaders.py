def load_glossary(file_path: str) -> list:
    import json
    import os
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []
