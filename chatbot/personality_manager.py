# chatbot/personality_manager.py
import os
import glob
import json
import datetime
from typing import Dict, Any, List

class PersonalityManager:
    def __init__(self, personality_dir="my-personality"):
        """Initialize the personality manager with a directory containing personality files."""
        self.personality_dir = personality_dir
        self.personality_files = {
            'core-identity': 'core-identity.json',
            'emotional-framework': 'emotional-framework.json',
            'cognitive-style': 'cognitive-style.json',
            'social-dynamics': 'social-dynamics.json',
            'interests-values': 'interests-values.json',
            'behavioral-patterns': 'behavioral-patterns.json',
            'memory-growth': 'memory-growth.json',
            'user-profile': 'user-profile.json'
        }
        self.current_personality = {}
        
        # Ensure directory exists
        if not os.path.exists(self.personality_dir):
            os.makedirs(self.personality_dir)
        
        # Initialize files if they don't exist
        self._initialize_personality_files()
        self._load_personality()
    
    def _initialize_personality_files(self):
        """Create empty template files if they don't exist."""
        template = {
            "core-identity.json": {
                "name": "",
                "age": "",
                "profession": "",
                "core_values": [],
                "life_philosophy": "",
                "aspirations": []
            },
            "emotional-framework.json": {
                "current_state": {
                    "mood": "",
                    "energy_level": "",
                    "stress_level": ""
                },
                "emotional_patterns": {
                    "triggers": {"positive": [], "negative": []},
                    "responses": {"positive": [], "negative": []}
                }
            },
            "cognitive-style.json": {
                "thinking_patterns": [],
                "learning_style": "",
                "problem_solving": ""
            },
            "social-dynamics.json": {
                "relationship_styles": {},
                "social_preferences": {},
                "communication_preferences": {}
            },
            "interests-values.json": {
                "interests": [],
                "values": [],
                "preferences": {}
            },
            "behavioral-patterns.json": {
                "habits": [],
                "routines": [],
                "responses": {}
            },
            "memory-growth.json": {
                "memories": [],
                "learned_concepts": [],
                "growth_areas": []
            },
            "user-profile.json": {
                "personal_info": {},
                "preferences": {},
                "relationship": {}
            }
        }
        
        # Only create files if they don't exist
        for filename, default_content in template.items():
            file_path = os.path.join(self.personality_dir, filename)
            if not os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    json.dump(default_content, f, indent=4)
    
    def _load_personality(self):
        """Load all personality files into current_personality."""
        self.current_personality = {}
        for category, filename in self.personality_files.items():
            file_path = os.path.join(self.personality_dir, filename)
            try:
                with open(file_path, 'r') as f:
                    self.current_personality[category] = json.load(f)
            except Exception as e:
                print(f"Error loading {filename}: {e}")
                self.current_personality[category] = {}
    
    def get_personality_traits(self) -> List[str]:
        """Get personality traits from core identity."""
        core_identity = self.current_personality.get('core-identity', {})
        return core_identity.get('core_values', [])
    
    def get_user_profile(self) -> Dict[str, Any]:
        """Get the user profile."""
        return self.current_personality.get('user-profile', {})
    
    def update_memory(self, memory_text: str, assistant_name: str):
        """Update memory growth with new interactions."""
        memory_file = os.path.join(self.personality_dir, 'memory-growth.json')
        try:
            with open(memory_file, 'r') as f:
                memory_data = json.load(f)
            
            # Add new memory
            memory_data['memories'].append({
                'timestamp': datetime.datetime.now().isoformat(),
                'content': memory_text,
                'assistant': assistant_name
            })
            
            # Keep only recent memories
            memory_data['memories'] = memory_data['memories'][-50:]  # Keep last 50 memories
            
            with open(memory_file, 'w') as f:
                json.dump(memory_data, f, indent=4)
        
        except Exception as e:
            print(f"Error updating memory: {e}")