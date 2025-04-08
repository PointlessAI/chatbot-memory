# chatbot/personality_manager.py
import os
import json
from typing import List, Dict, Any

class PersonalityManager:
    def __init__(self, base_dir="my-personality"):
        """Initialize the personality manager with the base directory containing all personalities."""
        self.base_dir = base_dir
        self.personality_files = [
            'core-identity.json',
            'emotional-framework.json',
            'cognitive-style.json',
            'social-dynamics.json',
            'interests-values.json',
            'behavioral-patterns.json',
            'memory-growth.json',
            'user-profile.json'
        ]
        self.current_personality = {}
        self.personality_dir = None
        
    def list_available_personalities(self) -> List[str]:
        """Get a list of available personalities."""
        try:
            personalities = [d for d in os.listdir(self.base_dir) 
                           if os.path.isdir(os.path.join(self.base_dir, d))]
            return sorted(personalities)
        except Exception as e:
            print(f"Error listing personalities: {e}")
            return []
    
    def load_personality(self, personality_name: str) -> bool:
        """Load a specific personality by name."""
        try:
            personality_path = os.path.join(self.base_dir, personality_name)
            if not os.path.isdir(personality_path):
                print(f"Error: Personality '{personality_name}' not found.")
                return False
            
            self.personality_dir = personality_path
            return self._load_personality()
        except Exception as e:
            print(f"Error in load_personality: {e}")
            return False
    
    def _load_personality(self) -> bool:
        """Load all personality files into current_personality."""
        try:
            self.current_personality = {}
            for filename in self.personality_files:
                file_path = os.path.join(self.personality_dir, filename)
                if os.path.exists(file_path):
                    try:
                        with open(file_path, 'r') as f:
                            name = os.path.splitext(filename)[0]
                            self.current_personality[name] = json.load(f)
                    except json.JSONDecodeError as e:
                        print(f"Error parsing {filename}: {e}")
                        return False
                else:
                    print(f"Warning: {filename} not found in {self.personality_dir}")
                    self.current_personality[os.path.splitext(filename)[0]] = {}
            return True
        except Exception as e:
            print(f"Error in _load_personality: {e}")
            return False
    
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