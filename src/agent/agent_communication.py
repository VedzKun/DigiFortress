from datetime import datetime
from src.database.security_db import SecurityDB
from src.agent.agent_authenticator import AgentAuthenticator
from src.agent.agent_message import AgentMessage
from src.agent.agent_registry import AgentRegistry
from src.security.containment_engine import ContainmentEngine
from src.graph.agent_network_graph import AgentNetworkGraph
from src.governance.policy_engine import PolicyEngine

class AgentCommunication:
    """Handles agent-to-agent communication and validation."""

    def __init__(self, security_db: SecurityDB | None = None):
        self.db = security_db or SecurityDB()
        self.registry = AgentRegistry(self.db)
        self.authenticator = AgentAuthenticator()
        self.containment = ContainmentEngine(self.db)
        self.network_graph = AgentNetworkGraph(self.db)
        self.policy_engine = PolicyEngine(security_db=self.db)

    def send_message(self, sender_id: str, receiver_id: str, message_text: str) -> AgentMessage:
        """
        Creates a securely signed message from a sender to a receiver.
        """
        # Check against enterprise policies
        policy_eval = self.policy_engine.evaluate_message(message_text)
        if policy_eval.is_violation and policy_eval.action_taken == "block":
            raise ValueError(f"Message blocked by policy: {policy_eval.reason}")

        if self.containment.should_block_outgoing(sender_id):
            raise ValueError(f"Agent {sender_id} is contained. Outgoing messages blocked.")

        secret_key = self.db.get_agent_secret(sender_id)
        if not secret_key:
            raise ValueError(f"No secret key found for sender: {sender_id}")

        # TD-2.6: Automatically create edge in the network graph
        self.network_graph.add_connection(sender_id, receiver_id)

        signature = self.authenticator.sign_message(message_text, secret_key)
        timestamp = str(datetime.now())

        return AgentMessage(
            sender_id=sender_id,
            receiver_id=receiver_id,
            message=message_text,
            signature=signature,
            timestamp=timestamp
        )

    def receive_message(self, agent_message_dict: dict) -> str:
        """
        Parses a raw message dictionary and validates it.
        """
        message = AgentMessage.from_dict(agent_message_dict)
        return self.validate_message(message)

    def validate_message(self, agent_message: AgentMessage) -> str:
        """
        Validates the signature of an incoming message and logs security events.
        """
        sender = self.registry.get_agent(agent_message.sender_id)
        timestamp = str(datetime.now())

        if not sender:
            # Sender doesn't exist
            self.db.increment_metric("unknown_agents")
            self.db.log_security_event(
                event_type="Unknown Agent",
                memory_content=agent_message.message,
                source=agent_message.sender_id,
                status="Rejected",
                risk_score=100.0,
                risk_level="CRITICAL",
                timestamp=timestamp
            )
            return "INVALID"

        secret_key = self.db.get_agent_secret(agent_message.sender_id)
        if not secret_key:
            # Sender registered but no secret key (should not happen in normal flow)
            self.db.increment_metric("auth_failed")
            return "INVALID"

        is_valid = self.authenticator.verify_message(
            message=agent_message.message,
            secret_key=secret_key,
            signature=agent_message.signature
        )

        if is_valid:
            self.db.increment_metric("auth_success")
            self.db.log_security_event(
                event_type="Successful Authentication",
                memory_content=agent_message.message,
                source=agent_message.sender_id,
                status="VALID",
                risk_score=0.0,
                risk_level="LOW",
                timestamp=timestamp
            )
            return "VALID"
        else:
            self.db.increment_metric("auth_failed")
            self.db.increment_metric("spoof_attempts")
            self.db.log_security_event(
                event_type="Spoof Attempt",
                memory_content=agent_message.message,
                source=agent_message.sender_id,
                status="INVALID",
                risk_score=90.0,
                risk_level="CRITICAL",
                timestamp=timestamp
            )
            return "INVALID"
