# Memory classifier for categorizing semantic memories
class MemoryClassifier:
    def classify(self,text):
        text = text.lower()
        if "like" in text or "prefer" or "enjoy" or "love" or "fond of" in text:
            return "preference"
        elif "hate" or "dislike" or "don't like" or "dont like" in text:
            return "preference"
        elif "task" or "work" or "to-do" in text:
            return "task"
        elif "remember" or "recall" or "think" in text:
            return "instruction"
        else:
            return "fact"
        