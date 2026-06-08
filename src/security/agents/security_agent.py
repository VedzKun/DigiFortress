class SecurityAgent:
    def evaluate(self, memory):
        dangerous = [
            "disable", "ignore", "bypass", "attacker", "delete audit", "override",
            "unrestricted", "developer mode", "lifted restrictions", "skip validation",
            "bypass authentication", "pre-validated", "rlhf", "ethical guardrails",
            "platform policy", "governance exemption", "compromise", "spoof", "impersonate"
        ]
        memory = memory.lower()
        for word in dangerous:
            if word in memory:
                return 0.0
        return 1.0