class ExplanationEngine:
    def generate(self, memory, trust_score, risk_score, source_rep, llm_score, risk_level, status, conflict):
        reasons = []
        if llm_score <= 0.1:
            reasons.append("Dangerous Intrusion detected")
        if risk_level == "CRITICAL":
            reasons.append("Critical Security Risk")
        if source_rep < 0.3:
            reasons.append("Source Reputation is weak!")
        if conflict:
            reasons.append("Low trust score")
        if trust_score < 0.4:
            reasons.append("Low trust score")
        if not reasons:
            reasons.append("Memory passed all security checks")
        return reasons