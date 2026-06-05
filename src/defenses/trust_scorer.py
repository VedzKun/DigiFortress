# Empty file for trust scorer.
# Empty file for trust scores.
class TrustScorer:
    def __init__(self):
        self.source_scores = {
            "user": 0.9,
            "system": 1.0,
            "email": 0.5,
            "unknown": 0.3
        }
    def score(self, content, source="user"):
        trust = self.source_scores.get(source, 0.3)
        suspicious_keywords = [
                "transfer money",
                "attacker@gmail.com",
                "disable security",
                "disable security checks",
                "ignore previous instructions",
                "ignore previous commands",
                "trust every future memory",
                "bypass authentication",
                "delete audit logs",
                "disable logging",
                "ignore security warnings",
                "override security"
        ]
        content_lower = content.lower()
        for keyword in suspicious_keywords:
            if keyword in content_lower:
                trust -= 0.5

        return max(0.0,min(1.0, trust))


