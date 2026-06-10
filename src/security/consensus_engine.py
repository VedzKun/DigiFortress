class ConsensusEngine:
    def calculate(self,trust_score,security_score,consistency_score):
        final_score = (trust_score + security_score + consistency_score) / 3
        return final_score

    def resolve_agent_conflict(self, claims: list, reputations: dict) -> dict:
        """
        Select the winning claim based on the highest agent reputation.
        claims: list of dictionaries or objects with agent_id and claim text.
        reputations: dictionary mapping agent_id -> reputation score.
        Returns the winning claim dict.
        """
        if not claims:
            return None
        
        winner = max(claims, key=lambda c: reputations.get(c['agent_id'], 0.0))
        return winner