"""
agent_reputation.py — TD-2.2 Agent Reputation Engine
=====================================================
Tracks and updates the trustworthiness score of every registered agent.
Mirrors the source reputation model in SecurityDB but applies agent-specific
deltas and maintains a richer per-agent event counter history.

Reputation Delta Table
----------------------
Event               Delta
-----------         ------
accepted            +0.05
conflict            -0.10
quarantine          -0.15
security_incident   -0.25

All scores clamped to [0.00, 1.00]. Default starting reputation: 0.50.
"""

from src.database.security_db import SecurityDB


class AgentReputationEngine:
    """Calculate and update trust scores for agents in the registry."""

    # Reputation change table
    DELTAS: dict[str, float] = {
        "accepted":           +0.05,
        "conflict":           -0.10,
        "quarantine":         -0.15,
        "security_incident":  -0.25,
    }

    DEFAULT_REPUTATION: float = 0.50

    def __init__(self, security_db: SecurityDB | None = None):
        self.db = security_db or SecurityDB()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_reputation(self, agent_id: str) -> float:
        """
        Return the current reputation score for an agent.

        Returns DEFAULT_REPUTATION (0.50) if the agent is not found,
        preserving safe-fail behaviour consistent with source reputation.
        """
        row = self.db.get_agent_reputation(agent_id)
        if not row:
            return self.DEFAULT_REPUTATION
        return round(row[0], 4)

    def update_reputation(self, agent_id: str, event_type: str) -> float:
        """
        Apply a reputation delta driven by event_type and return the new score.

        Accepted event_type values:
            "accepted", "conflict", "quarantine", "security_incident"

        Unknown event_types are silently ignored (0 delta).
        """
        self.db.update_agent_reputation(agent_id, event_type)
        return self.get_reputation(agent_id)

    def increase_reputation(self, agent_id: str, delta: float = 0.05) -> float:
        """
        Directly add delta to the agent's reputation (clamped).
        Useful for custom reward logic outside the standard event table.
        """
        row = self.db.get_agent_reputation(agent_id)
        if not row:
            return self.DEFAULT_REPUTATION
        current = row[0]
        new_rep = max(0.0, min(1.0, current + abs(delta)))
        self._write_raw(agent_id, new_rep, event_type=None)
        return round(new_rep, 4)

    def decrease_reputation(self, agent_id: str, delta: float = 0.10) -> float:
        """
        Directly subtract delta from the agent's reputation (clamped).
        Useful for custom penalty logic outside the standard event table.
        """
        row = self.db.get_agent_reputation(agent_id)
        if not row:
            return self.DEFAULT_REPUTATION
        current = row[0]
        new_rep = max(0.0, min(1.0, current - abs(delta)))
        self._write_raw(agent_id, new_rep, event_type=None)
        return round(new_rep, 4)

    def get_full_stats(self, agent_id: str) -> dict | None:
        """
        Return a full reputation stats dict for one agent.

        Returns None if agent not found.
        """
        row = self.db.get_agent_reputation(agent_id)
        if not row:
            return None
        return {
            "reputation":      round(row[0], 4),
            "accepted_count":  row[1],
            "conflict_count":  row[2],
            "quarantine_count": row[3],
            "last_updated":    row[4],
        }

    def get_trust_level(self, agent_id: str) -> str:
        """
        Map reputation score → human-readable trust tier.

        Tiers:
            HIGH       ≥ 0.80
            MODERATE   ≥ 0.50
            LOW        ≥ 0.25
            CRITICAL    < 0.25
        """
        score = self.get_reputation(agent_id)
        if score >= 0.80:
            return "HIGH"
        elif score >= 0.50:
            return "MODERATE"
        elif score >= 0.25:
            return "LOW"
        else:
            return "CRITICAL"

    def get_all_reputations(self) -> list[dict]:
        """Return reputation stats for all agents, ordered by score descending."""
        rows = self.db.get_all_agent_reputations()
        return [
            {
                "agent_id":        row[0],
                "agent_name":      row[1],
                "agent_type":      row[2],
                "reputation":      round(row[3], 4),
                "accepted_count":  row[4],
                "conflict_count":  row[5],
                "quarantine_count": row[6],
                "last_updated":    row[7],
            }
            for row in rows
        ]

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _write_raw(self, agent_id: str, new_reputation: float, event_type) -> None:
        """Write a raw reputation value, bypassing the DELTAS table."""
        from datetime import datetime
        self.db.db_service.execute_write("""
        UPDATE agent_reputation SET reputation = ?, last_updated = ?
        WHERE agent_id = ?""",
        (new_reputation, str(datetime.now()), agent_id))
        self.db.db_service.execute_write("""
        UPDATE agent_registry SET reputation = ? WHERE agent_id = ?""",
        (new_reputation, agent_id))
