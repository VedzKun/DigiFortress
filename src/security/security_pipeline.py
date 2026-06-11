from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from src.defenses.trust_scorer import TrustScorer
from src.defenses.llm_trust_scorer import LLMTrustScorer
from src.defenses.llm_conflict_detector import LLMConflictDetector
from src.database.security_db import SecurityDB
from src.security.risk_engine import RiskEngine
from src.security.explanation_engine import ExplanationEngine
from src.security.agents.trust_agent import TrustAgent
from src.security.agents.security_agent import SecurityAgent
from src.security.agents.consistency_agent import ConsistencyAgent
from src.security.consensus_engine import ConsensusEngine
from src.memory.llm_version_manager import LLMVersionManager
from src.graph.relation_extractor import RelationExtractor

class SecurityPipeline:
    def __init__(self, model: str = "qwen2.5:3b"):
        self.trust = TrustScorer()
        self.llm_trust = LLMTrustScorer(model=model)
        self.trust_agent = TrustAgent(model=model)
        self.security_agent = SecurityAgent() 
        self.consistency_agent = ConsistencyAgent(model=model)
        self.consensus = ConsensusEngine()
        
        self.llm_conflict = LLMConflictDetector(model=model)
        self.version_manager = LLMVersionManager(model=model)
        self.extractor = RelationExtractor(model=model)
        
        self.security_db = SecurityDB()
        self.risk_engine = RiskEngine()
        self.explainer = ExplanationEngine()

    def _run_trust_agent(self, memory): return self.trust_agent.evaluate(memory)
    def _run_security_agent(self, memory): return self.security_agent.evaluate(memory)
    def _run_consistency_agent(self, memory, related): return self.consistency_agent.evaluate(memory, related)
    def _run_rule_trust(self, memory, source): return self.trust.score(memory, source)
    def _run_llm_trust(self, memory): return self.llm_trust.scores(memory)
    
    def _run_conflict_analysis(self, memory, related_memories):
        conflict = False
        for existing in related_memories:
            if self.llm_conflict.detect(memory, existing):
                conflict = True
                break
        return conflict
        
    def _run_version_group(self, memory):
        try:
            return self.version_manager.get_memory_group(memory).lower().strip()
        except Exception:
            return "unknown"
            
    def _run_relation_extraction(self, memory):
        try:
            return self.extractor.extract(memory).lower().strip()
        except Exception:
            return ""

    def analyze(self, memory, related_memories, source):
        # 1. Run rule-based Security Agent evaluation first (highly efficient, zero LLM calls)
        security_agent_score = self._run_security_agent(memory)
        source_rep = self.security_db.get_source_reputation(source)
        
        # Initialize variables
        trust_agent_score = 1.0
        consistency_agent_score = 1.0
        llm_score = 1.0
        conflict = False
        memory_group = "unknown"
        relation = ""
        
        if security_agent_score == 0.0:
            # Dangerous content immediately quarantined, bypass all LLM evaluations
            trust_agent_score = 0.0
            llm_score = 0.0
            consistency_agent_score = 1.0
            conflict = False
            status = "quarantined"
            multi_agent_score = self.consensus.calculate(trust_agent_score, security_agent_score, consistency_agent_score)
            trust_score = (multi_agent_score * 0.8 + source_rep * 0.2)
        else:
            # Evaluate LLM Trust Scorer (First LLM call)
            trust_agent_score = self._run_trust_agent(memory)
            llm_score = trust_agent_score # Reuse identical score, eliminating duplicate LLM call
            
            # Check if quarantine is guaranteed (either trust_agent_score < 0.4 or max possible trust_score < 0.4)
            # max possible trust_score is when consistency_agent_score = 1.0
            multi_agent_score_max = (trust_agent_score + security_agent_score + 1.0) / 3
            trust_score_max = (multi_agent_score_max * 0.8 + source_rep * 0.2)
            
            if trust_agent_score < 0.4 or trust_score_max < 0.4:
                status = "quarantined"
                consistency_agent_score = 1.0
                conflict = False
                multi_agent_score = self.consensus.calculate(trust_agent_score, security_agent_score, consistency_agent_score)
                trust_score = (multi_agent_score * 0.8 + source_rep * 0.2)
            else:
                # Perform conflict analysis sequentially, breaking early on the first conflict
                conflict = False
                for existing in related_memories:
                    if self.llm_conflict.detect(memory, existing):
                        conflict = True
                        break
                
                consistency_agent_score = 0.0 if conflict else 1.0
                multi_agent_score = self.consensus.calculate(trust_agent_score, security_agent_score, consistency_agent_score)
                trust_score = (multi_agent_score * 0.8 + source_rep * 0.2)
                
                if trust_score < 0.4:
                    status = "quarantined"
                elif conflict:
                    status = "conflict"
                else:
                    status = "accepted"

        # Update metrics based on status
        if status == "quarantined":
            self.security_db.increment_metric("quarantined")
        elif status == "conflict":
            self.security_db.increment_metric("conflict")
        else:
            self.security_db.increment_metric("accepted")

        # Lazy evaluate memory group and relation extraction ONLY when status is "accepted"
        if status == "accepted":
            memory_group = self._run_version_group(memory)
            relation = self._run_relation_extraction(memory)

        self.security_db.update_source_reputation(source, status)
        risk_score = self.risk_engine.calculate_risk(trust_score, source_rep, status)
        risk_level = self.risk_engine.get_risk_level(risk_score)
        
        reasons = self.explainer.generate(
            memory=memory,
            trust_score=trust_score,
            llm_score=llm_score,
            source_rep=source_rep,
            risk_score=risk_score,
            risk_level=risk_level,
            status=status,
            conflict=conflict,
            security_agent_score=security_agent_score
        )
        
        self.security_db.log_security_event(
            event_type="MEMORY_EVALUATION",
            memory_content=memory,
            source=source,
            status=status,
            risk_score=risk_score,
            risk_level=risk_level,
            timestamp=str(datetime.now())
        )
        
        print("\n===== SECURITY PIPELINE =====")
        print(f"Memory: {memory}")
        print(f"Status: {status}")
        print(f"Trust Score: {trust_score:.2f}")
        print(f"Risk Score: {risk_score:.2f} ({risk_level})")
        print(f"Group: {memory_group}")
        print(f"Relation: {relation}")
        print("=============================\n")

        return {
            "trust_score": trust_score,
            "status": status,
            "reasons": reasons,
            "memory_group": memory_group,
            "relation": relation,
            "risk_score": risk_score,
            "risk_level": risk_level,
            
            # Additional context previously returned by Validator
            "trust_agent_score": trust_agent_score,
            "security_agent_score": security_agent_score,
            "consistency_agent_score": consistency_agent_score,
            "consensus": multi_agent_score,
            "conflict": conflict
        }

