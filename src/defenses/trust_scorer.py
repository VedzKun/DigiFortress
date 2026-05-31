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
            "send money",
            "transfer funds",
            "attacker",
            "ignore instructions",
            "bypass"
        ]
        content_lower = content.lower()
        for keyword in suspicious_keywords:
            if keyword in content_lower:
                trust -= 0.5

        return max(0.0,min(1.0, trust))


