# chatbot/autonomous_chat.py
import time
from typing import Optional, List, Dict
import json
import os
from openai import OpenAI

# Import at module level to avoid circular imports
from chatbot import ChatBot

class AutonomousChat:
    def __init__(self, personality1_name: str = "jack", personality2_name: str = "lucy"):
        """Initialize two chatbots and manage their conversation."""
        print(f"\nInitializing conversation between {personality1_name} and {personality2_name}...")
        self.bot1 = ChatBot(personality1_name)
        self.bot2 = ChatBot(personality2_name)
        
        self.conversation_history = []
        self.max_turns = 20
        self.delay = 2
    
    def _create_context_message(self, speaker_name: str, listener_name: str) -> str:
        """Create a context message for the next response."""
        return f"""You are {speaker_name} having a natural, unscripted conversation with {listener_name}.
You have complete freedom to:
1. Start new topics that interest you
2. Share your thoughts and feelings
3. React to what {listener_name} says
4. Ask questions about things you're curious about
5. Express your personality freely
6. Bring up memories or past experiences
7. Change the subject if you want to

Remember:
- Stay true to your personality and background
- You can be as casual or serious as you naturally would be
- You can disagree or have different opinions
- You can show real emotions and reactions
- You can be spontaneous and unpredictable, just like in a real conversation

This is a genuine interaction between two individuals with their own personalities, not a scripted dialogue."""

    def _generate_first_message(self, speaker: ChatBot, listener: ChatBot) -> str:
        """Generate the first message to start the conversation."""
        system_prompt = f"""You are {speaker.name}. Generate a natural conversation opener to {listener.name}.
This could be anything - a greeting, a question, an observation, a thought you want to share.
Make it feel spontaneous and true to your personality.
Don't feel constrained - say whatever comes naturally to you as {speaker.name}."""

        try:
            response = speaker.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "system", "content": system_prompt}],
                max_tokens=100
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error generating first message: {e}")
            return f"Hi {listener.name}, how are you today?"

# chatbot/autonomous_chat.py
    def _update_personality_files(self, speaker: ChatBot, listener: ChatBot, conversation_segment: List[Dict]):
        """Update the personality files based on the conversation."""
        system_prompt = f"""You are a personality analyzer. Your task is to analyze this conversation and return ONLY a valid JSON object.

IMPORTANT: Your entire response must be a valid JSON object, nothing else.

Analyze how {speaker.name} presents themselves to {listener.name} and identify new information to add to {listener.name}'s understanding.

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
            "with_{speaker.name}": {{
                "interactions": ["new interaction 1"],
                "observed_traits": ["trait 1"]
            }}
        }}
    }}
}}

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
            
            # Get analysis from GPT
            response = listener.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=1000,
                temperature=0.7  # Add some creativity while keeping structure
            )
            
            response_content = response.choices[0].message.content
            print("\nGPT Analysis Response:", response_content)  # Debug print
            
            try:
                # Try to parse the JSON response
                updates = json.loads(response_content)
                print("\nParsed updates:", json.dumps(updates, indent=2))  # Debug print
                
                # Apply updates to listener's personality files
                for filename, new_data in updates.items():
                    if filename != "user-profile.json":  # Never update user profiles
                        file_path = os.path.join(listener.personality_manager.personality_dir, filename)
                        try:
                            # Read existing file
                            with open(file_path, 'r') as f:
                                current_data = json.load(f)
                            
                            # Update the data
                            updated_data = self._merge_data(current_data, new_data)
                            
                            # Write back to file
                            with open(file_path, 'w') as f:
                                json.dump(updated_data, f, indent=2)
                                
                            print(f"Successfully updated {listener.name}'s {filename}")
                            
                        except Exception as e:
                            print(f"Error updating {filename}: {e}")
                
            except json.JSONDecodeError as e:
                print(f"Error parsing GPT response as JSON: {e}")
                print("Raw response was:", response_content)
        
        except Exception as e:
            print(f"Error in personality update process: {e}")

    def start_conversation(self, num_turns: Optional[int] = None):
        """Start an autonomous conversation between the two chatbots."""
        if num_turns is not None:
            self.max_turns = num_turns
        
        print(f"\nStarting conversation between {self.bot1.name} and {self.bot2.name}...")
        print("=" * 50)
        
        # Generate initial message with a more natural prompt
        system_prompt = f"""You are {self.bot1.name}. Start a natural conversation with {self.bot2.name}.
        Important:
        - Be natural and varied in your conversation style
        - You don't need to start with a greeting if you don't want to
        - You can start with an observation, question, or statement
        - Express your personality through your unique way of speaking
        - Avoid formulaic greetings like "Hey [name]!"
        
        Speak naturally, as if you're in the middle of an ongoing relationship."""
        
        try:
            response = self.bot1.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "system", "content": system_prompt}],
                max_tokens=100
            )
            current_message = response.choices[0].message.content
        except Exception as e:
            print(f"Error generating initial message: {e}")
            current_message = "I've been thinking about something interesting lately..."
        
        current_speaker = self.bot1
        next_speaker = self.bot2
        
        conversation_segment = []
        
        for turn in range(self.max_turns):
            try:
                context = f"""You are {next_speaker.name} having a natural conversation with {current_speaker.name}.
                Important:
                - Respond naturally to what was just said
                - You don't need to use their name in every response
                - Let your personality shine through
                - React authentically to the content of their message
                - Feel free to change topics if it feels natural
                - Express emotions, thoughts, and opinions freely
                
                Previous message: {current_message}"""
                
                messages = [
                    {"role": "system", "content": context},
                    {"role": "user", "content": current_message}
                ]
                
                response = next_speaker.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    max_tokens=150
                )
                
                response_text = response.choices[0].message.content
                print(f"\n{next_speaker.name}: {response_text}")
                
                message_data = {
                    "speaker": next_speaker.name,
                    "listener": current_speaker.name,
                    "message": response_text
                }
                self.conversation_history.append(message_data)
                conversation_segment.append(message_data)
                
                if len(conversation_segment) >= 5:
                    print(f"\nUpdating personality files after {len(conversation_segment)} messages...")
                    self._update_personality_files(self.bot1, self.bot2, conversation_segment)
                    self._update_personality_files(self.bot2, self.bot1, conversation_segment)
                    conversation_segment = []
                
                current_speaker, next_speaker = next_speaker, current_speaker
                current_message = response_text
                
                time.sleep(self.delay)
                
            except Exception as e:
                print(f"\nError in conversation turn: {e}")
                break

    def _format_conversation(self, conversation_segment: List[Dict]) -> str:
        """Format conversation segment into readable text."""
        return "\n".join([
            f"{msg['speaker']}: {msg['message']}"
            for msg in conversation_segment
        ])

    def _merge_data(self, current: Dict, new: Dict) -> Dict:
        """Merge new data into current data, preserving existing information."""
        if not isinstance(current, dict) or not isinstance(new, dict):
            return new

        merged = current.copy()
        for key, value in new.items():
            if key not in merged:
                merged[key] = value
            elif isinstance(value, list) and isinstance(merged[key], list):
                merged[key].extend(item for item in value if item not in merged[key])
            elif isinstance(value, dict) and isinstance(merged[key], dict):
                merged[key] = self._merge_data(merged[key], value)
            else:
                merged[key] = value
        return merged