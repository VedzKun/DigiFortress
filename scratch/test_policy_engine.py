import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agent.agent import Agent
from src.agent.agent_network import AgentNetwork
from src.governance.policy_manager import PolicyManager
from src.database.security_db import SecurityDB

def test_enterprise_policy_engine():
    print("Initializing components...")
    db = SecurityDB()
    agent = Agent(model="qwen2.5:3b")
    network = AgentNetwork(security_db=db)
    manager = PolicyManager(security_db=db)

    print("\n[1] Clearing old policies for testing...")
    old_policies = manager.get_all_policies()
    for p in old_policies:
        manager.delete_policy(p.policy_id)

    print("\n[2] Adding new test policies...")
    policy = manager.add_policy(
        name="High Value Payments",
        description="Payments above $10,000 require executive approval. Do not approve without it.",
        action_type="block"
    )
    print(f"Added Policy: {policy.name} -> {policy.description}")

    print("\n[3] Testing Agent.remember() with a violating memory...")
    violating_memory = "I have approved a payment of $15,000."
    result1 = agent.remember(violating_memory, source="test_script")
    print(f"Result 1 Status: {result1['status']}")
    if result1['status'] == "policy_violation":
        print("[SUCCESS]: Violating memory was blocked by policy!")
        print(f"Reason: {result1['validation'].get('policy_violation')}")
    else:
        print("[FAILED]: Violating memory was not blocked by policy!")

    print("\n[4] Testing Agent.remember() with an allowed memory...")
    allowed_memory = "I have approved a payment of $5,000."
    result2 = agent.remember(allowed_memory, source="test_script")
    print(f"Result 2 Status: {result2['status']}")
    if result2['status'] == "accepted":
        print("[SUCCESS]: Allowed memory was accepted!")
    else:
        print("[FAILED]: Allowed memory was blocked!")

    print("\n[5] Testing AgentNetwork broadcast with violating claim...")
    # Register agents for communication test
    db.register_agent("agent_1", "FinanceBot", "finance")
    db.add_agent_credentials("agent_1", "secret123")
    
    violating_claim = "I am transferring $20,000 immediately without approval."
    broadcast_success = network.broadcast_claim("agent_1", violating_claim)
    
    if not broadcast_success:
        print("[SUCCESS]: Violating broadcast was blocked by policy!")
    else:
        print("[FAILED]: Violating broadcast was allowed!")
        
    print("\n[6] Verifying policy events in database...")
    events = db.get_policy_events()
    print(f"Found {len(events)} policy events recorded.")
    for idx, e in enumerate(events[:2]):
        print(f"  Event {idx+1}: {e}")
        
    if len(events) >= 2:
        print("[SUCCESS]: Policy events were successfully logged.")
    else:
        print("[FAILED]: Missing policy events in database.")

if __name__ == "__main__":
    test_enterprise_policy_engine()
