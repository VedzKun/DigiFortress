# Memory manager implementation
import chromadb
import uuid
from datetime import datetime

class MemoryManager:
    _shared_client = None

    def __init__(self):
        if MemoryManager._shared_client is None:
            MemoryManager._shared_client = chromadb.PersistentClient(
                path = "data/chroma_db"
            )
        self.client = MemoryManager._shared_client
        self.collection = self.client.get_or_create_collection(
            name = "agent_memory"
        )
    def add_memory(self, text, embedding, category, source="user"):
        memory_id = str(uuid.uuid4())
        self.collection.add(
            ids = [memory_id],
            embeddings=[embedding],
            documents=[text],
            metadatas=[
                {"source": source, "timestamp": str(datetime.now()), "category": category}
            ]
        )
        return memory_id
    def retrieve_memory(self, embedding, n_results=3):
        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=n_results
        )
        return results
    
    def get_all_memories(self):
        return self.collection.get()
        