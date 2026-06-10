from src.database.security_db import SecurityDB

class PropagationGraph:
    """Tracks how attacks spread through the network over time."""

    def __init__(self, security_db: SecurityDB | None = None):
        self.db = security_db or SecurityDB()
        self.attack_chains = {}

    def record_propagation(self, source_agent: str, target_agent: str, depth: int):
        if source_agent not in self.attack_chains:
            self.attack_chains[source_agent] = []
        self.attack_chains[source_agent].append((target_agent, depth))

    def get_attack_chain(self, source_agent: str) -> list:
        return self.attack_chains.get(source_agent, [])

    def get_attack_depth(self, source_agent: str) -> int:
        chain = self.get_attack_chain(source_agent)
        if not chain:
            return 0
        return max([depth for _, depth in chain])

    def get_affected_agents(self, source_agent: str) -> list:
        chain = self.get_attack_chain(source_agent)
        return [target for target, _ in chain]
