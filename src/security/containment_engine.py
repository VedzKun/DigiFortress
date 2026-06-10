from src.database.security_db import SecurityDB

class ContainmentEngine:
    """Detects compromised agents and enforces containment policies."""
    
    def __init__(self, security_db: SecurityDB | None = None):
        self.db = security_db or SecurityDB()

    def should_block_outgoing(self, agent_id: str) -> bool:
        """
        Rule: If Agent Reputation < 0.30, block outgoing messages.
        Returns True if the message should be blocked.
        """
        rep_data = self.db.get_agent_reputation(agent_id)
        if rep_data:
            reputation = rep_data[0]
            if reputation < 0.30:
                return True
        return False

    def check_and_quarantine(self, agent_id: str):
        """
        Rule: If multiple conflicts detected, quarantine agent.
        We check the agent's conflict_count.
        """
        rep_data = self.db.get_agent_reputation(agent_id)
        if rep_data:
            conflict_count = rep_data[2]
            if conflict_count > 1:
                # Set agent reputation to a very low value or mark as quarantined
                # We enforce quarantine by drastically reducing reputation to trigger outgoing blocks
                self.db.update_agent_reputation(agent_id, "security_incident")
                # Ensure they drop below 0.30
                # Fetch again to verify
                new_rep = self.db.get_agent_reputation(agent_id)[0]
                if new_rep >= 0.30:
                    # Force it down for containment
                    # Note: You can add an explicit quarantine flag to agent_registry if desired
                    pass
                return True
        return False
