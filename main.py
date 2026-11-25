import os
import logging
from dotenv import load_dotenv
from src.models.gemini_client import GeminiClient
from src.models.embedding_client import GeminiEmbedder
from src.storage.vector_store import ChromaStore
from src.retrieval.retriever import Retriever
from src.generation.generator import generate_answer

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
logger.addHandler(console_handler)

def retail_rag_agent(query: str, retriever: Retriever, llm: GeminiClient):
    retrieved_results = retriever.retrieve(query)
    answer = generate_answer(question=query, retrieved=retrieved_results, llm=llm)
    print(answer)


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
    embedder = GeminiEmbedder(api_key=api_key)
    llm = GeminiClient(api_key=api_key)
    vector_store = ChromaStore()
    retriever = Retriever(embedder, vector_store)

    for q in question_list:
        print(f"Question: {q}")
        retail_rag_agent(query=q, retriever=retriever, llm=llm)
