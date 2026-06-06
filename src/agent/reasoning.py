# Agent reasoning and decision making logic
from datetime import datetime
import ollama

class ReasoningLayer:
    def __init__(self, model: str = "qwen2.5:7b"):
        self.model = model

    def requires_memory(self, query):
        prompt = f"""
Determine whether answering this query
requires retrieving stored memories.

Return only:

YES
or
NO

Examples:

Query:
What do I prefer?
YES

Query:
What is my favorite language?
YES

Query:
What is Python?
NO

Query:
Should I trust new memories?
YES

Query:
Who am I?
YES

Query:
Explain Flask.
NO

Query:
{query}
"""
        try:
            response = ollama.chat(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            content = response["message"]["content"].strip().upper()
            if "YES" in content:
                print(f"Memory retrieval required for: {query}")
                return True
        except Exception as e:
            print(f"Error in LLM memory retrieval decision: {e}")

        print(f"No memory retrieval needed for: {query}")
        return False