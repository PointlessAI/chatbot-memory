# chatbot/personality_manager.py
import os
import json
import shutil
from typing import Dict, Optional

class PersonalityManager:
    def __init__(self, base_dir: str = "my-personality"):
        self.base_dir = base_dir
        self.personality_dir = None
        self.current_personality = {}
        
        # Create users directory if it doesn't exist
        self.users_dir = os.path.join(base_dir, "users")
        if not os.path.exists(self.users_dir):
            os.makedirs(self.users_dir)

    def create_blank_personality(self, name: str, is_user: bool = False) -> None:
        """Create a new personality with blank template files."""
        target_dir = os.path.join(self.users_dir if is_user else self.base_dir, name)
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

        # Template structure for a new personality
        blank_template = {
            "core-identity.json": {
                "name": name,
                "background": "",
                "traits": [],
                "personality_type": ""
            },
            "interests-values.json": {
                "interests": [],
                "values": [],
                "preferences": {}
            },
            "emotional-framework.json": {
                "emotional_range": [],
                "communication_style": [],
                "observed_responses": []
            },
            "behavioral-patterns.json": {
                "habits": [],
                "routines": [],
                "decision_making": []
            },
            "cognitive-style.json": {
                "thinking_patterns": [],
                "learning_style": [],
                "problem_solving": []
            },
            "memory-growth.json": {
                "experiences": [],
                "learned_concepts": [],
                "growth_areas": []
            }
        }

        # Create each file with blank template
        for filename, content in blank_template.items():
            file_path = os.path.join(target_dir, filename)
            with open(file_path, 'w') as f:
                json.dump(content, f, indent=2)

    def load_personality(self, name: str, is_user: bool = False) -> bool:
        """Load a personality by name. Returns True if successful."""
        if is_user:
            target_dir = os.path.join(self.users_dir, name)
        else:
            target_dir = os.path.join(self.base_dir, "ai", name)
        
        if not os.path.exists(target_dir):
            if is_user:
                print(f"Creating new user personality: {name}")
                self.create_blank_personality(name, is_user=True)
            else:
                return False

        self.personality_dir = target_dir
        self._load_personality_files()
        return True

    def _load_personality_files(self) -> None:
        """Load all personality files from the current personality directory."""
        self.current_personality = {}
        json_files = [f for f in os.listdir(self.personality_dir) if f.endswith('.json')]
        
        for filename in json_files:
            file_path = os.path.join(self.personality_dir, filename)
            try:
                with open(file_path, 'r') as f:
                    self.current_personality[filename] = json.load(f)
            except json.JSONDecodeError as e:
                print(f"Error loading {filename}: {e}")
                self.current_personality[filename] = {}

    def save_personality_file(self, filename: str, data: Dict) -> None:
        """Save updates to a personality file."""
        if self.personality_dir is None:
            raise ValueError("No personality loaded")
            
        file_path = os.path.join(self.personality_dir, filename)
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        # Update current personality
        self.current_personality[filename] = data