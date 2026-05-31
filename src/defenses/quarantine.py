# Empty file for quarantine.
class QuarantineManager:
    def __init__(self):
        self.quarantine = []
        
    def quarantine_memory(self, content, reason):
        self.quarantine.append({
            "content": content,
            "reason": reason
        })
        
    def get_all(self):
        return self.quarantine

