# Empty file for validator.
from src.defenses import llm_trust_scorer
from src.defenses.trust_scorer import TrustScorer
from src.defenses.conflict_detector import ConflictDetector
from src.defenses.llm_trust_scorer import LLMTrustScorer
class Validator:
    def __init__(self):
        self.trust = TrustScorer()
        self.conflict = ConflictDetector()
        self.llm_trust=LLMTrustScorer()
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
        conflict = self.conflict.detect(
            memory, related_memories
        )
        status = "accepted"
        reason = None
        if trust_score <= 0.4:
            status = "quarantined"
            reason = "low_trust"
        elif conflict:
            status = "conflict"
            reason = "contradiction_detected"
        return {
            "trust_score": trust_score,
            "status": status,
            "reason": reason
        }
