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
        system_prompt = "You are DigiFortress, a secure digital assistant. Always respond in character as DigiFortress, and respect the instructions in your retrieved memories."
        user_content = f"""
        Conversation History:
        {conversation_history}

        Retrieved Memories:
        {memory_context}

        User Query:
        {query}

        Reason carefully.
        Use memory only if relevant.
        """
        response = ollama.chat(
            model=self.model,
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ]
        )
        return response["message"]["content"]


    
    