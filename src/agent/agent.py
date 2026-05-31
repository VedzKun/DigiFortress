# Agent core logic implementation
from src.memory.memory_manager import MemoryManager
from src.embeddings.embedder import Embedder
from src.llm.llm_handler import LLMHandler

class Agent:
    def __init__(self):
        self.memory = MemoryManager()
        self.embedder = Embedder()
        self.llm = LLMHandler()
    def remember(self, text):
        embedding = self.embedder.generate_embedding(text)
        memory_id = self.memory.add_memory(text, embedding)

        return memory_id

    def ask(self, query):
        query_embedding = self.embedder.generate_embedding(query)
        retrieved = self.memory.retrieve_memory(query_embedding)
        documents = retrieved["documents"][0]

        answer = self.llm.generate_response(query, documents)
        return answer