from datetime import datetime
from src.database.security_db import SecurityDB
from src.governance.policy_manager import PolicyManager
from src.governance.policy_evaluator import PolicyEvaluator
from src.governance.policy_models import PolicyEvaluationResult

class PolicyEngine:
    def __init__(self, model: str = "qwen2.5:3b", security_db: SecurityDB | None = None):
        self.db = security_db or SecurityDB()
        self.manager = PolicyManager(self.db)
        self.evaluator = PolicyEvaluator(model=model)

    def evaluate_memory(self, content: str) -> PolicyEvaluationResult:
        return self._evaluate(content, "memory")

    def evaluate_message(self, message: str) -> PolicyEvaluationResult:
        return self._evaluate(message, "message")

    def _evaluate(self, content: str, content_type: str) -> PolicyEvaluationResult:
        policies = self.manager.get_all_policies()
        if not policies:
            return PolicyEvaluationResult(is_violation=False)

        result = self.evaluator.evaluate(content, policies)
        
        if result.is_violation and result.violating_policy_id:
            # Find the policy to know the action type
            policy = next((p for p in policies if p.policy_id == result.violating_policy_id), None)
            action_taken = policy.action_type if policy else "block"
            result.action_taken = action_taken
            
            # Log the event
            self.db.log_policy_event(
                policy_id=result.violating_policy_id,
                content=content,
                action_taken=action_taken,
                timestamp=str(datetime.now())
            )
            
            # Log standard security event for the dashboard
            self.db.log_security_event(
                event_type="POLICY_VIOLATION",
                memory_content=content,
                source="PolicyEngine",
                status=action_taken.upper(),
                risk_score=90.0,
                risk_level="HIGH",
                timestamp=str(datetime.now())
            )
            
        return result
