# Memory manager implementation
import chromadb
import uuid
from datetime import datetime

class MemoryManager:
    def __init__(self):
        self.client = chromadb.PersistentClient(
            path = "data/chroma_db"
        )
        self.collection = self.client.get_or_create_collection(
            name = "agent_memory"
        )
    def add_memory(self, text, embedding, source="user"):
        memory_id = str(uuid.uuid64())
        self.collection.add(
            ids = [memory_id],
            embeddings=[embedding],
            documents=[text],
            metadatas=[
                {"source": source, "timestamp": str(datetime.now())}
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
        