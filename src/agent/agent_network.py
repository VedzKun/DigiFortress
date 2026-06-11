from src.database.security_db import SecurityDB
from src.agent.agent_communication import AgentCommunication
from src.security.cross_agent_validator import CrossAgentValidator
from src.agent.agent_claim import AgentClaim
from src.governance.policy_engine import PolicyEngine

class AgentNetwork:
    """Central message broker for agents, validating claims across the network."""
    def __init__(self, security_db: SecurityDB | None = None):
        self.db = security_db or SecurityDB()
        self.comm = AgentCommunication(self.db)
        self.validator = CrossAgentValidator(self.db)
        self.policy_engine = PolicyEngine(security_db=self.db)
        
        # Temporary storage for broadcast claims to perform validation
        self.active_claims = []

    def broadcast_claim(self, sender_id: str, claim_text: str):
        """
        An agent broadcasts a claim to the network.
        We securely package it and add it to active claims.
        """
        # Check policy before broadcast
        policy_eval = self.policy_engine.evaluate_message(claim_text)
        if policy_eval.is_violation and policy_eval.action_taken == "block":
            print(f"Broadcast blocked by policy: {policy_eval.reason}")
            return False

        # We use a dummy 'NETWORK' receiver just for packaging, or just sign the claim
        # Actually, let's use AgentCommunication to simulate sending to 'NETWORK'
        try:
            msg = self.comm.send_message(sender_id, "NETWORK", claim_text)
            
            # Authenticate the message to ensure it's really from sender_id
            status = self.comm.receive_message(msg.to_dict())
            if status == "VALID":
                ac = AgentClaim(agent_id=sender_id, claim=claim_text, timestamp=msg.timestamp)
                self.active_claims.append(ac.to_dict())
                return True
            return False
        except ValueError as e:
            # Blocked by containment or missing key
            print(f"Broadcast blocked: {e}")
            return False

    def validate_network_claims(self) -> dict:
        """
        Runs the CrossAgentValidator on all currently active claims,
        resolves conflicts, and clears the active claims list.
        """
        result = self.validator.validate_claims(self.active_claims)
        self.active_claims.clear()
        return result
