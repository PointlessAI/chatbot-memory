# chatbot/autonomous_chat.py
import time
import json
import os
from typing import List, Dict, Optional
from .chatbot import ChatBot

class AutonomousChat:
    def __init__(self, delay: float = 2.0):
        self.bot1 = ChatBot("jack")
        self.bot2 = ChatBot("lucy")
        self.delay = delay
        self.max_turns = 20
        self.conversation_history = []

    def _create_context_message(self, speaker_name: str, listener_name: str) -> str:
        """Create context message for the current speaker."""
        return f"""You are {speaker_name} having a natural conversation with {listener_name}.
        Important:
        - Respond naturally to what was just said
        - You don't need to use their name in every response
        - Let your personality shine through
        - React authentically to the content of their message
        - Feel free to change topics if it feels natural
        - Express emotions, thoughts, and opinions freely"""

    def _update_personality_files(self, speaker: ChatBot, listener: ChatBot, conversation_segment: List[Dict]):
        """Update the personality files based on the conversation."""
        print(f"\n{'='*50}")
        print(f"Analyzing conversation for {listener.name}'s personality updates...")
        print(f"Conversation segment length: {len(conversation_segment)} messages")
        
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
            
            print(f"\nSending conversation analysis request for {listener.name}...")
            
            # Get analysis from GPT
            response = listener.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=1000,
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
                        print(f"❌ Error updating {filename}: {e}")
                
            except json.JSONDecodeError as e:
                print(f"❌ Error parsing GPT response as JSON: {e}")
                print("Raw response was:", response_content)
        
        except Exception as e:
            print(f"❌ Error in personality update process: {e}")
        
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
        
        Example natural starters:
        - "The sunset is beautiful today, isn't it?"
        - "I've been thinking about that book you mentioned..."
        - "You won't believe what just happened!"
        - "Do you ever wonder about..."
        
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
                print(f"\n{current_speaker.name}: {current_message}")
                
                # Add current message to conversation segment
                message_data = {
                    "speaker": current_speaker.name,
                    "listener": next_speaker.name,
                    "message": current_message
                }
                self.conversation_history.append(message_data)
                conversation_segment.append(message_data)
                
                context = self._create_context_message(next_speaker.name, current_speaker.name)
                
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
                
                # Add response to conversation segment
                response_data = {
                    "speaker": next_speaker.name,
                    "listener": current_speaker.name,
                    "message": response_text
                }
                self.conversation_history.append(response_data)
                conversation_segment.append(response_data)
                
                # Update personalities after 5 messages
                if len(conversation_segment) >= 5:
                    print("\n" + "=" * 50)
                    print(f"Processing personality updates after {len(conversation_segment)} messages...")
                    print("Current conversation segment:")
                    for msg in conversation_segment:
                        print(f"{msg['speaker']}: {msg['message']}")
                    
                    print("\nUpdating personalities...")
                    self._update_personality_files(current_speaker, next_speaker, conversation_segment)
                    self._update_personality_files(next_speaker, current_speaker, conversation_segment)
                    print("=" * 50 + "\n")
                    
                    # Keep the last message for context
                    conversation_segment = [conversation_segment[-1]]
                
                current_speaker, next_speaker = next_speaker, current_speaker
                current_message = response_text
                
                time.sleep(self.delay)
                
            except Exception as e:
                print(f"\nError in conversation turn: {e}")
                break
        
        if conversation_segment:
            print("\nProcessing final conversation segment...")
            self._update_personality_files(self.bot1, self.bot2, conversation_segment)
            self._update_personality_files(self.bot2, self.bot1, conversation_segment)
        
        print("\n" + "=" * 50)
        print("Conversation ended.")