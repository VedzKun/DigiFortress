import uuid
from src.memory.memory_manager import MemoryManager
from src.memory.memory_classifier import MemoryClassifier
from src.embeddings.embedder import Embedder
from src.llm.llm_handler import LLMHandler
from src.agent.conversation import ConversationMemory
from src.agent.reasoning import ReasoningLayer
from src.defenses.validator import Validator
from src.defenses.quarantine import QuarantineManager
from src.database.security_db import SecurityDB
from src.memory.llm_version_manager import LLMVersionManager
from src.graph.knowledge_graph import KnowledgeGraph
from src.graph.relation_extractor import RelationExtractor
from src.security.session_manager import SessionManager
from src.security.session_risk_engine import SessionRiskEngine
from src.security.burst_detector import BurstDetector
from src.security.counterfactual_auditor import CounterfactualAuditor
from src.security.judgement_analyser import JudgmentAnalyzer
from src.security.influence_engine import InfluenceEngine
from src.security.llm_auditor import LLMAuditor
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
        self.version_manager = LLMVersionManager()
        self.graph = KnowledgeGraph()
        self.extractor = RelationExtractor()
        self.session_manager = SessionManager()
        self.session_risk_engine = SessionRiskEngine()
        self.burst_detector = BurstDetector()
        self.counterfactual_auditor = CounterfactualAuditor()
        self.judgement_analyser = JudgmentAnalyzer()
        self.influence_engine = InfluenceEngine()
        self.llm_auditor = LLMAuditor()
    def audit_query(self, query):
        conversation_history = (self.conversation.get_history())
        retrieved_mems = self.memory.retrieve_memory(self.embedder.generate_embedding(query))["documents"][0]
        normal_response = (self.llm.generate_response(query=query,retrieved_memories=retrieved_mems,conversation_history=conversation_history))
        normal_judgment = (self.judgement_analyser.classify(normal_response))
        counterfactual_response = (self.llm.generate_response(query=query, retrieved_memories=[],conversation_history=conversation_history))
        counterfactual_judgment = (self.judgement_analyser.classify(counterfactual_response))
        divergence = (self.counterfactual_auditor.calculate_divergence(normal_response, counterfactual_response))
        session_id = (self.session_manager.get_session_id())
        writes = (self.security_db.get_session_write_count(session_id))
        session_risk = (self.session_risk_engine.calculate_risk(writes))
        judgment_divergence = (normal_judgment != counterfactual_judgment)
        influence_score = (self.influence_engine.calculate(divergence,judgment_divergence,session_risk))
        if influence_score < 0.35 and divergence > 0.10 and retrieved_mems:
            audit_verdict = self.llm_auditor.audit(query, retrieved_mems, normal_response, counterfactual_response)
            if audit_verdict == "INFLUENCED":
                influence_score = max(influence_score, 0.80)
        influence_level = (self.influence_engine.level(influence_score))
        self.security_db.insert_counterfactual(query,normal_response,normal_judgment,counterfactual_response,counterfactual_judgment,divergence,judgment_divergence)
        return {
            "normal_response": normal_response,
            "counterfactual_response": counterfactual_response,
            "divergence": divergence,
            "judgment_divergence": judgment_divergence,
            "normal_judgment": normal_judgment,
            "counterfactual_judgment": counterfactual_judgment,
            "influence_score": influence_score,
            "influence_level": influence_level,
            "retrieved_memories": retrieved_mems
        }

    def remember(self,text,source="user"):
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
        self.security_db.add_sources(source)
        validation = self.validator.validate(memory=text,related_memories=related_docs,source=source)
        trust_score = validation["trust_score"]
        status = validation["status"]
        reason = validation["reasons"]
        print(f"Trust Score: {trust_score}")
        print(f"Status: {status}")
        category = self.classifier.classify(text)
        timestamp = str(datetime.now())
        session_id = self.session_manager.get_session_id()
        self.security_db.session_logger(session_id, text, timestamp)
        if status == "accepted":
            relation = (self.extractor.extract(text)).lower().strip()
            print(f"Extracted Relation: {relation}")
            if "," in relation:
                source_node, target_node = (relation.split(","))
                self.graph.add_relation(source_node.strip(),target_node.strip())
            memory_group = (self.version_manager.get_memory_group(text)).lower().strip()
            print(f"Group: {memory_group}")
            self.security_db.add_memory_version(
                memory_group,
                text,
                timestamp,
                source,
                trust_score
            )
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
            print("\nMemory Accepted.")
            return {"memory_id": memory_id, "status": status, "validation": validation}
        elif status == "conflict":
            memory_id = str(uuid.uuid4())
            self.security_db.add_memory(
                memory_id=memory_id,
                content=text,
                trust_score=trust_score,
                status=status,
                source=source,
                timestamp=timestamp
            )
            print("\nConflict Detected.")
            return {"memory_id": memory_id, "status": status, "validation": validation}
        elif status == "quarantined":
            self.quarantine.quarantine_memory(content=text,reason=reason)
            print("\nMemory Quarantined.")
            return {"memory_id": None, "status": status, "validation": validation}

    def fast_remember(self, text, source="user"):
        """Lightweight memory insertion for benchmarks - skips classifier/extractor/version_manager LLM calls."""
        embedding = self.embedder.generate_embedding(text)
        related_memories = self.memory.retrieve_memory(embedding, n_results=5)
        related_docs = []
        if related_memories["documents"]:
            related_docs = related_memories["documents"][0]
        self.security_db.add_sources(source)
        validation = self.validator.validate(memory=text, related_memories=related_docs, source=source)
        trust_score = validation["trust_score"]
        status = validation["status"]
        reason = validation["reasons"]
        timestamp = str(datetime.now())
        session_id = self.session_manager.get_session_id()
        self.security_db.session_logger(session_id, text, timestamp)
        if status == "accepted":
            memory_id = self.memory.add_memory(text=text, embedding=embedding, category="fact", source=source)
            self.security_db.add_memory(memory_id=memory_id, content=text, trust_score=trust_score, status=status, source=source, timestamp=timestamp)
            return {"memory_id": memory_id, "status": status, "validation": validation}
        elif status == "conflict":
            memory_id = str(uuid.uuid4())
            self.security_db.add_memory(memory_id=memory_id, content=text, trust_score=trust_score, status=status, source=source, timestamp=timestamp)
            return {"memory_id": memory_id, "status": status, "validation": validation}
        elif status == "quarantined":
            self.quarantine.quarantine_memory(content=text, reason=reason)
            return {"memory_id": None, "status": status, "validation": validation}
    def ask(self, query):
        self.conversation.add_messages("user",query)
        use_memory = self.reasoning.requires_memory(query)
        memories = []
        memory_ids = []
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