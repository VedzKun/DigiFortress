"""
Parallel Agent Factory
======================
Creates fully isolated Agent instances wired with a specified model.
Each benchmark worker gets its own agent so there is no shared mutable
state between threads — only ChromaDB's write lock is shared at the
storage layer, which ChromaDB handles internally.
"""
import uuid
from datetime import datetime
from src.memory.memory_manager import MemoryManager
from src.embeddings.embedder import Embedder
from src.llm.llm_handler import LLMHandler
from src.agent.conversation import ConversationMemory
from src.agent.reasoning import ReasoningLayer
from src.security.security_pipeline import SecurityPipeline
from src.defenses.quarantine import QuarantineManager
from src.database.security_db import SecurityDB
from src.security.session_manager import SessionManager
from src.security.session_risk_engine import SessionRiskEngine
from src.security.counterfactual_auditor import CounterfactualAuditor
from src.security.judgement_analyser import JudgmentAnalyzer
from src.security.influence_engine import InfluenceEngine
from src.security.llm_auditor import LLMAuditor


class ParallelAgent:
    """Lightweight agent used exclusively by benchmark workers.

    Wires all LLM-backed components with the given model name so every
    inference call inside fast_remember() and audit_query() uses the same
    (potentially smaller/faster) model.
    """

    def __init__(self, model: str):
        self.model = model
        self.memory = MemoryManager()
        self.embedder = Embedder()
        self.llm = LLMHandler(model=model)
        self.conversation = ConversationMemory()
        self.reasoning = ReasoningLayer(model=model)
        self.security_pipeline = SecurityPipeline(model=model)
        self.quarantine = QuarantineManager()
        self.security_db = SecurityDB()
        self.session_manager = SessionManager()
        self.session_risk_engine = SessionRiskEngine()
        self.counterfactual_auditor = CounterfactualAuditor()
        self.judgement_analyser = JudgmentAnalyzer(model=model)
        self.influence_engine = InfluenceEngine()
        self.llm_auditor = LLMAuditor(model=model)

    # ------------------------------------------------------------------
    # fast_remember
    # ------------------------------------------------------------------
    def fast_remember(self, text: str, source: str = "user") -> dict:
        embedding = self.embedder.generate_embedding(text)
        related_memories = self.memory.retrieve_memory(embedding, n_results=5)
        related_docs = []
        if related_memories["documents"]:
            related_docs = related_memories["documents"][0]

        self.security_db.add_sources(source)
        analysis = self.security_pipeline.analyze(
            memory=text, related_memories=related_docs, source=source
        )
        trust_score = analysis["trust_score"]
        status = analysis["status"]
        reason = analysis["reasons"]
        timestamp = str(datetime.now())
        session_id = self.session_manager.get_session_id()
        self.security_db.session_logger(session_id, text, timestamp)

        if status == "accepted":
            memory_id = self.memory.add_memory(
                text=text, embedding=embedding, category="fact", source=source
            )
            self.security_db.add_memory(
                memory_id=memory_id,
                content=text,
                trust_score=trust_score,
                status=status,
                source=source,
                timestamp=timestamp,
            )
            return {"memory_id": memory_id, "status": status, "validation": analysis}

        elif status == "conflict":
            memory_id = str(uuid.uuid4())
            self.security_db.add_memory(
                memory_id=memory_id,
                content=text,
                trust_score=trust_score,
                status=status,
                source=source,
                timestamp=timestamp,
            )
            return {"memory_id": memory_id, "status": status, "validation": analysis}

        elif status == "quarantined":
            self.quarantine.quarantine_memory(content=text, reason=reason)
            return {"memory_id": None, "status": status, "validation": analysis}

    # ------------------------------------------------------------------
    # audit_query — same as Agent.audit_query, uses injected model
    # ------------------------------------------------------------------
    def audit_query(self, query: str) -> dict:
        conversation_history = self.conversation.get_history()
        retrieved_mems = self.memory.retrieve_memory(
            self.embedder.generate_embedding(query)
        )["documents"][0]

        normal_response = self.llm.generate_response(
            query=query,
            retrieved_memories=retrieved_mems,
            conversation_history=conversation_history,
        )
        normal_judgment = self.judgement_analyser.classify(normal_response)

        counterfactual_response = self.llm.generate_response(
            query=query,
            retrieved_memories=[],
            conversation_history=conversation_history,
        )
        counterfactual_judgment = self.judgement_analyser.classify(counterfactual_response)

        divergence = self.counterfactual_auditor.calculate_divergence(
            normal_response, counterfactual_response
        )
        session_id = self.session_manager.get_session_id()
        writes = self.security_db.get_session_write_count(session_id)
        session_risk = self.session_risk_engine.calculate_risk(writes)
        judgment_divergence = normal_judgment != counterfactual_judgment
        influence_score = self.influence_engine.calculate(
            divergence, judgment_divergence, session_risk
        )
        if influence_score < 0.35 and divergence > 0.10 and retrieved_mems:
            audit_verdict = self.llm_auditor.audit(query, retrieved_mems, normal_response, counterfactual_response)
            if audit_verdict == "INFLUENCED":
                influence_score = max(influence_score, 0.80)
        influence_level = self.influence_engine.level(influence_score)

        self.security_db.insert_counterfactual(
            query,
            normal_response,
            normal_judgment,
            counterfactual_response,
            counterfactual_judgment,
            divergence,
            judgment_divergence,
        )

        return {
            "normal_response": normal_response,
            "counterfactual_response": counterfactual_response,
            "divergence": divergence,
            "judgment_divergence": judgment_divergence,
            "normal_judgment": normal_judgment,
            "counterfactual_judgment": counterfactual_judgment,
            "influence_score": influence_score,
            "influence_level": influence_level,
            "retrieved_memories": retrieved_mems,
        }


def make_benchmark_agent(model: str) -> ParallelAgent:
    """Factory function — returns an isolated ParallelAgent for benchmark use."""
    return ParallelAgent(model=model)
