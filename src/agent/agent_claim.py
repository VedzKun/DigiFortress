from dataclasses import dataclass, asdict
from typing import Dict, Any

@dataclass
class AgentClaim:
    """Represents a claim made by an agent to be validated."""
    agent_id: str
    claim: str
    timestamp: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentClaim':
        return cls(
            agent_id=data.get('agent_id', ''),
            claim=data.get('claim', ''),
            timestamp=data.get('timestamp', '')
        )
