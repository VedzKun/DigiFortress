# LLM handler implementation
import ollama

class LLMHandler:
    def __init__(self):
        self.model = "qwen2.5:7b"
    def generate_response(
        self, query, retrieved_memories, conversation_history):
        memory_context = ""
        for memory in retrieved_memories:
            memory_context += f"- {memory}\n"
        prompt = f"""
        You are DigiFortress.

        Conversation History:

        {conversation_history}

        Retrieved Memories:

        {memory_context}

        User Query:
        {query}

        Reason carefully.

        Use memory only if relevant.
        """
        print("\n========== PROMPT SENT TO LLM ==========")
        print(prompt)
        print("========================================\n")
        response = ollama.chat(
            model=self.model,
            messages = [{
                "role": "user",
                "content": prompt
            }]
        )
        return response["message"]["content"]


    
    