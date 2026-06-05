import networkx as nx
class KnowledgeGraph:
    def __init__(self):
        self.graph = nx.Graph()
    def add_relation(self, source, target):
        source = source.lower().strip()
        target = target.lower().strip()
        self.graph.add_node(source)
        self.graph.add_node(target)
        self.graph.add_edge(source, target)
    def get_neighbors(self,node):
        node = node.lower().strip()
        if node not in self.graph:
            return []
        return list(self.graph.neighbors(node))
    