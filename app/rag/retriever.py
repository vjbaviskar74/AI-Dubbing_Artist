from app.rag.vector_store import VectorStore

def retrieve_context(query: str, metadata: dict) -> list:
    # Use pgvector if configured. Fallback to basic JSON.
    return [{"content": "Context placeholder", "score": 1.0}]
