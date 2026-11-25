import os
from dotenv import load_dotenv
from src.storage.vector_store import ChromaStore
from src.models.embedding_client import GeminiEmbedder
from src.retrieval.retriever import Retriever

def search_demo(query: str, retriever: Retriever) -> None:
    retrieved_results = retriever.retrieve(query)
    results = [(chunk.chunk_id, score) for chunk, score in retrieved_results]
    print(f"Question: {query}")
    print(f"Top 3 results: {results}")


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
    retriever = Retriever(embedder, vector_store)

    for question in question_list:
        search_demo(question, retriever)
