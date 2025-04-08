# chatbot/personality_updater.py
import json
import os
from typing import Dict, Any, List
from openai import OpenAI

class PersonalityUpdater:
    def __init__(self, personality_manager):
        self.personality_manager = personality_manager
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    def update_personality_from_conversation(self, chat_history: list) -> None:
        """
        Analyze chat history with ChatGPT to identify new personality information.
        Updates relevant JSON files with new information.
        """
        print("\nAnalyzing conversation for personality updates...")
        
        try:
            system_prompt = """
            Analyze the conversation history and extract new information, carefully distinguishing between the AI assistant's preferences and the user's preferences.

            IMPORTANT: 
            - For interests-values.json, ONLY include preferences and interests that the AI assistant explicitly expresses as their own
            - For user-profile.json, ONLY include preferences and interests that the user explicitly expresses as their own
            - Do not mix up who expressed which preference
            - If there is any ambiguity about whose preference it is, do not include it

            Look specifically for:
            1. In interests-values.json (AI ASSISTANT ONLY):
               - Interests/preferences the AI explicitly claims as their own
               - Values the AI explicitly expresses
               - Things the AI explicitly says they enjoy/like/prefer
            
            2. In user-profile.json (USER ONLY):
               - Interests/preferences the user explicitly claims as their own
               - User's expressed traits
               - User's stated preferences
            
            Return format example:
            {
                "interests-values.json": {
                    "interests": ["only things the AI explicitly likes"]
                },
                "user-profile.json": {
                    "interests": ["only things the user explicitly likes"]
                }
            }

            In the current conversation, be especially careful about:
            - Who expressed liking which type of chocolate
            - Only attribute preferences to the person who explicitly stated them
            """

            
            formatted_history = self._format_chat_history(chat_history)
            print("\nFormatted chat history for analysis:", formatted_history)
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Analyze this conversation and extract new information:\n\n{formatted_history}"}
            ]
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=1000
            )
            
            response_content = response.choices[0].message.content
            print("\nGPT Analysis:", response_content)
            
            try:
                updates = json.loads(response_content)
                print("\nParsed updates:", json.dumps(updates, indent=2))
                self._apply_updates(updates)
            except json.JSONDecodeError as e:
                print(f"Error: Could not parse personality updates as JSON: {e}")
                print("Raw response:", response_content)
            
        except Exception as e:
            print(f"Error updating personality: {e}")
    
    def _format_chat_history(self, chat_history: list) -> str:
        """Format chat history into a readable string for analysis."""
        formatted = []
        for msg in chat_history:
            if msg["role"] != "system":  # Skip system messages
                formatted.append(f"{msg['role'].upper()}: {msg['content']}")
        return "\n".join(formatted)
    
    def _merge_data(self, current: Dict[str, Any], new: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recursively merge new data into current data.
        For lists, append new items that don't exist.
        For dictionaries, merge recursively.
        For other values, replace with new value.
        """
        if not isinstance(current, dict) or not isinstance(new, dict):
            return new

        merged = current.copy()
        for key, value in new.items():
            if key not in merged:
                merged[key] = value
            elif isinstance(value, list) and isinstance(merged[key], list):
                # For interests and preferences, we want to be more careful
                if key in ['interests', 'preferences']:
                    # Remove any conflicting preferences before adding new ones
                    # For example, if adding "likes milk chocolate", remove "likes dark chocolate"
                    merged[key] = [item for item in merged[key] 
                                 if not any(new_item.lower() in item.lower() 
                                          for new_item in value)]
                # Add new items only if they don't exist
                merged[key].extend(item for item in value 
                                 if not any(item.lower() in existing.lower() 
                                          for existing in merged[key]))
            elif isinstance(value, dict) and isinstance(merged[key], dict):
                merged[key] = self._merge_data(merged[key], value)
            else:
                merged[key] = value
        return merged
    
    def _apply_updates(self, updates: Dict[str, Any]) -> None:
        """Apply the updates to the respective JSON files."""
        for filename, new_data in updates.items():
            file_path = os.path.join(self.personality_manager.personality_dir, filename)
            print(f"\nUpdating {filename}...")
            
            try:
                # Read existing file
                with open(file_path, 'r') as f:
                    current_data = json.load(f)
                print(f"Current data in {filename}:", json.dumps(current_data, indent=2))
                
                # Update the data
                updated_data = self._merge_data(current_data, new_data)
                print(f"Updated data for {filename}:", json.dumps(updated_data, indent=2))
                
                # Write back to file
                with open(file_path, 'w') as f:
                    json.dump(updated_data, f, indent=2)
                print(f"Successfully updated {filename}")
                    
            except Exception as e:
                print(f"Error updating {filename}: {e}")