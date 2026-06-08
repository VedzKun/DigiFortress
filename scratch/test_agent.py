from src.agent.agent import Agent

try:
    print("Initializing agent...")
    agent = Agent()
    print("Agent initialized.")
    # Let's bypass LLM if possible, but actually we can just see if it crashes or errors out.
    print("Test passed: Architecture load successful.")
except Exception as e:
    import traceback
    traceback.print_exc()
