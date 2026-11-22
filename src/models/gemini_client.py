import json
import time
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

RETRYABLE_CODES = {429}

def is_retryable(exc: BaseException) -> bool:
    if isinstance(exc, ServerError):
        return True
    return isinstance(exc, APIError) and exc.code in RETRYABLE_CODES

class GeminiClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = genai.Client(api_key=api_key)
        self.model = "gemma-4-26b-a4b-it"
        self.RATE_LIMIT_PER_MINUTE = 30
        self.LAST_REQUEST_TIME = 0  # Initialize last request time

    def rate_limit(self):
        now = time.time()
        elapsed_time = now - self.LAST_REQUEST_TIME
        if elapsed_time < 60 / self.RATE_LIMIT_PER_MINUTE:
            sleep_time = (60 / self.RATE_LIMIT_PER_MINUTE) - elapsed_time + 5
            logger.info(f"Rate limit reached. Sleeping for {sleep_time:.2f} seconds.")
            time.sleep(sleep_time)
        self.LAST_REQUEST_TIME = time.time()

    @retry(
    retry=retry_if_exception(is_retryable),            # which exceptions trigger a retry
    stop=stop_after_attempt(4),                        # 1 try + 3 retries
    wait=wait_exponential(multiplier=5, min=5, max=30),  # wait grows each retry, capped at 30s
    before_sleep=before_sleep_log(logger, logging.WARNING),  # log each retry
    reraise=True,                                      # after last attempt, raise the original error
)
    def _call_api(self, user_msg, sys_instructions, temperature):
        config_object = types.GenerateContentConfig(
            temperature=temperature,
            system_instruction=sys_instructions,
            response_mime_type="application/json"
        )
        self.rate_limit()
        response = self.client.models.generate_content(
            model=self.model,
            contents=user_msg,
            config=config_object
        )

        return response

    def generate_text(self, user_msg: str | list[str], sys_instructions: str = "", temperature: float = 1.0)->dict:
        try:
            response = self._call_api(user_msg, sys_instructions, temperature)

            # Build dict from resp
            raw_text = response.text
            clean_json_str = raw_text.replace("```json", "").replace("```", "").strip()

            try:
                ai_result = json.loads(clean_json_str)
            except json.JSONDecodeError:
                logger.error(f"Failed to parse JSON: {raw_text}")
                return {"status": "ERROR", "error": "Failed to parse JSON from model response."}

            usage_dict = (
                response.usage_metadata.model_dump()
                if response.usage_metadata is not None and hasattr(response.usage_metadata, "model_dump")
                else {}
            )

            resp_dict = {
                "result": ai_result,
                "status": "SUCCESS",
                "metadata": {
                    "model": self.model,
                    "token_used": usage_dict,
                    "timestamp": int(time.time())
                }
            }
            return resp_dict
        except APIError as e:
            logger.error(f"API Error: {e}")
            return {"status": "ERROR", "error": str(e)}
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return {"status": "ERROR", "error": str(e)}