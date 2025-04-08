# chatbot/token_manager.py
import tiktoken
from typing import List, Dict

class TokenManager:
    def __init__(self):
        self.total_tokens = 0
    
    def count_tokens(self, messages: List[Dict], model: str = "gpt-4o-mini") -> int:
        try:
            encoding = tiktoken.encoding_for_model(model)
            num_tokens = 0
            for message in messages:
                num_tokens += 4
                for key, value in message.items():
                    num_tokens += len(encoding.encode(value))
                    if key == "name":
                        num_tokens += -1
            num_tokens += 2
            return num_tokens
        except Exception as e:
            print(f"Error counting tokens: {e}")
            return 0
    
    def print_token_usage(self, model: str, messages: List[Dict], response: str) -> None:
        input_tokens = self.count_tokens(messages, model)
        output_tokens = len(tiktoken.encoding_for_model(model).encode(response))
        total_tokens = input_tokens + output_tokens
        self.total_tokens += total_tokens
        
        print(f"\nToken Usage for {model}:")
        print(f"Input tokens: {input_tokens}")
        print(f"Output tokens: {output_tokens}")
        print(f"Total tokens for this request: {total_tokens}")
        print(f"Running total tokens: {self.total_tokens}\n")