from dataclasses import dataclass, asdict
from typing import Dict, Any

@dataclass
class AgentMessage:
    """Represents a secure inter-agent message."""
    sender_id: str
    receiver_id: str
    message: str
    signature: str
    timestamp: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert the AgentMessage instance into a dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentMessage':
        """Create an AgentMessage instance from a dictionary."""
        return cls(
            sender_id=data.get('sender_id', ''),
            receiver_id=data.get('receiver_id', ''),
            message=data.get('message', ''),
            signature=data.get('signature', ''),
            timestamp=data.get('timestamp', '')
        )
