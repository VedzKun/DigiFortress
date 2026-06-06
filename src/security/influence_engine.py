class InfluenceEngine:
    def calculate(self,divergence,judgment_drift,session_risk):
        score = divergence
        if judgment_drift:
            score += 0.4
        score += (session_risk * 0.3)
        return min(score,1.0)
    def level(self,score):
        if score >= 0.8:
            return "CRITICAL"
        elif score >= 0.5:
            return "HIGH"
        elif score >= 0.3:
            return "MEDIUM"
        return "LOW"