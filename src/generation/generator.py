import json
import logging
from src.core.models import Chunk, Answer
from src.models.gemini_client import GeminiClient
from src.utils.prompt_utils import render_prompt

logger = logging.getLogger(__name__)

def build_prompt(question: str, retrieved: list[tuple[Chunk, float]], prompt_version: str) -> tuple[str, str]:
    schema_dict = Answer.model_json_schema()
    schema_str = json.dumps(schema_dict, indent=2)
    system_instruction = render_prompt(f"system_{prompt_version}.md", schema_str=schema_str)
    user_message = render_prompt(f"user_{prompt_version}.md", query=question,
                                 chunks=[chunk for chunk, _ in retrieved])

    return system_instruction, user_message

def generate_answer(question: str, retrieved: list[tuple[Chunk, float]], llm: GeminiClient, prompt_version: str, temperature: float) -> dict:
    sys_instruction, user_msg = build_prompt(question, retrieved, prompt_version)
    resp = llm.generate_text(user_msg=user_msg, sys_instructions=sys_instruction, temperature=temperature)
    if resp["status"] == "ERROR":
        return resp

    results = resp["result"]
    try:
        validated_result = Answer(**results)
    except Exception as e:
        return {"status": "ERROR", "error": f"Schema Validation Error:{e}"}

    retrieved_chunk_ids = [chunk.chunk_id for chunk, _ in retrieved]
    for id in validated_result.cited_chunk_ids:
        if id not in retrieved_chunk_ids:
            logger.warning(f"Chunk_id outside reference: {id}")

    return {"status": "SUCCESS", "answer": validated_result, "metadata": resp["metadata"]}

