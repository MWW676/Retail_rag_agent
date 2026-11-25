import logging
from google import genai
from google.genai import types
from google.genai.errors import APIError, ServerError
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential, before_sleep_log

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
logger.addHandler(console_handler)

RETRYABLE_CODES = {429, 503}

def is_retryable(exc: BaseException) -> bool:
    if isinstance(exc, ServerError):
        return True
    return isinstance(exc, APIError) and exc.code in RETRYABLE_CODES

class GeminiEmbedder:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = genai.Client(api_key=self.api_key)
        self.embed_model = "gemini-embedding-001"

    @retry(
        retry=retry_if_exception(is_retryable),  # which exceptions trigger a retry
        stop=stop_after_attempt(4),  # 1 try + 3 retries
        wait=wait_exponential(multiplier=5, min=5, max=30),  # wait grows each retry, capped at 30s
        before_sleep=before_sleep_log(logger, logging.WARNING),  # log each retry
        reraise=True,  # after last attempt, raise the original error
    )
    def _call_api(self, texts: str | list[str], task_type: str):
        resp = self.client.models.embed_content(
            model=self.embed_model,
            contents=texts,
            config=types.EmbedContentConfig(task_type=task_type)
        )
        return resp

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        result = self._call_api(texts=texts, task_type="RETRIEVAL_DOCUMENT")
        logger.info("Documents embedded.")

        return [e.values for e in result.embeddings]

    def embed_query(self, text: str) -> list[float]:
        result = self._call_api(texts=text, task_type="RETRIEVAL_QUERY")
        logger.info("Query embedded.")

        return result.embeddings[0].values

