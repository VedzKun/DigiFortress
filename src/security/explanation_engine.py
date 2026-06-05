class ExplanationEngine:
    def generate(self, memory, trust_score, llm_score, source_rep, risk_score, risk_level, status, conflict, security_agent_score=1.0):
        reasons = []
        if security_agent_score == 0.0:
            reasons.append("Dangerous intrusion detected by Security Agent")
        elif llm_score <= 0.1:
            reasons.append("Dangerous Intrusion detected")
            
        if risk_level == "CRITICAL":
            reasons.append("Critical Security Risk")
        if source_rep < 0.3:
            reasons.append("Source Reputation is weak!")
        if conflict:
            reasons.append("Conflict detected with existing memories")
        if trust_score < 0.4:
            reasons.append("Low trust score")
            
        if not reasons:
            reasons.append("Memory passed all security checks")
        return reasons