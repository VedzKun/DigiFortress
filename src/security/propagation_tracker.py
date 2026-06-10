from datetime import datetime
from src.database.security_db import SecurityDB

class PropagationTracker:
    def __init__(self, security_db: SecurityDB | None = None):
        self.db = security_db or SecurityDB()

    def track_propagation(self, source_agent: str, affected_agents: list, attack_depth: int):
        """
        Logs the spread of a poisoned claim to other agents.
        """
        timestamp = str(datetime.now())
        for target in affected_agents:
            self.db.log_agent_propagation_event(
                source_agent=source_agent,
                target_agent=target,
                attack_depth=attack_depth,
                timestamp=timestamp
            )
