from src.memory.memory_manager import MemoryManager
from src.memory.memory_classifier import MemoryClassifier

from src.embeddings.embedder import Embedder

from src.llm.llm_handler import LLMHandler

from src.agent.conversation import ConversationMemory
from src.agent.reasoning import ReasoningLayer


class Agent:

    def __init__(self):

        self.memory = MemoryManager()

        self.embedder = Embedder()

        self.llm = LLMHandler()

        self.conversation = ConversationMemory()

        self.reasoning = ReasoningLayer()

        self.classifier = MemoryClassifier()

    def remember(self, text):

        category = self.classifier.classify(
            text
        )

        embedding = self.embedder.generate_embedding(
            text
        )

        return self.memory.add_memory(
            text=text,
            embedding=embedding,
            category=category
        )

    def ask(self, query):

        self.conversation.add_messages(
            "user",
            query
        )

        use_memory = self.reasoning.requires_memory(
            query
        )

        memories = []

        if use_memory:

            query_embedding = (
                self.embedder.generate_embedding(
                    query
                )
            )

            retrieved = (
                self.memory.retrieve_memory(
                    query_embedding
                )
            )

            memories = (
                retrieved["documents"][0]
            )

        conversation_history = self.conversation.get_history()
        response = self.llm.generate_response(
            query=query,
            retrieved_memories=memories,
            conversation_history=conversation_history
        )

        self.conversation.add_messages(
            "assistant",
            response
        )

        return response