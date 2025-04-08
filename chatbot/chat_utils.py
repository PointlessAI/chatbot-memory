# chatbot/chat_utils.py
from typing import Dict

def create_welcome_message(name: str, user_profile: Dict, core_identity: Dict, emotional: Dict) -> str:
    relationship = user_profile.get('relationship', {})
    trust_level = relationship.get('trust_level', 0.0)
    emotional_bond = relationship.get('emotional_bond', 0.0)
    
    if not name or name == 'the user':
        name = "sir"
    
    if trust_level > 0.7 and emotional_bond > 0.7:
        return f"Good day, {name}. It's wonderful to see you again. How are you?"
    elif trust_level > 0.5 and emotional_bond > 0.5:
        return f"Hello, {name}. It's nice to see you. How are you today?"
    elif trust_level > 0.3 and emotional_bond > 0.3:
        return f"Greetings, {name}. Hello, how are you?"
    else:
        return f"Good day, {name}. How are you?"