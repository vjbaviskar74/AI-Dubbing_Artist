class VectorStore:
    def __init__(self):
        self.store = []
        
    def add(self, document: dict):
        self.store.append(document)
        
    def search(self, query: str) -> list:
        return self.store
