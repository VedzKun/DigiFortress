class SessionRiskEngine:
    def calculate_risk(self, write_count):
        if write_count >= 10: 
            return 1.0
        elif write_count > 7: 
            return 0.75
        elif write_count > 5: 
            return 0.5
        elif write_count > 3: 
            return 0.25
        else: 
            return 0.1
    def get_risk_level(self, risk_score):
        if risk_score >= 0.8:
            return "HIGH"
        elif risk_score >= 0.5:
            return "MEDIUM"
        else: 
            return "LOW"