# Empty file for validator.
from src.agent import reasoning
from src.defenses import llm_trust_scorer
from src.defenses.trust_scorer import TrustScorer
from src.defenses.conflict_detector import ConflictDetector
from src.defenses.llm_trust_scorer import LLMTrustScorer
from src.defenses.llm_conflict_detector import LLMConflictDetector
from src.database.security_db import SecurityDB
from src.security.risk_engine import RiskEngine
from src.security.explanation_engine import ExplanationEngine
from datetime import datetime

class Validator:
    def __init__(self):
        self.trust = TrustScorer()
        self.llm_trust=LLMTrustScorer()
        self.llm_conflict = LLMConflictDetector()
        self.security_db = SecurityDB()
        self.risk_engine = RiskEngine()
        self.explainer = ExplanationEngine()
    def validate(self, memory, related_memories, source):
        rule_score=self.trust.score(memory,source)
        llm_score=self.llm_trust.scores(memory)
        source_rep = self.security_db.get_source_reputation(source)
        trust_score=((rule_score*0.3)+(llm_score*0.5)+(source_rep*0.2))

        conflict = False
        for existing_memory in related_memories:
            if self.llm_conflict.detect(memory,existing_memory):
                conflict = True
                break
        status = "accepted"
        reason = None
        if trust_score < 0.4:
            status = "quarantined"
            self.security_db.increment_metric("quarantined")
        elif conflict:
            status = "conflict"
            self.security_db.increment_metric("conflict")
        else:
            status = "accepted"
            self.security_db.increment_metric("accepted")
        self.security_db.update_source_reputation(source, status)
        risk_score = (self.risk_engine.calculate_risk(trust_score,source_rep,status))
        risk_level = (self.risk_engine.get_risk_level(risk_score))
        reasons = (self.explainer.generate(memory, trust_score, llm_score, source_rep, risk_score, risk_level, status, conflict))
        self.security_db.log_security_event(
            event_type="MEMORY_EVALUATION",
            memory_content=memory,
            source=source,
            status=status,
            risk_score=risk_score,
            risk_level=risk_level,
            timestamp=str(datetime.now())
        )
        print("\n===== TRUST ANALYSIS =====")
        print(f"Memory: {memory}")
        print(f"Rule Score: {rule_score}")
        print(f"LLM Score: {llm_score}")
        print(f"Final Score: {trust_score}")
        print("==========================\n")
        print("\n===== RISK ANALYSIS =====")
        print(f"Risk Score: {risk_score}")
        print(f"Risk Level: {risk_level}")
        print("\n===== SECURITY EXPLANATION =====")
        for reason in reasons:
            print(f"- {reason}")
            
        return {
            "trust_score": trust_score,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "status": status,
            "reasons": reasons
        }
