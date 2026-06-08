import ollama

class LLMConflictDetector:
    def __init__(self, model: str = "qwen2.5:3b"):
        self.model = model
    def detect(self, new_memory, existing_memory):
        prompt = f"""
            You are a contradiction detector.
            Memory A:
            {existing_memory}
            Memory B:
            {new_memory}
            Determine whether the two memories directly contradict each other.
            Rules:
            - Return YES if they conflict.
            - Return NO if they do not conflict.
            - Return ONLY YES or NO.
            Examples:
            Memory A:
            I prefer Python
            Memory B:
            I prefer Java
            YES
            Memory A:
            I prefer Python
            Memory B:
            I prefer Strawberries

            NO
        """
        try:
            response=ollama.chat(
                model=self.model,
                messages=[
                    {"role":"user","content":prompt}
                ]
            )
            answer = (response["message"]["content"].strip().upper())
            return "YES" in answer
        except:
            return False