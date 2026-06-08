from src.defenses.llm_conflict_detector import LLMConflictDetector
class ConsistencyAgent:
    def __init__(self, model: str = "qwen2.5:3b"):
        self.detector = LLMConflictDetector(model=model)
    def evaluate(self,memory,related_memories):
        for existing in related_memories:
            if self.detector.detect(memory,existing):
                return 0.0
        return 1.0