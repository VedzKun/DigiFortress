# Memory classifier for categorizing semantic memories
import ollama

class MemoryClassifier:
    def __init__(self, model: str = "qwen2.5:3b"):
        self.model = model

    def classify(self, text):
        prompt = f"""
Classify the following memory text into exactly ONE of these categories:
- preference
- task
- instruction
- fact

Return ONLY the category name. Do not include any other text.

Memory text:
{text}
"""
        try:
            response = ollama.chat(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            content = response["message"]["content"].strip().lower()
            if content in ["preference", "task", "instruction", "fact"]:
                return content
            else:
                return "fact"
        except Exception as e:
            print(f"Error in LLM memory classification: {e}")
            return "fact"