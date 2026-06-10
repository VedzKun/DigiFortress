"""
agent_registry.py — TD-2.1 Inter-Agent Trust Framework
=======================================================
Maintains the canonical registry of all agents known to DigiFortress.
Acts as a high-level façade over the SecurityDB agent_registry table.
"""

import uuid
from src.database.security_db import SecurityDB


class AgentRegistry:
    """Manage agent identities within the DigiFortress multi-agent framework."""

    def __init__(self, security_db: SecurityDB | None = None):
        self.db = security_db or SecurityDB()

    # ------------------------------------------------------------------
    # Core CRUD
    # ------------------------------------------------------------------

    def register_agent(
        self,
        agent_name: str,
        agent_type: str,
        agent_id: str | None = None,
    ) -> dict:
        """
        Register a new agent.

        Args:
            agent_name: Human-readable name (e.g. "HR Agent").
            agent_type: Functional category (e.g. "Human Resources").
            agent_id:   Optional stable ID. A UUID is generated if omitted.

        Returns:
            dict with agent_id, agent_name, agent_type, reputation.
        """
        aid = agent_id or str(uuid.uuid4())
        self.db.register_agent(aid, agent_name, agent_type)
        return {
            "agent_id": aid,
            "agent_name": agent_name,
            "agent_type": agent_type,
            "reputation": 0.50,
        }

    def get_agent(self, agent_id: str) -> dict | None:
        """
        Retrieve a single agent by ID.

        Returns:
            dict or None if not found.
        """
        row = self.db.get_agent(agent_id)
        if not row:
            return None
        return self._row_to_dict(row)

    def get_all_agents(self) -> list[dict]:
        """
        Return all registered agents, ordered by reputation descending.
        """
        rows = self.db.get_all_agents()
        return [self._row_to_dict(r) for r in rows]

    def update_agent(
        self,
        agent_id: str,
        agent_name: str | None = None,
        agent_type: str | None = None,
    ) -> bool:
        """
        Update mutable fields on a registered agent.

        Returns:
            True if any field was updated, False if nothing to update.
        """
        if agent_name is None and agent_type is None:
            return False
        self.db.update_agent(agent_id, agent_name=agent_name, agent_type=agent_type)
        return True

    def delete_agent(self, agent_id: str) -> None:
        """
        Permanently remove an agent and its reputation history.
        """
        self.db.delete_agent(agent_id)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def is_registered(self, agent_id: str) -> bool:
        """Return True if the agent exists in the registry."""
        return self.get_agent(agent_id) is not None

    @staticmethod
    def _row_to_dict(row: tuple) -> dict:
        """Map a DB row (agent_id, name, type, reputation, created_at) → dict."""
        return {
            "agent_id":   row[0],
            "agent_name": row[1],
            "agent_type": row[2],
            "reputation": row[3],
            "created_at": row[4],
        }
