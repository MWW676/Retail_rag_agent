from src.core.models import Chunk
from src.storage.vector_store import ChromaStore
from src.models.embedding_client import GeminiEmbedder

class Retriever:
    def __init__(self, embedder: GeminiEmbedder, store: ChromaStore):
        self.embedder = embedder
        self.vector_store = store

    def retrieve(self, question: str, k: int=3) -> list[tuple[Chunk, float]]:
        embedded_query = self.embedder.embed_query(question)
        resp = self.vector_store.search(embedded_query,k)
        results = [(chunk, score) for chunk, score in resp]

        return results