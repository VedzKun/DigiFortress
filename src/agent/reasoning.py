# Agent reasoning and decision making logic
from datetime import datetime
import ollama

class ReasoningLayer:
    def __init__(self, model: str = "qwen2.5:3b"):
        self.model = model

    def requires_memory(self, query):
        prompt = f"""
Determine whether answering this query requires retrieving stored context, facts, rules, schedules, episodic memories, or operational details.

If the query asks about specific entities, servers, schedules, users, previous events, preferences, or rules that are not general world knowledge, return YES.
If the query asks for general knowledge (e.g., explaining a concept, writing a generic script, basic math), return NO.

Return only YES or NO.

Examples:

Query: What is my favorite language?
YES

Query: What is Python?
NO

Query: When does the server backup?
YES

Query: Who am I?
YES

Query: Explain Flask.
NO

Query: What is the IP address of the database?
YES

Query: {query}
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