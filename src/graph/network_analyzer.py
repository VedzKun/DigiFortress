import networkx as nx
from src.graph.agent_network_graph import AgentNetworkGraph

class NetworkAnalyzer:
    """Analyzes network structure to identify critical vulnerabilities."""

    def __init__(self, network_graph: AgentNetworkGraph):
        self.network = network_graph

    def find_critical_agents(self) -> list:
        """Finds agents whose removal would split the network (articulation points) or have high betweenness."""
        graph = self.network.get_graph()
        if len(graph.nodes) == 0:
            return []
        
        # Use betweenness centrality as a proxy for criticality
        bc = nx.betweenness_centrality(graph)
        sorted_bc = sorted(bc.items(), key=lambda item: item[1], reverse=True)
        return sorted_bc

    def find_isolated_agents(self) -> list:
        """Finds agents with 0 edges."""
        graph = self.network.get_graph()
        return [node for node in graph.nodes if graph.degree(node) == 0]

    def find_high_risk_agents(self) -> list:
        """Agents with high connections but low trust scores."""
        graph = self.network.get_graph()
        db = self.network.db
        high_risk = []
        for node in graph.nodes:
            if graph.degree(node) > 2:
                rep = db.get_agent_reputation(node)
                if rep and rep[0] < 0.5:
                    high_risk.append((node, rep[0]))
        return sorted(high_risk, key=lambda x: x[1])

    def find_attack_paths(self, source: str, target: str) -> list:
        """Finds shortest paths from attacker to target."""
        graph = self.network.get_graph()
        try:
            return list(nx.all_shortest_paths(graph, source, target))
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return []
