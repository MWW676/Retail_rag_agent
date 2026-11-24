import os
from dotenv import load_dotenv
from pathlib import Path
from src.ingestion.loader import load_policy
from src.ingestion.chunker import chunk_documents
from src.models.embedding_client import GeminiEmbedder
from src.storage.vector_store import ChromaStore

def build_index(policy_path: Path) -> None:
    documents = load_policy(policy_path)
    chunks = chunk_documents(documents)

    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    embedder = GeminiEmbedder(api_key)
    texts = [chunk.text for chunk in chunks]
    embeddings = embedder.embed_documents(texts)

    vector_store = ChromaStore()
    vector_store.add(chunks, embeddings)


if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent
    policy_path = base_dir.parent / "data" / "policy.md"
    build_index(policy_path)
