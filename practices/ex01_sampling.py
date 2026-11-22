import os
import time
import json
from src.models.gemini_client import GeminiClient
from pathlib import Path
from dotenv import load_dotenv

STORE_POLICIES = """
    1. Return Policy: Customers can return items within 30 days of purchase with a valid receipt for a full refund or exchange.
    2. Warranty: All electronic products come with a one-year warranty covering manufacturing defects.
    3. Shipping: We offer free standard shipping on orders over $50. Expedited shipping options are available at an additional cost.
    4. Payment Methods: We accept Visa, MasterCard, American Express, PayPal, and Apple Pay.
    5. Privacy Policy: We are committed to protecting customer privacy and will not share personal information with third parties without consent.
    6. Customer Support: Our customer support team is available Monday through Friday from 9 AM to 5 PM EST. You can reach us via phone, email, or live chat.
    7. Items cannot be returned if they are damaged due to misuse, or if they are perishable goods. Including but not limited to food, flowers, and the following health products: vitamins, supplements, and over-the-counter medications.
    8. Gift cards are non-refundable and cannot be exchanged for cash.
    9. Sale items are final sale and cannot be returned or exchanged.
    10. We reserve the right to modify our store policies at any time without prior notice
"""

USER_QUERY = "What is your return policy for electronic products?"


class TemperatureExercise:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model = GeminiClient(self.api_key)
        self.current_dir = Path(__file__).parent
        self.file_path = self.current_dir / "model_response.jsonl"
        self.analysis_file_path = self.current_dir / "analysis_results.txt"


    def resp_temperature_checks(self):
        for t in [0, 1.0]:
            for i in range(3):  # Generate 3 responses for each temperature
                response = self.model.generate_text(
                    user_msg=USER_QUERY,
                    sys_instructions=STORE_POLICIES,
                    temperature=t
                )
                if response["status"] == "ERROR":
                    data = {
                        "status": response["status"],
                        "model": self.model.model,
                        "temperature": t,
                        "generated_text": None,
                        "token_usage": None,
                        "timestamp": int(time.time()),
                        "error": response["error"]
                    }
                else:
                    meta = response.get("metadata", {})
                    data = {
                        "status": response["status"],
                        "model": meta.get("model"),
                        "temperature": t,
                        "generated_text": response["result"],
                        "token_usage": meta.get("token_used", "{}"),
                        "timestamp": meta.get("timestamp")
                    }
                with open(self.file_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(data)+'\n')


    def analysis(self):
        with open(self.file_path, "r", encoding="utf-8") as f:
            data = [json.loads(line) for line in f]

        temp_types = [item["temperature"] for item in data]
        input_token_range = thought_token_range = total_token_range = [0]  # Initialize ranges
        for temp in set(temp_types):
            unique_strings = {
                json.dumps(item["generated_text"], sort_keys=True)
                for item in data
                if item["temperature"] == temp and item["status"] == "SUCCESS"
            }
            resp_types = [json.loads(s) for s in unique_strings]
            input_token_range = [item["token_usage"]["prompt_token_count"] for item in data if item["temperature"] == temp and item["status"] == "SUCCESS"]
            thought_token_range = [item["token_usage"]["thoughts_token_count"] for item in data if item["temperature"] == temp and item["status"] == "SUCCESS"]
            total_token_range = [item["token_usage"]["total_token_count"] for item in data if item["temperature"] == temp and item["status"] == "SUCCESS"]

            with open(self.analysis_file_path, "a", encoding="utf-8") as f:
                f.write(f"Temperature:{temp}, Success Unique Responses: {len(resp_types)}, Input Token Usage Range: {min(input_token_range)} - {max(input_token_range)}, Thought Token Usage Range: {min(thought_token_range)} - {max(thought_token_range)},Total Token Usage Range: {min(total_token_range)} - {max(total_token_range)}\n")

if __name__ == "__main__":
    exercise = TemperatureExercise()
    exercise.resp_temperature_checks()
    exercise.analysis()