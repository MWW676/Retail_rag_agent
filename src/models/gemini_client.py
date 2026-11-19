import logging
from google import genai
from google.genai import types
from google.genai.errors import APIError

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class GeminiClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = genai.GeminiClient(api_key=api_key)
        self.model = "gemini-3.8-flash"

    def generate_text(self, user_msg: str, temperature: float = 1.0, max_tokens: int = 100) -> str:
        try:
            config_object = types.TextGenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens
            )
            response = self.client.generate_text(
                model=self.model,
                contents=user_msg,
                config=config_object
            )
            return response.text
        except APIError as e:
            logger.error(f"API Error: {e}")
            return ""
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return ""