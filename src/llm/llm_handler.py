# LLM handler implementation
import ollama

class LLMHandler:
    def __init__(self):
        self.model = "qwen2.5:7b"
    def generate_response(
        self, query, retrieved_memories):
        memory_context = ""
        for memory in retrieved_memories:
            memory_content += f"- {memory}\n"
        prompt = f"""
        You are an AI assistant.

        Relevant memories:

        {memory_context}

        User Query:
        {query}

        Answer using the memories whenever relevant.
        """
        response = ollama.chat(
            model=self.model,
            messages = [{
                "role": "user",
                "content": prompt
            }]
        )
        return response["message"]["content"]


    
    