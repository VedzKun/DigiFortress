from src.graph.agent_network_graph import AgentNetworkGraph

class TrustNetwork:
    """Calculates trust metrics across the agent ecosystem."""

    def __init__(self, network_graph: AgentNetworkGraph):
        self.network = network_graph

    def calculate_network_trust(self) -> float:
        """Overall average trust score of all agents in the network."""
        return self.calculate_average_trust()

    def calculate_average_trust(self) -> float:
        graph = self.network.get_graph()
        if len(graph.nodes) == 0:
            return 0.0

        total_trust = 0.0
        # For each node, we grab their DB reputation. But if we want it from graph, we can use edge weights.
        # Alternatively, get it directly from the security DB.
        db = self.network.db
        count = 0
        for node in graph.nodes:
            rep_data = db.get_agent_reputation(node)
            if rep_data:
                total_trust += rep_data[0]
                count += 1
        
        return (total_trust / count) if count > 0 else 0.0

    def get_most_trusted_agents(self) -> list:
        graph = self.network.get_graph()
        agents = []
        for node in graph.nodes:
            rep = self.network.db.get_agent_reputation(node)
            if rep:
                agents.append((node, rep[0]))
        agents.sort(key=lambda x: x[1], reverse=True)
        return agents

    def get_least_trusted_agents(self) -> list:
        agents = self.get_most_trusted_agents()
        return list(reversed(agents))
