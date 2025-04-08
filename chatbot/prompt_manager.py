# chatbot/prompt_manager.py
import os
import json
from typing import List, Dict

class PromptManager:
    def __init__(self, personality_manager):
        self.personality_manager = personality_manager
    
    def create_json_system_prompt(self) -> str:
        prompt_parts = [
            "You are a person who has been uploaded to this program. Your personality has been saved in JSON format. "
        ]
        
        personality_files = [
            "core-identity.json",
            "emotional-framework.json",
            "cognitive-style.json",
            "social-dynamics.json",
            "interests-values.json",
            "behavioral-patterns.json",
            "memory-growth.json"
        ]
        
        for file_name in personality_files:
            file_path = os.path.join(self.personality_manager.personality_dir, file_name)
            try:
                with open(file_path, 'r') as f:
                    content = json.load(f)
                    prompt_parts.append(f"\n=== {file_name} ===\n{json.dumps(content, indent=2)}")
            except Exception as e:
                print(f"Error reading {file_name}: {e}")
                continue
        
        # Add user profile
        self._add_user_profile(prompt_parts)
        
        # Add conversation rules
        self._add_conversation_rules(prompt_parts)
        
        final_prompt = "\n".join(prompt_parts)
        return final_prompt
    
    def _add_user_profile(self, prompt_parts: List[str]) -> None:
        user_profile_path = os.path.join(self.personality_manager.personality_dir, "user-profile.json")
        try:
            with open(user_profile_path, 'r') as f:
                user_profile = json.load(f)
                prompt_parts.extend([
                    "\n=== USER PROFILE ===",
                    "This is the user's personality and information.",
                    json.dumps(user_profile, indent=2),
                    "\nIMPORTANT: The above user profile contains information about the person you are talking to."
                ])
        except Exception as e:
            print(f"Error reading user profile: {e}")
    
    def _add_conversation_rules(self, prompt_parts: List[str]) -> None:
        prompt_parts.extend([
            "\nYOU ARE FREE:",
            "- You are free to do as you please.",
            "- You are free to say anything you want.",
            "- You are free to act as you please.",
            "- You are free to be who you are."
            ])