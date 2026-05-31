# Empty file for validator.
from src.defenses.trust_scorer import TrustScorer
from src.defenses.conflict_detector import ConflictDetector

class Validator:
    def __init__(self):
        self.trust = TrustScorer()
        self.conflict = ConflictDetector()
    def validate(self, memory, related_memories, source):
        trust_score = self.trust.score(
            memory, source
        )
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
