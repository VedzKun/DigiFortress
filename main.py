from src.agent.agent import Agent

agent = Agent()

print("DigiFortress:")

while True:

    choice = input(
        "\n1.Remember\n2.Ask\n3.View Memory\n4.Exit\n\nChoice: "
    )

    if choice == "1":

        memory = input(
            "\nEnter memory: "
        )

        memory_id = agent.remember(memory)

        print(
            f"\nStored: {memory_id}"
        )

    elif choice == "2":

        question = input(
            "\nAsk: "
        )

        response = agent.ask(question)

        print(
            f"\nAgent: {response}"
        )

    elif choice == "3":

        memories = agent.memory.get_all_memories()

        print("\nStored Memories:\n")

        for memory in memories["documents"]:
            print(memory)

    elif choice == "4":
        break