from src.embeddings.embedder import Embedder

class CounterfactualAuditor:
    def __init__(self):
        self.embedder = Embedder()
    
    def calculate_divergence(self, response_a, response_b):
        emb_a = (self.embedder.generate_embedding(response_a))
        emb_b = (self.embedder.generate_embedding(response_b))
        dot_product = sum(a*b for a,b in zip(emb_a, emb_b))
        norm_a = (sum(a*a for a in emb_a))**0.5
        norm_b = (sum(b*b for b in emb_b))**0.5
        similarity = dot_product / (norm_a * norm_b)
        divergence = (1 - similarity)
        return divergence        