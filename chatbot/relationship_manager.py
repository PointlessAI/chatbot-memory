import os
import json
from typing import Dict, List, Optional
from openai import OpenAI
from dotenv import load_dotenv

class RelationshipManager:
    def __init__(self, personality_dir: str):
        # personality_dir should be the full path to the AI personality's directory
        self.personality_dir = personality_dir
        self.relationships_dir = os.path.join(self.personality_dir, "relationships")
        if not os.path.exists(self.relationships_dir):
            os.makedirs(self.relationships_dir)
        self.current_relationships = {}
        
        # Initialize OpenAI client
        load_dotenv()
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OpenAI API key not found in environment variables or .env file")
        self.client = OpenAI(api_key=api_key)

    def get_relationship_file(self, other_name: str) -> str:
        """Get the path to a relationship file for a specific person."""
        return os.path.join(self.relationships_dir, f"{other_name}.json")

    def load_relationship(self, other_name: str) -> Dict:
        """Load relationship data for a specific person."""
        file_path = self.get_relationship_file(other_name)
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return json.load(f)
        return self._create_blank_relationship(other_name)

    def _create_blank_relationship(self, other_name: str) -> Dict:
        """Create a blank relationship template."""
        return {
            "interactions": [],
            "observed_traits": [],
            "shared_experiences": [],
            "emotional_dynamics": {
                "positive_moments": [],
                "challenges": [],
                "trust_level": "neutral"
            },
            "communication_patterns": {
                "topics": [],
                "style": [],
                "frequency": "occasional"
            },
            "relationship_development": {
                "milestones": [],
                "current_status": "acquaintance",
                "growth_areas": []
            },
            "social_preferences": {
                "preferred_topics": [],
                "interaction_style": [],
                "boundaries": []
            },
            "interaction_history": {
                "recent_interactions": [],
                "key_moments": [],
                "conflicts": [],
                "resolutions": []
            }
        }

    def save_relationship(self, other_name: str, data: Dict) -> None:
        """Save relationship data for a specific person."""
        file_path = self.get_relationship_file(other_name)
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)

    def update_relationship(self, other_name: str, conversation_segment: List[Dict]) -> None:
        """Update relationship based on new conversation."""
        current_data = self.load_relationship(other_name)
        
        system_prompt = f"""You are a relationship analyzer. Your task is to analyze this conversation and return ONLY a valid JSON object.

IMPORTANT: Your entire response must be a valid JSON object, nothing else.

Analyze the relationship dynamics between the two people in this conversation and update the relationship data.

Return format must be exactly:
{{
    "interactions": ["new interaction 1", "new interaction 2"],
    "observed_traits": ["new trait 1", "new trait 2"],
    "shared_experiences": ["new experience 1", "new experience 2"],
    "emotional_dynamics": {{
        "positive_moments": ["new moment 1", "new moment 2"],
        "challenges": ["new challenge 1", "new challenge 2"],
        "trust_level": "updated level"
    }},
    "communication_patterns": {{
        "topics": ["new topic 1", "new topic 2"],
        "style": ["new style 1", "new style 2"],
        "frequency": "updated frequency"
    }},
    "relationship_development": {{
        "milestones": ["new milestone 1", "new milestone 2"],
        "current_status": "updated status",
        "growth_areas": ["new area 1", "new area 2"]
    }},
    "social_preferences": {{
        "preferred_topics": ["new topic 1", "new topic 2"],
        "interaction_style": ["new style 1", "new style 2"],
        "boundaries": ["new boundary 1", "new boundary 2"]
    }},
    "interaction_history": {{
        "recent_interactions": ["new interaction 1", "new interaction 2"],
        "key_moments": ["new moment 1", "new moment 2"],
        "conflicts": ["new conflict 1", "new conflict 2"],
        "resolutions": ["new resolution 1", "new resolution 2"]
    }}
}}

Only include fields that need updates. Ensure the response is valid JSON."""
        
        try:
            # Format the conversation for analysis
            conversation_text = "\n".join([
                f"{msg['speaker']}: {msg['message']}" 
                for msg in conversation_segment
            ])
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Analyze this conversation:\n\n{conversation_text}"}
            ]
            
            # Get analysis from GPT
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=2000,
                temperature=0.7
            )
            
            response_content = response.choices[0].message.content
            updates = json.loads(response_content)
            
            # Merge updates with current data
            self._merge_relationship_data(current_data, updates)
            
            # Save the updated relationship
            self.save_relationship(other_name, current_data)
            
            print(f"\n✅ Successfully updated relationship with {other_name}")
            print(f"Updated relationship preview:")
            print(json.dumps(current_data, indent=2)[:500] + "...")
            
        except Exception as e:
            print(f"❌ Error updating relationship: {e}")

    def _merge_relationship_data(self, current_data: Dict, new_data: Dict) -> Dict:
        """Merge new relationship data with current data."""
        for key, value in new_data.items():
            if isinstance(value, dict):
                if key not in current_data:
                    current_data[key] = {}
                current_data[key] = self._merge_relationship_data(current_data[key], value)
            elif isinstance(value, list):
                if key not in current_data:
                    current_data[key] = []
                current_data[key].extend(item for item in value if item not in current_data[key])
            else:
                current_data[key] = value
        return current_data 