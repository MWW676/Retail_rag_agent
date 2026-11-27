import os
from pathlib import Path
from dotenv import load_dotenv
from src.core.config import load_config
from src.storage.vector_store import ChromaStore
from src.models.embedding_client import GeminiEmbedder
from src.retrieval.retriever import Retriever

def search_demo(query: str, retriever: Retriever, k: int) -> None:
    retrieved_results = retriever.retrieve(query)
    results = [(chunk.chunk_id, score) for chunk, score in retrieved_results]
    print(f"Question: {query}")
    print(f"Top {k} results: {results}")


if __name__ == "__main__":
    question_list = [
        "Can I cancel an order that is still pending?",
        "How do I get a refund for something I received?",
        "Can I change the payment method on my order?",
        "Can I exchange an item for a different size?",
        "Do you offer gift wrapping?"
    ]

    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    config_path = Path(__file__).resolve().parent.parent / "configs" / "config.yaml"
    app_config = load_config(config_path)

    embedder = GeminiEmbedder(api_key=api_key, embedding_model=app_config.embedding_model)
    vector_store = ChromaStore(chunk_size=app_config.chunk_size)
    retriever = Retriever(embedder, vector_store, app_config.top_k)

    for question in question_list:
        search_demo(question, retriever, app_config.top_k)
