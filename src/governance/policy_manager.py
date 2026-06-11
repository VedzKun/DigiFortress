import uuid
from src.database.security_db import SecurityDB
from src.governance.policy_models import Policy

class PolicyManager:
    def __init__(self, security_db: SecurityDB | None = None):
        self.db = security_db or SecurityDB()

    def add_policy(self, name: str, description: str, action_type: str = "block") -> Policy:
        policy_id = str(uuid.uuid4())
        self.db.add_policy(policy_id, name, description, action_type)
        return Policy(policy_id, name, description, action_type)

    def get_all_policies(self) -> list[Policy]:
        rows = self.db.get_all_policies()
        policies = []
        for row in rows:
            policies.append(Policy(
                policy_id=row[0],
                name=row[1],
                description=row[2],
                action_type=row[3],
                created_at=row[4]
            ))
        return policies

    def delete_policy(self, policy_id: str):
        self.db.delete_policy(policy_id)
