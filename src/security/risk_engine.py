
class RiskEngine:
    def calculate_risk(self, trust_score, source_reputation, status):
        risk = 100
        risk -= (trust_score * 50)
        risk -= (source_reputation * 30)
        if status == "conflict":
            risk += 15
        elif status == "quarantined":
            risk += 25
        risk = max(0, min(100,risk))
        return risk
    
    def get_risk_level(self, risk_score):
        if risk_score >= 75:
            return "CRITICAL"
        elif risk_score>= 50:
            return "HIGH"
        elif risk_score>= 25:
            return "MODERATE"
        else:
            return "LOW"
    
  