import networkx as nx
from src.graph.agent_network_graph import AgentNetworkGraph

class InfluenceTracker:
    """Measures agent influence in the network."""

    def __init__(self, network_graph: AgentNetworkGraph):
        self.network = network_graph

    def calculate_influence(self) -> dict:
        """Calculates degree centrality for all agents."""
        graph = self.network.get_graph()
        if len(graph.nodes) == 0:
            return {}
        return nx.degree_centrality(graph)

    def get_top_influencers(self) -> list:
        """Returns list of agents sorted by highest influence."""
        influence_scores = self.calculate_influence()
        sorted_influencers = sorted(influence_scores.items(), key=lambda item: item[1], reverse=True)
        return sorted_influencers

    def get_influence_score(self, agent_id: str) -> float:
        influence_scores = self.calculate_influence()
        return influence_scores.get(agent_id, 0.0)
