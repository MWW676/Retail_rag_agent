import os
import logging
import uuid
import time
from dotenv import load_dotenv
from pathlib import Path
from src.core.models import Chunk
from src.models.gemini_client import GeminiClient
from src.models.embedding_client import GeminiEmbedder
from src.storage.vector_store import ChromaStore
from src.retrieval.retriever import Retriever
from src.generation.generator import generate_answer
from src.core.config import load_config, AppConfig
from src.utils.run_logger import log_run

logging.basicConfig(level=logging.INFO)

def retail_rag_agent(query: str, retriever: Retriever, llm: GeminiClient, config: AppConfig):
    t0 = time.perf_counter()
    retrieved_results = retriever.retrieve(query)
    t1 = time.perf_counter()
    result = generate_answer(question=query, retrieved=retrieved_results, llm=llm,
                             prompt_version=config.prompt_version, temperature=config.temperature)
    t2 = time.perf_counter()

    timings = {"retrieval_ms": round((t1 - t0) * 1000), "generation_ms": round((t2 - t1) * 1000)}
    return retrieved_results, result, timings


def build_run_record(run_id: str, retrieved_results: list[tuple[Chunk, float]], question: str,
                     result: dict, config: AppConfig, timings: dict) -> dict:
    ok = result["status"] == "SUCCESS"
    return {
        "run_id": run_id,
        "timestamp": time.time(),
        "question": question,
        "config": config.model_dump(),
        "retrieved": [(chunk.chunk_id, score) for chunk, score in retrieved_results],
        "answer": result["answer"].answer if ok else None,
        "refused": result["answer"].refused if ok else None,
        "cited_chunk_ids": result["answer"].cited_chunk_ids if ok else None,
        "token_counts": result["metadata"]["token_used"] if ok else None,
        "status": result["status"],
        "error": None if ok else result["error"],
        **timings,
    }


if __name__ == "__main__":
    question_list = [
        "Can I cancel an order that is still pending?",
        "How do I get a refund for something I received?",
        "Can I change the payment method on my order?",
        "Can I exchange an item for a different size?",
        "Do you offer gift wrapping?",
        "My order already shipped, can I still cancel it?",
        "How long until I get my money back?",
        "What reasons can I give to cancel my order?"
    ]

    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")

    config_path = Path(__file__).resolve().parent / "configs" / "config.yaml"
    app_config = load_config(config_path)

    embedder = GeminiEmbedder(api_key=api_key, embedding_model=app_config.embedding_model)
    llm = GeminiClient(api_key=api_key, llm_model=app_config.llm_model)
    vector_store = ChromaStore(chunk_size=app_config.chunk_size)
    retriever = Retriever(embedder, vector_store, app_config.top_k)
    run_id = str(uuid.uuid4())
    log_path = Path(__file__).resolve().parent / "data" / "runs" / "runs.jsonl"

    for q in question_list:
        print(f"Question: {q}")
        retrieved_results, result, timings = retail_rag_agent(q, retriever, llm, app_config)
        record = build_run_record(run_id, retrieved_results, q, result, app_config, timings)
        log_run(record, log_path)
