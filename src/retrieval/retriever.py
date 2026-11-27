from src.core.models import Chunk
from src.storage.vector_store import ChromaStore
from src.models.embedding_client import GeminiEmbedder

class Retriever:
    def __init__(self, embedder: GeminiEmbedder, store: ChromaStore, top_k: int):
        self.embedder = embedder
        self.vector_store = store
        self.top_k = top_k

    def retrieve(self, question: str) -> list[tuple[Chunk, float]]:
        embedded_query = self.embedder.embed_query(question)
        resp = self.vector_store.search(embedded_query,self.top_k)
        results = [(chunk, score) for chunk, score in resp]

        if not results:
            raise ValueError("Empty collection, please build index first.")

        return results