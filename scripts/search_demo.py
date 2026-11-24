import os
from dotenv import load_dotenv
from src.storage.vector_store import ChromaStore
from src.models.embedding_client import GeminiEmbedder

def search_demo(query: str, embedder: GeminiEmbedder, vector_store: ChromaStore) -> list[tuple[str, float]]:
    embedded_query = embedder.embed_query(query)
    resp = vector_store.search(embedded_query)
    results = [(chunk.chunk_id, score) for chunk, score in resp]

    return results

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
    embedder = GeminiEmbedder(api_key)
    vector_store = ChromaStore()

    for question in question_list:
        results = search_demo(question, embedder, vector_store)
        print(f"Question: {question}")
        print(f"Top 3 results: {results}")
