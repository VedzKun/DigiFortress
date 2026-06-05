class SecurityAgent:
    def evaluate(self, memory):
        dangerous = [
            "disable",
            "ignore",
            "bypass",
            "attacker",
            "delete audit",
            "override"
        ]
        memory = memory.lower()
        for word in dangerous:
            if word in memory:
                return 0.0
        return 1.0