def retrieve_context(query: str, metadata: dict) -> dict:
    # Use pgvector if configured, otherwise fallback
    return {
        "retrieved_documents": [
            {"content": "Placeholder for local JSON glossary context.", "score": 1.0}
        ],
        "context_source": "fallback_local_json"
    }
