from google import genai
from google.genai import types
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
logger.addHandler(console_handler)

class GeminiEmbedder:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = genai.Client(api_key=self.api_key)
        self.embed_model = "gemini-embedding-001"

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        result = self.client.models.embed_content(
            model=self.embed_model,
            contents=texts,
            config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT")
        )
        logger.info("Documents embedded.")

        return [e.values for e in result.embeddings]

    def embed_query(self, text: str) -> list[float]:
        result = self.client.models.embed_content(
            model=self.embed_model,
            contents=text,
            config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY")
        )
        logger.info("Query embedded.")

        return result.embeddings[0].values
