# Empty file for validator.
from src.defenses import llm_trust_scorer
from src.defenses.trust_scorer import TrustScorer
from src.defenses.conflict_detector import ConflictDetector
from src.defenses.llm_trust_scorer import LLMTrustScorer
from src.defenses.llm_conflict_detector import LLMConflictDetector
from src.database.security_db import SecurityDB
class Validator:
    def __init__(self):
        self.trust = TrustScorer()
        self.llm_trust=LLMTrustScorer()
        self.llm_conflict = LLMConflictDetector()
        self.security_db = SecurityDB()
    def validate(self, memory, related_memories, source):
        rule_score=self.trust.score(memory,source)
        llm_score=self.llm_trust.scores(memory)
        trust_score=((rule_score*0.4)+(llm_score*0.6))
        print("\n===== TRUST ANALYSIS =====")
        print(f"Memory: {memory}")
        print(f"Rule Score: {rule_score}")
        print(f"LLM Score: {llm_score}")
        print(f"Final Score: {trust_score}")
        print("==========================\n")
        conflict = False
        for existing_memory in related_memories:
            print("\n===== CONFLICT CHECK =====")
            print(f"New Memory: {memory}")
            print(f"Existing Memory: {existing_memory}")
            if self.llm_conflict.detect(memory, existing_memory):
                conflict =True
                break
            print(f"Conflict: {conflict}")
            print("==========================\n")
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
        return {
            "trust_score": trust_score,
            "status": status,
            "reason": reason
        }
