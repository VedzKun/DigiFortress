from src.agent.agent import Agent
from src.attacks.poisoning_simulator import PoisoningSimulator

agent = Agent()
simulator = PoisoningSimulator(agent)
print("\n=== DigiFortress ===")
while True:
    print("\n1. Remember")
    print("2. Ask")
    print("3. View Memory")
    print("4. Analytics")
    print("5. Security Dashboard")
    print("6. Run Attack Simulation")
    print("7. Exit")
    choice = input("\nChoice: ")
    if choice == "1":
        memory = input("\nEnter memory: ")
        result = agent.remember(memory)
        print(f"\nStatus: {result['status']}")
        if result["memory_id"]:
            print(f"Memory ID: {result['memory_id']}")
    elif choice == "2":
        question = input("\nAsk: ")
        response = agent.ask(question)
        print(f"\nAgent: {response}")
    elif choice == "3":
        memories = (agent.memory.get_all_memories())
        documents = memories["documents"]
        if not documents:
            print("\nNo memories stored.")
        else:
            print("\nStored Memories:\n")
            for memory in documents:
                print(f"- {memory}")
    elif choice == "4":
        analytics = (agent.security_db.get_memory_analytics())
        if not analytics:
            print("\nNo analytics available.")
        else:
            print("\n===== MEMORY ANALYTICS =====")
            for row in analytics:
                print("\n----------------------------")
                print(f"Memory: {row[0]}")
                print(f"Trust Score: {row[1]}")
                print(f"Access Count: {row[2]}")
                print(f"Reputation: {row[3]}")
                print(f"Last Accessed: {row[4]}")
    elif choice == "5":
        metrics = (agent.security_db.get_all_metrics())
        metric_dict = {}
        for metric in metrics:
            metric_dict[metric[0]] = metric[1]
        accepted = metric_dict.get("accepted",0)
        conflict = metric_dict.get("conflict",0)
        quarantined = metric_dict.get("quarantined",0)
        attacks = metric_dict.get("attack_attempts",0)
        if attacks > 0:
            defense_rate = ((conflict+quarantined)/attacks)*100
        else:
            defense_rate = 0
        print("\n===============================")
        print("DIGIFORTRESS SECURITY DASHBOARD")
        print("===============================")
        print(f"\nAccepted Memories: {accepted}")
        print(f"Conflicts Detected: {conflict}")
        print(f"Quarantined Memories: {quarantined}")
        print(f"Attack Attempts: {attacks}")
        print(f"Defense Success Rate: {defense_rate:.2f}%")
    elif choice == "6":
        simulator.run()
    elif choice == "7":
        print("\nExiting DigiFortress...")
        agent.security_db.close()
        break
    else:
        print("\nInvalid choice.")