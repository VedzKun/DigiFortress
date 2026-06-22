# Text embedder implementation

from sentence_transformers import SentenceTransformer

class Embedder:
    _shared_model = None

    def __init__(self):
        if Embedder._shared_model is None:
            Embedder._shared_model = SentenceTransformer(
                "sentence-transformers/all-MiniLM-L6-v2"
            )
        self.model = Embedder._shared_model

    def generate_embedding(self, text: str):
        return self.model.encode(text).tolist()