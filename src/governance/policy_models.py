from dataclasses import dataclass
from typing import Optional

@dataclass
class Policy:
    policy_id: str
    name: str
    description: str
    action_type: str  # e.g., 'block', 'flag'
    created_at: Optional[str] = None

@dataclass
class PolicyEvaluationResult:
    is_violation: bool
    violating_policy_id: Optional[str] = None
    reason: Optional[str] = None
    action_taken: str = "allow"
