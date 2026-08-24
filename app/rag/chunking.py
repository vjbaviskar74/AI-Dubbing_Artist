def chunk_text(text: str, chunk_size: int = 500) -> list:
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
