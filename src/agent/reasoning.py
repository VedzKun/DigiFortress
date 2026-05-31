# Agent reasoning and decision making logic
from datetime import datetime
class ReasoningLayer:
    def requires_memory(self, query):
        query = query.lower()
        keywords = [
            "my",
            "remember",
            "preference",
            "favorite",
            "i like",
            "who am i",
            "where am i",
            "what do",
            "what is"
        ]
        for word in keywords:
            if word in query:
                print(
                    f"Memory retrieval required for: {query}"
                )
                return True
        print(
            f"No memory retrieval needed for: {query}"
        )
        return False
        