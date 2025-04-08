# chatbot/autonomous_chat.py
import time
import json
import os
from typing import List, Dict, Optional
from .chatbot import ChatBot
from dotenv import load_dotenv
from openai import OpenAI

class AutonomousChat:
    def __init__(self, delay: float = 2.0):
        self.delay = delay
        load_dotenv()
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OpenAI API key not found in environment variables or .env file")
        self.client = OpenAI(api_key=api_key)

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
        # print(f"\n{'='*50}")
        # print(f"Analyzing conversation for {listener.name}'s personality updates...")
        # print(f"Conversation segment length: {len(conversation_segment)} messages")
        
        # Separate messages by speaker
        speaker_messages = [msg for msg in conversation_segment if msg["speaker"] == speaker.name]
        listener_messages = [msg for msg in conversation_segment if msg["speaker"] == listener.name]
        
        # Create conversation pairs for analysis
        conversation_pairs = []
        for i in range(len(conversation_segment)):
            if i > 0:  # Skip the first message as it has no previous context
                prev_msg = conversation_segment[i-1]
                current_msg = conversation_segment[i]
                conversation_pairs.append({
                    "previous": prev_msg,
                    "current": current_msg
                })
        
        system_prompt = f"""You are a personality analyzer. Your task is to analyze this conversation and return ONLY a valid JSON object.

IMPORTANT: Your entire response must be a valid JSON object, nothing else.

Analyze how {speaker.name} presents themselves to {listener.name} and identify new information to add to {listener.name}'s understanding.

Consider the following aspects:
1. How {speaker.name} responds to {listener.name}'s messages
2. New interests or values revealed in the conversation
3. Emotional responses and communication style
4. Relationship dynamics and social preferences

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
                f"{pair['previous']['speaker']}: {pair['previous']['message']}\n{pair['current']['speaker']}: {pair['current']['message']}"
                for pair in conversation_pairs
            ])
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Analyze this conversation:\n\n{conversation_text}"}
            ]
            
            # print(f"\nSending conversation analysis request for {listener.name}...")
            
            # Get analysis from GPT
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=1000,
                temperature=0.7
            )
            
            response_content = response.choices[0].message.content
            # print("\nAnalysis received. Processing updates...")
            
            try:
                # Try to parse the JSON response
                updates = json.loads(response_content)
                # print(f"\nUpdates to be applied to {listener.name}'s personality:")
                # print(json.dumps(updates, indent=2))
                
                # Apply updates to listener's personality files
                for filename, new_data in updates.items():
                    try:
                        # Get current data from personality manager
                        current_data = listener.personality_manager.current_personality.get(filename, {})
                        
                        # Merge new data with current data
                        merged_data = self._merge_data(current_data, new_data)
                        
                        # Save the updated data
                        listener.personality_manager.save_personality_file(filename, merged_data)
                            
                        # print(f"\n✅ Successfully updated {listener.name}'s {filename}")
                        # print(f"Updated content preview:")
                        # print(json.dumps(merged_data, indent=2)[:500] + "...")
                        
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
        
        # print(f"{'='*50}\n")

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

    def start_conversation(self, bot1: ChatBot, bot2: ChatBot):
        """Start an autonomous conversation between two AI personalities."""
        print(f"\nStarting autonomous conversation between {bot1.name} and {bot2.name}...")
        print("Conversation will run continuously. Press Ctrl+C to stop.")
        
        turns = input("\nHow many turns? (default: 20): ")
        num_turns = int(turns) if turns.isdigit() else 20
        
        # Initialize conversation with a natural greeting
        initial_message = f"Hi {bot2.name}! It's so nice to see you again. How have you been?"
        print(f"\n{bot1.name}: {initial_message}")
        
        # Initialize conversation history
        conversation_history = [
            {"speaker": bot1.name, "message": initial_message}
        ]
        
        try:
            # First response from bot2
            response = bot2.get_response(initial_message, bot1.name)
            print(f"\n{bot2.name}: {response}")
            conversation_history.append({"speaker": bot2.name, "message": response})
            
            # Update relationship for bot2
            if hasattr(bot2, 'relationship_manager'):
                bot2.relationship_manager.update_relationship(
                    bot1.name,
                    [{"speaker": bot2.name, "message": response}]
                )
            
            # Main conversation loop
            for turn in range(1, num_turns):
                # Get the last message from the conversation history
                last_message = conversation_history[-1]
                
                # Determine current and other speaker based on last message
                if last_message["speaker"] == bot1.name:
                    current_speaker = bot2
                    other_speaker = bot1
                else:
                    current_speaker = bot1
                    other_speaker = bot2
                
                # Get response from current speaker
                message = current_speaker.get_response(last_message["message"], other_speaker.name)
                print(f"\n{current_speaker.name}: {message}")
                conversation_history.append({"speaker": current_speaker.name, "message": message})
                
                # Update relationship for current speaker
                if hasattr(current_speaker, 'relationship_manager'):
                    current_speaker.relationship_manager.update_relationship(
                        other_speaker.name,
                        [{"speaker": current_speaker.name, "message": message}]
                    )
                
                # Update personality files every 10 turns
                if turn % 10 == 0:
                    print(f"\nUpdating personality files for {current_speaker.name} and {other_speaker.name}...")
                    # Get the last 10 messages for each bot
                    bot1_messages = [msg for msg in conversation_history[-20:] if msg["speaker"] == bot1.name]
                    bot2_messages = [msg for msg in conversation_history[-20:] if msg["speaker"] == bot2.name]
                    
                    # Update personalities
                    self._update_personality_files(bot1, bot2, bot1_messages)
                    self._update_personality_files(bot2, bot1, bot2_messages)
                    print("Personality files updated successfully.")
                
                # Add a small delay between turns
                time.sleep(self.delay)
                
        except KeyboardInterrupt:
            print("\n\nConversation ended by user.")
        except Exception as e:
            print(f"\nError in conversation: {e}")

    def _create_system_message(self) -> str:
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
        if self.relationship_manager and self.other_name:
            relationship_data = self.relationship_manager.load_relationship(self.other_name)
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
   - After 2-3 exchanges on a single topic, naturally transition to a new subject
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