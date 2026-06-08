import ollama

class LLMVersionManager:
    def __init__(self, model: str = "qwen2.5:3b"):
        self.model = model
    def get_memory_group(self, memory):
        prompt = f"""
        You are a memory categorization system.

        Your task is to place memories into
        high-level semantic groups.

        Examples:

        Memory:
        I love Python

        Group:
        preferences

        Memory:
        I prefer Java

        Group:
        preferences

        Memory:
        My manager is John

        Group:
        personal_information

        Memory:
        Our backend uses Flask

        Group:
        technical_environment

        Memory:
        My favorite food is pizza

        Group:
        preferences

        Return ONLY the group name.

        Memory:
        {memory}

        Group:
        """
        response = ollama.chat(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return (
            response["message"]["content"]
            .strip()
            .lower()
        )