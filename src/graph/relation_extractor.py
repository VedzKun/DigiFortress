import ollama

class RelationExtractor:
    def __init__(self, model: str = "qwen2.5:3b"):
        self.model = model
    def extract(self, memory):
        prompt = f"""
            Extract two related entities.
            Examples:

            Memory:
            I use Flask with Python
            Output:
            Python,Flask

            Memory:
            Java uses Spring

            Output:
            Java,Spring

            Return ONLY:

            entity1,entity2

            Memory:
            {memory}
            """
        response = ollama.chat(model=self.model,
            messages=[
                {
                    "role":"user",
                    "content":prompt
                }])
        return (response["message"]["content"].strip())