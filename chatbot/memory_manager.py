# chatbot/memory_manager.py
from typing import List, Dict
from openai import OpenAI

class MemoryManager:
    def __init__(self, client: OpenAI, personality_manager, name: str):
        self.client = client
        self.personality_manager = personality_manager
        self.name = name
        self.chat_history = []
        self.chat_history_summary_count = 3
    
    def summarize_chat_history(self, chat_history_string: str) -> str:
        try:
            messages = [
                {"role": "system", "content": f"Summarize this conversation in 30 words or less, focusing on key points and emotional tone. Always use {self.name}'s name and specific personality traits: {self.personality_manager.get_personality_traits()}. Never use generic terms like 'the assistant'."},
                {"role": "user", "content": chat_history_string}
            ]
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=100
            )
            memory_summary = response.choices[0].message.content
            
            if len(self.chat_history) % 10 == 0:
                self.personality_manager.update_from_response(memory_summary, self.client)
            
            self.personality_manager.update_memory(memory_summary, self.name)
            
            return memory_summary
            
        except Exception as e:
            print(f"Error during summarization: {e}")
            return "Error summarizing chat history."