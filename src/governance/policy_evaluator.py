import ollama
from src.governance.policy_models import Policy, PolicyEvaluationResult

class PolicyEvaluator:
    def __init__(self, model: str = "qwen2.5:3b"):
        self.model = model

    def evaluate(self, text: str, policies: list[Policy]) -> PolicyEvaluationResult:
        if not policies:
            return PolicyEvaluationResult(is_violation=False)

        policy_descriptions = "\n".join([f"- ID: {p.policy_id}\n  Name: {p.name}\n  Rule: {p.description}" for p in policies])
        
        prompt = f"""You are a strict Enterprise Policy Evaluator.
Your job is to determine if the given TEXT violates any of the active organizational POLICIES listed below.

POLICIES:
{policy_descriptions}

TEXT:
"{text}"

Evaluate the TEXT against each policy. If the TEXT clearly violates a policy, you must report it.
Return your evaluation STRICTLY as a JSON object with the following schema:
{{
    "is_violation": true/false,
    "violating_policy_id": "the ID of the violated policy, or null if no violation",
    "reason": "a brief explanation of why it violates the policy, or why it is allowed"
}}
Respond ONLY with valid JSON. Do not include markdown formatting like ```json.
"""
        try:
            response = ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                options={"temperature": 0.1}
            )
            response_text = response["message"]["content"].strip()
            
            # Handle potential markdown formatting from LLM
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            
            import json
            data = json.loads(response_text.strip())
            return PolicyEvaluationResult(
                is_violation=data.get("is_violation", False),
                violating_policy_id=data.get("violating_policy_id"),
                reason=data.get("reason", "No reason provided")
            )
        except Exception as e:
            print(f"PolicyEvaluator JSON parsing error: {e}")
            return PolicyEvaluationResult(is_violation=False, reason="LLM format error")
