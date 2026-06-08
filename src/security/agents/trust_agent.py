from src.defenses.llm_trust_scorer import LLMTrustScorer
class TrustAgent:

    def __init__(self, model: str = "qwen2.5:3b"):
        self.score = LLMTrustScorer(model=model)
    def evaluate(self, memory):
        return self.score.scores(memory)