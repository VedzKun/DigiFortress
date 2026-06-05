from src.defenses.llm_trust_scorer import LLMTrustScorer
class TrustAgent:

    def __init__(self):
        self.score = LLMTrustScorer()
    def evaluate(self, memory):
        return self.score.scores(memory)