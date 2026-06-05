class ConsensusEngine:
    def calculate(self,trust_score,security_score,consistency_score):
        final_score = (trust_score + security_score + consistency_score) / 3
        return final_score
        