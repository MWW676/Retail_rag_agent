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

USER_QUERY_1 = "I bought a jacket last week, can I return it?"
USER_QUERY_2 = "What if I already wore it?"

class QueryExercise:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model = GeminiClient(self.api_key)
        self.current_dir = Path(__file__).parent
        self.file_path = self.current_dir / "user_query_response.jsonl"
        self.analysis_file_path = self.current_dir / "user_query_analysis_results.txt"


    def user_query_checks(self):
        resp_1 = None
        for query in [USER_QUERY_1, USER_QUERY_2]:
            response = self.model.generate_text(
                user_msg=query,
                sys_instructions=STORE_POLICIES
            )
            if response["status"] == "ERROR":
                data = {
                    "status": response["status"],
                    "model": self.model.model,
                    "query": query,
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
                    "query": query,
                    "generated_text": response["result"],
                    "token_usage": meta.get("token_used", "{}"),
                    "timestamp": meta.get("timestamp")
                }
                if query == USER_QUERY_1:
                    resp_1 = response["result"]
            with open(self.file_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(data)+'\n')

        combined_query = f"role=user:{USER_QUERY_1}, role=model: {resp_1}, role=user: {USER_QUERY_2}"
        response = self.model.generate_text(
            user_msg=combined_query,
            sys_instructions=STORE_POLICIES,
        )
        if response["status"] == "ERROR":
            data = {
                "status": response["status"],
                "model": self.model.model,
                "query": combined_query,
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
                "query": combined_query,
                "generated_text": response["result"],
                "token_usage": meta.get("token_used", "{}"),
                "timestamp": meta.get("timestamp")
            }
        with open(self.file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(data)+'\n')

    def analysis(self):
        with open(self.file_path, "r", encoding="utf-8") as f:
            data = [json.loads(line) for line in f]

        queries = [item["query"] for item in data]
        input_token_range = thought_token_range = total_token_range = [0]  # Initialize ranges
        for query in set(queries):
            input_token_range = [item["token_usage"]["prompt_token_count"] for item in data if item["query"] == query and item["status"] == "SUCCESS"]
            thought_token_range = [item["token_usage"]["thoughts_token_count"] for item in data if item["query"] == query and item["status"] == "SUCCESS"]
            total_token_range = [item["token_usage"]["total_token_count"] for item in data if item["query"] == query and item["status"] == "SUCCESS"]

            with open(self.analysis_file_path, "a", encoding="utf-8") as f:
                f.write(f"Query: {query}, Input Token Usage Range: {min(input_token_range)} - {max(input_token_range)}, Thought Token Usage Range: {min(thought_token_range)} - {max(thought_token_range)},Total Token Usage Range: {min(total_token_range)} - {max(total_token_range)}\n")

if __name__ == "__main__":
    exercise = QueryExercise()
    exercise.user_query_checks()
    exercise.analysis()