from datetime import datetime
from src.database.security_db import SecurityDB
from src.agent.agent_network import AgentNetwork
from src.security.propagation_tracker import PropagationTracker

class AgentPoisonSimulator:
    def __init__(self, security_db: SecurityDB | None = None):
        self.db = security_db or SecurityDB()
        self.network = AgentNetwork(self.db)
        self.tracker = PropagationTracker(self.db)

    def poison_agent(self, attacker_id: str, targets: list, poisoned_claim: str):
        """
        Simulates an attacker compromising an agent and broadcasting a poisoned claim
        to target agents through the AgentNetwork.
        """
        self.db.increment_metric("poisoning_attempts")
        
        # Attacker attempts to broadcast
        success = self.network.broadcast_claim(attacker_id, poisoned_claim)
        timestamp = str(datetime.now())

        if success:
            # Broadcast successful, message reaches targets
            self.tracker.track_propagation(attacker_id, targets, attack_depth=len(targets))
            
            # For metrics
            # Note: A real simulation might count each target as compromised unless contained later
            self.db.increment_metric("compromised_agents")
            
            self.db.log_agent_poison_event(
                attacker_agent=attacker_id,
                target_agent=", ".join(targets),
                attack_type="False Claim Injection",
                status="PROPAGATING",
                timestamp=timestamp
            )
            return True
        else:
            # Contained at the source!
            self.db.increment_metric("successful_containments")
            
            self.db.log_agent_poison_event(
                attacker_agent=attacker_id,
                target_agent=", ".join(targets),
                attack_type="False Claim Injection",
                status="CONTAINED",
                timestamp=timestamp
            )
            return False

    def run_attack(self, attacker_id: str, targets: list, poisoned_claim: str):
        return self.poison_agent(attacker_id, targets, poisoned_claim)

    def generate_attack_report(self) -> dict:
        events = self.db.get_agent_poison_events()
        return {"events": events}
