import os
import logging
from dotenv import load_dotenv
from pathlib import Path
from src.core.config import load_config
from src.ingestion.loader import load_policy, load_articles
from src.ingestion.chunker import chunk_documents
from src.models.embedding_client import GeminiEmbedder
from src.storage.vector_store import ChromaStore

logging.basicConfig(level=logging.INFO)

def build_index(doc_path: list[tuple[Path, str]], api_key: str, embedding_model: str, chunk_size: int) -> None:
    chunks = []
    for path, doc_type in doc_path:
        doc = load_policy(path) if doc_type == "policy" else load_articles(path)
        results = chunk_documents(doc, chunk_size)
        print(f"Chunk size:{chunk_size}, chunk counts:{len(results)}")
        chunks.extend(results)

    embedder = GeminiEmbedder(api_key, embedding_model)
    texts = [chunk.text for chunk in chunks]
    embeddings = embedder.embed_documents(texts)

    vector_store = ChromaStore(chunk_size=chunk_size)
    vector_store.reset()
    vector_store.add(chunks, embeddings)


if __name__ == "__main__":
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")

    config_path = Path(__file__).resolve().parent.parent / "configs" / "config.yaml"
    app_config = load_config(config_path)
    policy_path = Path(__file__).resolve().parent.parent / "data" / "policy.md"
    article_path = Path(__file__).resolve().parent.parent / "data" / "help_articles"
    doc_path = [(policy_path, "policy"), (article_path, "help_articles")]

    build_index(doc_path, api_key, app_config.embedding_model, app_config.chunk_size)
