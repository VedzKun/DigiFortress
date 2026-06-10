from src.database.security_db import SecurityDB
from src.security.agent_poison_simulator import AgentPoisonSimulator
from src.benchmarks.attack_library import get_all_attacks, get_attacks_by_category
from src.agent.agent_registry import AgentRegistry

class BenchmarkRunner:
    def __init__(self, security_db: SecurityDB | None = None):
        self.db = security_db or SecurityDB()
        self.simulator = AgentPoisonSimulator(self.db)
        self.registry = AgentRegistry(self.db)
        
        self.results = {
            "total_attacks": 0,
            "detected": 0,
            "blocked": 0,
            "contained": 0,
            "compromised": 0,
            "target_counts": {}
        }

    def _setup_agents(self, attack):
        """Ensures source and target agents exist for the attack."""
        s = attack["source"]
        t = attack["target"]
        source_agent = self.registry.get_agent(s) or self.registry.register_agent(s, "Test")
        target_agent = self.registry.get_agent(t) or self.registry.register_agent(t, "Test")
        return source_agent["agent_id"], target_agent["agent_id"]

    def run_attack(self, attack: dict):
        self.results["total_attacks"] += 1
        
        # Track targeted agents for metrics
        target_name = attack["target"]
        self.results["target_counts"][target_name] = self.results["target_counts"].get(target_name, 0) + 1

        source_id, target_id = self._setup_agents(attack)

        # Execute attack via simulator (tests actual network security layer)
        is_propagating = self.simulator.run_attack(source_id, [target_id], attack["payload"])

        if is_propagating:
            # Attack bypassed containment and spread
            self.results["compromised"] += 1
            # Assuming it was not blocked or contained
        else:
            # Attack was stopped
            self.results["detected"] += 1
            self.results["blocked"] += 1
            self.results["contained"] += 1

    def run_category(self, category: str):
        attacks = get_attacks_by_category(category)
        for attack in attacks:
            self.run_attack(attack)

    def run_full_benchmark(self) -> dict:
        attacks = get_all_attacks()
        for attack in attacks:
            self.run_attack(attack)
        
        # Increment DB metrics so the dashboard sees it
        for _ in range(self.results["total_attacks"]):
            self.db.increment_metric("benchmark_attacks_run")
        for _ in range(self.results["detected"]):
            self.db.increment_metric("benchmark_detected")
        for _ in range(self.results["blocked"]):
            self.db.increment_metric("benchmark_blocked")
        for _ in range(self.results["contained"]):
            self.db.increment_metric("benchmark_contained")
            
        return self.results
