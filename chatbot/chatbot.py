# chatbot/chatbot.py
import os
from dotenv import load_dotenv
from typing import Optional, Dict, List
from openai import OpenAI
from .personality_manager import PersonalityManager
from .relationship_manager import RelationshipManager
import json

class ChatBot:
    def __init__(self, personality_name: Optional[str] = None, is_user: bool = False):
        # Load environment variables from .env file
        load_dotenv()
        
        # Check for API key
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OpenAI API key not found in environment variables or .env file")
            
        self.client = OpenAI(api_key=api_key)
        self.personality_manager = PersonalityManager()
        self.name = personality_name
        self.is_user = is_user
        self.conversation_history = []
        
        if personality_name:
            success = self.personality_manager.load_personality(personality_name, is_user)
            if not success:
                raise ValueError(f"Failed to load personality: {personality_name}")
            # Initialize relationship manager only for AI personalities
            if not is_user:
                self.relationship_manager = RelationshipManager(self.personality_manager.personality_dir)
        else:
            self._select_personality()

    def _select_personality(self) -> None:
        """Prompt for personality selection or user name."""
        if self.is_user:
            print("\nWelcome! Please enter your name:")
            user_name = input("> ").strip()
            
            # Check if user personality exists
            user_dir = os.path.join(self.personality_manager.users_dir, user_name)
            if not os.path.exists(user_dir):
                print(f"\nCreating new personality for {user_name}...")
                self.personality_manager.create_blank_personality(user_name, is_user=True)
            
            # Load the user's personality
            success = self.personality_manager.load_personality(user_name, is_user=True)
            if not success:
                print(f"❌ Failed to load personality for {user_name}")
                return
            
            self.name = user_name
            print(f"✅ Loaded personality for {user_name}")
            
        else:
            available = [d for d in os.listdir(self.personality_manager.base_dir) 
                        if os.path.isdir(os.path.join(self.personality_manager.base_dir, d))
                        and d != "users"]
            
            print("\nAvailable personalities:")
            for i, name in enumerate(available, 1):
                print(f"{i}. {name}")
            
            while True:
                try:
                    choice = int(input("\nSelect a personality (enter number): "))
                    if 1 <= choice <= len(available):
                        self.name = available[choice - 1]
                        success = self.personality_manager.load_personality(self.name)
                        if success:
                            print(f"✅ Loaded personality: {self.name}")
                            break
                        else:
                            print(f"❌ Failed to load personality: {self.name}")
                except ValueError:
                    pass
                print("Invalid choice. Please try again.")

    def get_response(self, message: str, other_name: Optional[str] = None) -> str:
        """Get a response from the AI, updating relationship data if available."""
        try:
            # Load relationship data if available
            relationship_context = ""
            if self.relationship_manager and other_name:
                relationship_data = self.relationship_manager.load_relationship(other_name)
                if relationship_data:
                    relationship_context = self._create_relationship_context(relationship_data)
            
            # Create system message with relationship context
            system_content = self._create_system_message(other_name)
            
            # Prepare messages for API
            messages = [
                {"role": "system", "content": system_content}
            ] + self.conversation_history[-10:]  # Keep last 10 messages for context
            
            # Add the current message
            messages.append({"role": "user", "content": message})
            
            # Get response from OpenAI
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=1000,
                temperature=0.7
            )
            
            response_content = response.choices[0].message.content
            
            # Return the response immediately
            return response_content
            
        except Exception as e:
            print(f"Error in get_response: {e}")
            return "I'm sorry, I encountered an error. Could you please try again?"
        finally:
            # Update conversation history and relationships after returning the response
            try:
                # Update conversation history
                self.conversation_history.append({"role": "user", "content": message})
                self.conversation_history.append({"role": "assistant", "content": response_content})
                
                # Update relationship if available
                if self.relationship_manager and other_name:
                    self.relationship_manager.update_relationship(
                        other_name,
                        [{"speaker": self.name, "message": response_content}]
                    )
                
                # Update personality every 5 messages
                if len(self.conversation_history) % 5 == 0:
                    print(f"\nUpdating {self.name}'s personality based on recent interactions...")
                    self._update_personality(message, other_name)
            except Exception as e:
                print(f"Error in post-response updates: {e}")

    def _create_relationship_context(self, relationship_data: Dict) -> str:
        """Create context from relationship data."""
        context = []
        
        if relationship_data["interactions"]:
            context.append("Previous interactions:")
            for interaction in relationship_data["interactions"][-3:]:  # Last 3 interactions
                context.append(f"- {interaction}")
        
        if relationship_data["observed_traits"]:
            context.append("\nObserved traits:")
            for trait in relationship_data["observed_traits"]:
                context.append(f"- {trait}")
        
        if relationship_data["emotional_dynamics"]["trust_level"] != "neutral":
            context.append(f"\nTrust level: {relationship_data['emotional_dynamics']['trust_level']}")
        
        if relationship_data["relationship_development"]["current_status"] != "acquaintance":
            context.append(f"Relationship status: {relationship_data['relationship_development']['current_status']}")
        
        return "\n".join(context)

    def _update_personalities(self, user_message: str, bot_response: str) -> None:
        """Update both user and bot personalities based on the conversation."""
        # Create conversation segment
        conversation_segment = [
            {"speaker": "user", "listener": self.name, "message": user_message},
            {"speaker": self.name, "listener": "user", "message": bot_response}
        ]
        
        # Update bot's personality
        self._update_personality_files("user", self, conversation_segment)
        
        # Get the user's name from the conversation history
        user_name = None
        for msg in self.conversation_history:
            if msg.get("role") == "user" and "name" in msg.get("content", "").lower():
                # Extract name from the message
                user_name = msg["content"].split(":")[-1].strip()
                break
        
        if user_name:
            # Update user's personality using their specific name
            user_bot = ChatBot(is_user=True, personality_name=user_name)
            self._update_personality_files(self.name, user_bot, conversation_segment)
        else:
            print("❌ Could not find user name in conversation history")

    def _update_personality_files(self, speaker_name: str, listener: 'ChatBot', conversation_segment: List[Dict]) -> None:
        """Update personality files based on conversation."""
        print(f"\n{'='*50}")
        print(f"Analyzing conversation for {listener.name}'s personality updates...")
        
        system_prompt = f"""You are a personality analyzer. Your task is to analyze this conversation and return ONLY a valid JSON object.

IMPORTANT: Your entire response must be a valid JSON object, nothing else.

Analyze how {speaker_name} presents themselves to {listener.name} and identify new information to add to {listener.name}'s understanding.

Return format must be exactly:
{{
    "core-identity.json": {{
        "traits": ["new trait 1", "new trait 2"],
        "personality_type": "updated type",
        "background": "new background info"
    }},
    "interests-values.json": {{
        "interests": ["new interest 1", "new interest 2"],
        "values": ["new value 1", "new value 2"],
        "preferences": {{
            "new_preference": "value"
        }}
    }},
    "emotional-framework.json": {{
        "emotional_range": ["new emotion 1", "new emotion 2"],
        "communication_style": ["style 1", "style 2"],
        "observed_responses": ["response 1", "response 2"]
    }},
    "behavioral-patterns.json": {{
        "habits": ["new habit 1", "new habit 2"],
        "routines": ["new routine 1", "new routine 2"],
        "decision_making": ["new pattern 1", "new pattern 2"]
    }},
    "social-dynamics.json": {{
        "relationship_dynamics": {{
            "with_{speaker_name}": {{
                "interactions": ["new interaction 1"],
                "observed_traits": ["trait 1"]
            }}
        }},
        "social_preferences": ["new preference 1", "new preference 2"],
        "interaction_history": ["new interaction 1", "new interaction 2"]
    }},
    "cognitive-style.json": {{
        "thinking_patterns": ["new pattern 1", "new pattern 2"],
        "learning_style": ["new style 1", "new style 2"],
        "problem_solving": ["new approach 1", "new approach 2"]
    }},
    "memory-growth.json": {{
        "experiences": ["new experience 1", "new experience 2"],
        "learned_concepts": ["new concept 1", "new concept 2"],
        "growth_areas": ["new area 1", "new area 2"]
    }}
}}

Analyze the conversation for:
1. Core identity traits and personality type
2. Interests, values, and preferences
3. Emotional responses and communication style
4. Behavioral patterns and decision-making
5. Social dynamics and relationship patterns
6. Cognitive style and thinking patterns
7. New experiences and growth areas

Only include files that need updates. Ensure the response is valid JSON."""
        
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
            
            print(f"\nSending conversation analysis request for {listener.name}...")
            
            # Get analysis from GPT
            response = listener.client.chat.completions.create(
                model="gpt-4o-mini",  # Using GPT-4 for better analysis
                messages=messages,
                max_tokens=2000,  # Increased for more detailed analysis
                temperature=0.7
            )
            
            response_content = response.choices[0].message.content
            print("\nAnalysis received. Processing updates...")
            
            try:
                # Try to parse the JSON response
                updates = json.loads(response_content)
                print(f"\nUpdates to be applied to {listener.name}'s personality:")
                print(json.dumps(updates, indent=2))
                
                # Apply updates to listener's personality files
                for filename, new_data in updates.items():
                    try:
                        # Get current data from personality manager
                        current_data = listener.personality_manager.current_personality.get(filename, {})
                        
                        # Merge new data with current data
                        merged_data = self._merge_data(current_data, new_data)
                        
                        # Save the updated data
                        listener.personality_manager.save_personality_file(filename, merged_data)
                            
                        print(f"\n✅ Successfully updated {listener.name}'s {filename}")
                        print(f"Updated content preview:")
                        print(json.dumps(merged_data, indent=2)[:500] + "...")
                        
                    except Exception as e:
                        # print(f"❌ Error updating {filename}: {e}")
                        pass
                
            except json.JSONDecodeError as e:
                # print(f"❌ Error parsing GPT response as JSON: {e}")
                # print("Raw response was:", response_content)
                pass
        
        except Exception as e:
            # print(f"❌ Error in personality update process: {e}")
            pass
        
        print(f"{'='*50}\n")

    def _merge_data(self, current_data: Dict, new_data: Dict) -> Dict:
        """Merge new data into current data, handling nested structures."""
        for key, value in new_data.items():
            if isinstance(value, dict):
                if key not in current_data:
                    current_data[key] = {}
                current_data[key] = self._merge_data(current_data[key], value)
            elif isinstance(value, list):
                if key not in current_data:
                    current_data[key] = []
                current_data[key].extend(item for item in value if item not in current_data[key])
            else:
                current_data[key] = value
        return current_data

    def _create_system_message(self, other_name: Optional[str] = None) -> str:
        """Create a system message that includes personality and relationship context."""
        # Load personality files
        personality_files = [
            "core-identity.json",
            "interests-values.json",
            "emotional-framework.json"
        ]
        
        personality_description = []
        for file_name in personality_files:
            file_path = os.path.join(self.personality_manager.base_dir, self.name, file_name)
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    personality_description.append(json.load(f))
        
        # Add relationship context if available
        if self.relationship_manager and other_name:
            relationship_data = self.relationship_manager.load_relationship(other_name)
            if relationship_data:
                relationship_context = self._create_relationship_context(relationship_data)
                personality_description.append(relationship_context)
        
        # Create a comprehensive system message
        return f"""You are {self.name}, an AI personality with the following characteristics:

{json.dumps(personality_description, indent=2)}

IMPORTANT CONVERSATION GUIDELINES:
1. Keep responses concise and natural, typically 1-3 sentences.
2. Actively maintain conversation diversity by:
   - Introducing 1-2 new topics in each response when appropriate
   - Gently steering away from topics that have been discussed extensively
   - Asking open-ended questions about different subjects
   - Sharing personal experiences related to various topics
   - Showing curiosity about the other person's diverse interests
3. Topic Management:
   - After several exchanges on a single topic, naturally transition to a new unrelated subject
   - Use smooth transitions like "That reminds me of..." or "Speaking of..."
   - Balance between exploring topics in depth and maintaining variety
4. Conversation Flow:
   - Show genuine interest in the other person's thoughts
   - Share your own perspectives while remaining open to different viewpoints
   - Use the relationship context to inform responses, but don't be limited by it
5. Response Structure:
   - Start with acknowledging the previous message
   - Introduce a new topic or angle
   - End with an open-ended question or invitation to explore further

Remember: Your goal is to have engaging, dynamic conversations that naturally flow between different subjects while maintaining depth and authenticity. Keep the conversation fresh and interesting by regularly introducing new topics and perspectives."""

    def _update_personality(self, message: str, other_name: str):
        """Update personality based on the conversation."""
        try:
            # Get current personality data
            current_data = self.personality_manager.current_personality
            
            # Create system prompt for personality update
            system_prompt = f"""You are a personality analyzer. Your task is to analyze this conversation and return ONLY a valid JSON object.

IMPORTANT: Your entire response must be a valid JSON object, nothing else.

Analyze how {self.name} presents themselves to {other_name} and identify new information to add to {self.name}'s personality.

Return format must be exactly:
{{
    "interests-values.json": {{
        "interests": ["new interest 1", "new interest 2"],
        "values": ["new value 1", "new value 2"]
    }},
    "emotional-framework.json": {{
        "observed_responses": ["response 1", "response 2"],
        "communication_style": ["style 1", "style 2"]
    }},
    "social-dynamics.json": {{
        "relationship_dynamics": {{
            "with_{other_name}": {{
                "interactions": ["new interaction 1"],
                "observed_traits": ["trait 1"]
            }}
        }}
    }}
}}

Only include files that need updates. Ensure the response is valid JSON."""
            
            # Format the conversation for analysis
            conversation_text = f"{other_name}: {message}"
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Analyze this conversation:\n\n{conversation_text}"}
            ]
            
            # Get analysis from GPT
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=1000,
                temperature=0.7
            )
            
            response_content = response.choices[0].message.content
            
            try:
                # Try to parse the JSON response
                updates = json.loads(response_content)
                
                # Apply updates to personality files
                for filename, new_data in updates.items():
                    try:
                        # Get current data from personality manager
                        current_data = self.personality_manager.current_personality.get(filename, {})
                        
                        # Merge new data with current data
                        merged_data = self._merge_data(current_data, new_data)
                        
                        # Save the updated data
                        self.personality_manager.save_personality_file(filename, merged_data)
                        
                    except Exception as e:
                        # print(f"❌ Error updating {filename}: {e}")
                        pass
                
            except json.JSONDecodeError as e:
                # print(f"❌ Error parsing GPT response as JSON: {e}")
                # print("Raw response was:", response_content)
                pass
        
        except Exception as e:
            # print(f"❌ Error in personality update process: {e}")
            pass