import networkx as nx
from datetime import datetime
from src.database.security_db import SecurityDB

class AgentNetworkGraph:
    """Manages the creation and persistence of the agent trust network graph."""

    def __init__(self, security_db: SecurityDB | None = None):
        self.db = security_db or SecurityDB()
        self.graph = nx.DiGraph()

    def add_agent_node(self, agent_id: str):
        if not self.graph.has_node(agent_id):
            self.graph.add_node(agent_id)

    def remove_agent_node(self, agent_id: str):
        if self.graph.has_node(agent_id):
            self.graph.remove_node(agent_id)

    def add_connection(self, source_agent: str, target_agent: str):
        """
        Creates an edge automatically on send_message(). 
        Calculates a dynamic trust score from the source's reputation.
        """
        # Fetch sender's reputation to represent current trust
        rep_data = self.db.get_agent_reputation(source_agent)
        trust_score = rep_data[0] if rep_data else 0.5
        timestamp = str(datetime.now())

        # Update Database
        self.db.add_network_edge(source_agent, target_agent, trust_score, timestamp)
        self.db.increment_metric("total_connections")

        # Update in-memory graph
        self.add_agent_node(source_agent)
        self.add_agent_node(target_agent)
        
        if self.graph.has_edge(source_agent, target_agent):
            self.graph[source_agent][target_agent]['weight'] = trust_score
            self.graph[source_agent][target_agent]['message_count'] += 1
        else:
            self.graph.add_edge(source_agent, target_agent, weight=trust_score, message_count=1)

    def remove_connection(self, source_agent: str, target_agent: str):
        if self.graph.has_edge(source_agent, target_agent):
            self.graph.remove_edge(source_agent, target_agent)

    def get_neighbors(self, agent_id: str) -> list:
        if self.graph.has_node(agent_id):
            return list(self.graph.neighbors(agent_id))
        return []

    def get_graph(self) -> nx.DiGraph:
        return self.graph

    def load_graph(self):
        """Loads edges from SQLite DB into NetworkX graph."""
        self.graph.clear()
        edges = self.db.get_network_edges()
        for edge in edges:
            src, tgt, trust, count, ts = edge
            self.add_agent_node(src)
            self.add_agent_node(tgt)
            self.graph.add_edge(src, tgt, weight=trust, message_count=count)

    def save_graph(self):
        """(Redundant if we write synchronously, but here for completeness)"""
        pass
