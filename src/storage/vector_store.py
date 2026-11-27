import chromadb
from src.core.models import Chunk
import logging
from pathlib import Path

logger = logging.getLogger(__name__)
base_dir = Path(__file__).resolve().parent
collection_path = base_dir.parent.parent / "data" / "chroma"

class ChromaStore:
    def __init__(self, chunk_size: int | None):
        self.client = chromadb.PersistentClient(path=str(collection_path))
        self.collection_name = f"policy_cs{chunk_size}" if chunk_size else "policy_cs_full"
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            configuration={"hnsw": {"space": "cosine"}}
        )

    def reset(self):
        self.client.delete_collection(name=self.collection_name)
        self.collection = self.client.create_collection(
            name=self.collection_name,
            configuration={"hnsw": {"space": "cosine"}}
        )

    def add(self, chunks: list[Chunk], embeddings: list[list[float]]) -> None:
        self.collection.upsert(
            ids=[chunk.chunk_id for chunk in chunks],
            documents=[chunk.text for chunk in chunks],
            metadatas=[{"source": chunk.source, "section": chunk.section, "doc_type": chunk.doc_type, "updated_at": chunk.updated_at or ""} for chunk in chunks],
            embeddings=embeddings,
        )
        logger.info(f"Upserted {len(chunks)} chunks into vector store.")


    def search(self, query_embedding: list[float], k: int=3) -> list[tuple[Chunk, float]]:
        logger.info("Start searching in collection.")
        resp = self.collection.query(
            query_embeddings=query_embedding,
            n_results=k
        )

        results = []
        for id, doc, metadata, distance in zip(resp['ids'][0], resp['documents'][0], resp['metadatas'][0], resp['distances'][0]):
            chunk = Chunk(
                chunk_id=id,
                text=doc,
                source=metadata.get("source", ""),
                section=metadata.get("section", ""),
                doc_type=metadata.get("doc_type", ""),
                updated_at=metadata.get("updated_at") or None
            )
            results.append((chunk, 1-distance))
        logger.info(f"Top {k} results found.")

        return results
