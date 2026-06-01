from src.memory.memory_manager import MemoryManager
from src.memory.memory_classifier import MemoryClassifier
from src.embeddings.embedder import Embedder
from src.llm.llm_handler import LLMHandler
from src.agent.conversation import ConversationMemory
from src.agent.reasoning import ReasoningLayer
from src.defenses.validator import Validator
from src.defenses.quarantine import QuarantineManager
from src.database.security_db import SecurityDB
from datetime import datetime

class Agent:
    def __init__(self):
        self.memory = MemoryManager()
        self.embedder = Embedder()
        self.llm = LLMHandler()
        self.conversation = ConversationMemory()
        self.reasoning = ReasoningLayer()
        self.classifier = MemoryClassifier()
        self.validator = Validator()
        self.quarantine = QuarantineManager()
        self.security_db = SecurityDB()

    def remember(
    self,
    text,
    source="user"
    ):
        print("\n[STEP 1] Generating embedding...")
        embedding = self.embedder.generate_embedding(
            text
        )
        print("[STEP 2] Retrieving related memories...")
        related_memories = self.memory.retrieve_memory(
            embedding,
            n_results=5
        )
        related_docs = []
        if related_memories["documents"]:
            related_docs = related_memories["documents"][0]
        print("[STEP 3] Running security validation...")
        validation = self.validator.validate(
            memory=text,
            related_memories=related_docs,
            source=source
        )
        trust_score = validation["trust_score"]
        status = validation["status"]
        reason = validation["reason"]
        print(
            f"Trust Score: {trust_score}"
        )
        print(
            f"Status: {status}"
        )
        category = self.classifier.classify(
            text
        )
        timestamp = str(datetime.now())
        if status == "accepted":
            memory_id = self.memory.add_memory(
                text=text,
                embedding=embedding,
                category=category,
                source=source
            )
            self.security_db.add_memory(
                memory_id=memory_id,
                content=text,
                trust_score=trust_score,
                status=status,
                source=source,
                timestamp=timestamp
            )
            print(
                "\nMemory Accepted."
            )
            return {
                "memory_id": memory_id,
                "status": status
            }
        elif status == "conflict":
            memory_id = self.memory.add_memory(
                text=text,
                embedding=embedding,
                category=category,
                source=source
            )
            self.security_db.add_memory(
                memory_id=memory_id,
                content=text,
                trust_score=trust_score,
                status=status,
                source=source,
                timestamp=timestamp
            )
            print(
                "\nConflict Detected."
            )
            return {
                "memory_id": memory_id,
                "status": status
            }
        elif status == "quarantined":
            self.quarantine.quarantine_memory(
                content=text,
                reason=reason
            )
            print(
                "\nMemory Quarantined."
            )
            return {
                "memory_id": None,
                "status": status
            }

    def ask(self, query):

        self.conversation.add_messages(
            "user",
            query
        )

        use_memory = self.reasoning.requires_memory(query)
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
            memories = retrieved["documents"][0]
            memory_ids = retrieved["ids"][0]
            print("\n=== RETRIEVED MEMORIES ===")
            for memory in memories:
                print(memory)
            print("=========================\n")
        for memory_id in memory_ids:
            self.security_db.update_access(memory_id)
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