# chatbot.py
import os
import json
from dotenv import load_dotenv
from openai import OpenAI  # type: ignore
import datetime
import tiktoken  # Add this import

from personality_manager import PersonalityManager

class ChatBot:
    def __init__(self, personality_manager=None):
        """
        Initialize the chatbot with a personality manager.
        """
        self.personality_manager = personality_manager or PersonalityManager()
        self.current_personality = self.personality_manager.current_personality
        
        # Get name from core identity
        core_identity = self.current_personality.get('core-identity', {})
        self.name = core_identity.get('name', 'AI Assistant')
        self.entity = "AI Assistant"
        
        # Initialize fresh chat history
        self.chat_history = []
        self.chat_history_summary_count = 3
        
        # Load environment variables
        load_dotenv()
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("API key not found. Please set OPENAI_API_KEY in your .env file.")
        
        # Initialize OpenAI client
        self.client = OpenAI(api_key=self.api_key)
        
        # Initialize token counter
        self.total_tokens = 0
        
        # Initialize conversation memory
        self.conversation_memory = []
        
        # Load user profile
        user_profile = self.personality_manager.get_user_profile()
        user_name = user_profile.get('personal_info', {}).get('name', 'the user')
        
        # Create initial greeting based on previous interactions
        greeting = self._create_welcome_message(user_name, user_profile)
        
        # Start with a minimal system message and greeting
        self.chat_history = [
            {"role": "system", "content": self._create_json_system_prompt()},
            {"role": "assistant", "content": greeting}
        ]
        
        self.update_counter = 0
        self.message_count = 0  # Add message counter
        self.personality_update_interval = 5  # Update personality every 5 messages
        
        # Load initial personality
        self._load_personality()
        
        # Load user profile
        self.user_profile = self.personality_manager.get_user_profile()
        
        # Create initial greeting
        self.chat_history.append({
            "role": "assistant",
            "content": self._create_welcome_message(user_name, self.user_profile)
        })

    def _create_welcome_message(self, user_name: str, user_profile: dict) -> str:
        """Create a personalized welcome message based on personality and relationship."""
        # Get core identity and emotional traits
        core_identity = self.current_personality.get('core-identity', {})
        emotional = self.current_personality.get('emotional-framework', {})
        
        # Get relationship metrics
        relationship = user_profile.get('relationship', {})
        trust_level = relationship.get('trust_level', 0.0)
        emotional_bond = relationship.get('emotional_bond', 0.0)
        
        # Get communication style
        communication_style = emotional.get('communication_style', '')
        
        # Ensure user_name is not empty
        if not user_name or user_name == 'the user':
            user_name = "sir"  # Default respectful address if no name is available
        
        # Generate greeting based on relationship and personality
        if trust_level > 0.7 and emotional_bond > 0.7:
            return f"Good day, {user_name}. It's wonderful to see you again. How are you?"
        elif trust_level > 0.5 and emotional_bond > 0.5:
            return f"Hello, {user_name}. It's nice to see you. How are you today?"
        elif trust_level > 0.3 and emotional_bond > 0.3:
            return f"Greetings, {user_name}. Hello, how are you?"
        else:
            return f"Good day, {user_name}. How are you?"

    def _create_json_system_prompt(self):
        """Create a system prompt that includes the raw JSON content from each personality file."""
        prompt_parts = [
            "You are an AI assistant with the following personality defined in JSON format. ",
            "Use this information to maintain consistent character traits and behaviors in all interactions.\n"
        ]
        
        # List of personality files to include
        personality_files = [
            "core-identity.json",
            "emotional-framework.json",
            "cognitive-style.json",
            "social-dynamics.json",
            "interests-values.json",
            "behavioral-patterns.json",
            "memory-growth.json"
        ]
        
        # Read and include each personality file
        for file_name in personality_files:
            file_path = os.path.join(self.personality_manager.personality_dir, file_name)
            try:
                with open(file_path, 'r') as f:
                    content = json.load(f)
                    prompt_parts.append(f"\n=== {file_name} ===\n{json.dumps(content, indent=2)}")
            except Exception as e:
                print(f"Error reading {file_name}: {e}")
                continue
        
        # Add user profile with clear instructions
        user_profile_path = os.path.join(self.personality_manager.personality_dir, "user-profile.json")
        try:
            with open(user_profile_path, 'r') as f:
                user_profile = json.load(f)
                prompt_parts.extend([
                    "\n=== USER PROFILE ===",
                    "This is the user's personality and information. Use this to understand and adapt to the user:",
                    json.dumps(user_profile, indent=2),
                    "\nIMPORTANT: The above user profile contains information about the person you are talking to.",
                    "Use this information to personalize your responses and maintain context about the user.",
                    "Remember their preferences, shared history, and relationship status when interacting.",
                    "When asked about the user's interests, preferences, or characteristics, always refer to this profile.",
                    "For example, if asked 'what are my interests?', list the interests from the user's profile.",
                    "The user's interests are: " + ", ".join(user_profile.get('interests', []))
                ])
        except Exception as e:
            print(f"Error reading user profile: {e}")
        
        # Add conversation rules
        prompt_parts.extend([
            "\nCONVERSATION RULES:",
            "- Use the personality information above to maintain consistent character traits",
            "- Express personality through words and tone, not actions",
            "- Maintain appropriate decorum and respect",
            "- Consider the user's preferences and emotional state from their profile",
            "- Use the shared history to inform responses",
            "- Adapt communication style based on trust level and emotional bond",
            "- Be mindful of topics to avoid and favorite topics from the user's profile",
            "- Incorporate inside jokes and personal rituals when appropriate",
            "- Reference shared experiences and milestones naturally",
            "- Provide emotional support when needed",
            "- Maintain the character's personality traits and values consistently",
            "- When asked about the user's characteristics, always refer to the user profile",
            "- Never make up or assume information about the user - only use what's in the profile",
            "- If asked about user interests, always list the exact interests from the user profile"
        ])
        
        final_prompt = "\n".join(prompt_parts)
        print("\n=== SYSTEM PROMPT ===")
        print(final_prompt)
        print("=== END SYSTEM PROMPT ===\n")
        return final_prompt

    def _count_tokens(self, messages, model="gpt-4o-mini"):
        """
        Count tokens in messages using tiktoken.
        """
        try:
            encoding = tiktoken.encoding_for_model(model)
            num_tokens = 0
            for message in messages:
                num_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
                for key, value in message.items():
                    num_tokens += len(encoding.encode(value))
                    if key == "name":  # if there's a name, the role is omitted
                        num_tokens += -1  # role is always required and always 1 token
            num_tokens += 2  # every reply is primed with <im_start>assistant
            return num_tokens
        except Exception as e:
            print(f"Error counting tokens: {e}")
            return 0

    def _print_token_usage(self, model, messages, response):
        """
        Print token usage information.
        """
        input_tokens = self._count_tokens(messages, model)
        output_tokens = len(tiktoken.encoding_for_model(model).encode(response))
        total_tokens = input_tokens + output_tokens
        self.total_tokens += total_tokens
        
        print(f"\nToken Usage for {model}:")
        print(f"Input tokens: {input_tokens}")
        print(f"Output tokens: {output_tokens}")
        print(f"Total tokens for this request: {total_tokens}")
        print(f"Running total tokens: {self.total_tokens}\n")

    def summarize_chat_history(self, chat_history_string):
        """
        Summarizes the current conversation history using gpt-4o-mini for efficiency.
        """
        try:
            messages = [
                {"role": "system", "content": f"Summarize this conversation in 30 words or less, focusing on key points and emotional tone. Always use {self.name}'s name and specific personality traits: {self.personality_manager.get_personality_traits()}. Never use generic terms like 'the assistant'."},
                {"role": "user", "content": chat_history_string}
            ]
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=100
            )
            memory_summary = response.choices[0].message.content
            
            # Print token usage
            self._print_token_usage("gpt-4o-mini", messages, memory_summary)
            
            # Only update personality every 10 summaries to reduce API calls
            if len(self.chat_history) % 10 == 0:
                self.personality_manager.update_from_response(memory_summary, self.client)
            
            self.personality_manager.update_memory(memory_summary, self.name)
            
        except Exception as e:
            print(f"Error during summarization: {e}")
            return "Error summarizing chat history."
        
        return memory_summary

    def _update_personality_from_conversation(self, user_input: str, assistant_response: str):
        """Update personality files based on conversation content."""
        try:
            # Create a prompt to analyze the conversation for personality updates
            messages = [
                {"role": "system", "content": (
                    "Analyze this conversation and identify any new personality traits, interests, or information "
                    "that should be added to the personality files. Return a JSON object with updates for each file. "
                    "Format: {\"file_name\": {\"field\": [\"new_value\"]}}. "
                    "Only include fields that have new information. "
                    "For example, if the assistant mentions liking tennis, add it to interests-values.json. "
                    "If the user mentions liking tennis, add it to user-profile.json. "
                    "Be specific and accurate in your updates. "
                    "Your response must be a valid JSON object, nothing else."
                )},
                {"role": "user", "content": f"User: {user_input}\nAssistant: {assistant_response}"}
            ]
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.1  # Lower temperature for more consistent JSON output
            )
            
            # Clean the response to ensure it's valid JSON
            content = response.choices[0].message.content.strip()
            # Remove any markdown code block markers if present
            content = content.replace('```json', '').replace('```', '').strip()
            
            try:
                updates = json.loads(content)
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON response: {e}")
                print(f"Raw response: {content}")
                return
            
            # Process updates for each file
            for file_name, content in updates.items():
                file_path = os.path.join(self.personality_manager.personality_dir, file_name)
                if os.path.exists(file_path):
                    # Load current content
                    with open(file_path, 'r') as f:
                        current_data = json.load(f)
                    
                    # Update the content while preserving structure
                    self._deep_update(current_data, content)
                    
                    # Save the updated file
                    with open(file_path, 'w') as f:
                        json.dump(current_data, f, indent=2)
                    
                    print(f"Updated {file_name} with new information")
            
            # Reload personality after updates
            self._load_personality()
            
        except Exception as e:
            print(f"Error updating personality from conversation: {e}")

    def _deep_update(self, current: dict, new: dict):
        """Recursively update a dictionary with new values."""
        for key, value in new.items():
            if key in current:
                if isinstance(current[key], dict) and isinstance(value, dict):
                    self._deep_update(current[key], value)
                elif isinstance(current[key], list) and isinstance(value, list):
                    # For lists, extend with new unique items
                    current[key].extend([item for item in value if item not in current[key]])
                else:
                    current[key] = value
            else:
                current[key] = value

    def generate_response(self, user_input: str) -> str:
        """Generate a response using gpt-4o-mini for most interactions."""
        try:
            # Update chat history
            self.chat_history.append({"role": "user", "content": user_input})
            
            # Prepare messages with minimal context
            messages = [
                {"role": "system", "content": self._create_json_system_prompt()}
            ]
            
            # Add recent memories to context
            if self.conversation_memory:
                recent_memories = self.conversation_memory[-3:]
                for memory in recent_memories:
                    messages.append({"role": "system", "content": f"Recent memory: {memory['text']}"})
            
            # Add only the last 3 messages from chat history
            messages.extend(self.chat_history[-3:])
            
            # Use gpt-4o-mini for regular responses
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.7,
                max_tokens=300
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # Print token usage
            self._print_token_usage("gpt-4o-mini", messages, response_text)
            
            # Update chat history
            self.chat_history.append({"role": "assistant", "content": response_text})
            
            # Update personality based on conversation
            self._update_personality_from_conversation(user_input, response_text)
            
            # Summarize chat history if it gets too long
            if len(self.chat_history) > self.chat_history_summary_count:
                self._summarize_chat_history()
            
            return response_text
            
        except Exception as e:
            print(f"Error generating response: {e}")
            return "I apologize, but I encountered an error while processing your request."

    def _update_user_profile_from_conversation(self, user_input: str, response_text: str):
        """Extract and update user information and relationship details from the conversation."""
        try:
            # Create a prompt to extract user information and relationship updates
            messages = [
                {"role": "system", "content": (
                    "Analyze this conversation for: "
                    "1. New information about the user (name, traits, preferences, interests, occupation) "
                    "2. Relationship updates (trust level, emotional bond, status) "
                    "3. Shared history (topics, emotional support, milestones) "
                    "4. New interests or hobbies mentioned by either party "
                    "Return a JSON object with updates to the user profile. "
                    "For relationship metrics, use values between 0.0 and 1.0. "
                    "Include any new nicknames, inside jokes, or personal rituals. "
                    "Your response must be a valid JSON object with the following structure: "
                    '{"personal_info": {"name": "", "traits": [], "preferences": [], "interests": [], "occupation": ""}, '
                    '"relationship": {"trust_level": 0.0, "emotional_bond": 0.0, "status": ""}, '
                    '"shared_history": {"topics": [], "emotional_support": [], "milestones": []}}'
                )},
                {"role": "user", "content": f"User: {user_input}\nAssistant: {response_text}"}
            ]
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages
            )
            
            try:
                # Replace single quotes with double quotes in the response
                json_str = response.choices[0].message.content.replace("'", '"')
                updates = json.loads(json_str)
                
                # Get current profile
                current_profile = self.personality_manager.get_user_profile()
                
                # Update personal info
                if 'personal_info' in updates:
                    for key, value in updates['personal_info'].items():
                        if key in current_profile['personal_info']:
                            if isinstance(current_profile['personal_info'][key], list):
                                # For lists, extend with new unique items
                                if isinstance(value, list):
                                    current_profile['personal_info'][key].extend(
                                        [item for item in value if item not in current_profile['personal_info'][key]]
                                    )
                                else:
                                    if value not in current_profile['personal_info'][key]:
                                        current_profile['personal_info'][key].append(value)
                            else:
                                # For non-list values, only update if not empty
                                if value:
                                    current_profile['personal_info'][key] = value
                
                # Update relationship
                if 'relationship' in updates:
                    for key, value in updates['relationship'].items():
                        if key in current_profile['relationship']:
                            if key in ['trust_level', 'emotional_bond']:
                                # For numeric values, take the maximum
                                current_profile['relationship'][key] = max(
                                    current_profile['relationship'][key],
                                    float(value)
                                )
                            else:
                                # For non-numeric values, only update if not empty
                                if value:
                                    current_profile['relationship'][key] = value
                
                # Update shared history
                if 'shared_history' in updates:
                    for key, value in updates['shared_history'].items():
                        if key in current_profile['shared_history']:
                            if isinstance(current_profile['shared_history'][key], list):
                                # For lists, extend with new unique items
                                if isinstance(value, list):
                                    current_profile['shared_history'][key].extend(
                                        [item for item in value if item not in current_profile['shared_history'][key]]
                                    )
                                else:
                                    if value not in current_profile['shared_history'][key]:
                                        current_profile['shared_history'][key].append(value)
                
                # Update last_updated timestamp
                current_profile['last_updated'] = datetime.datetime.now().isoformat()
                
                # Save the updated profile
                self.personality_manager.update_user_profile(current_profile)
                
                # Update the in-memory profile
                self.user_profile = current_profile
                
                # Also update interests in the personality files
                if 'personal_info' in updates and 'interests' in updates['personal_info']:
                    new_interests = updates['personal_info']['interests']
                    if isinstance(new_interests, list):
                        # Update interests in the personality files
                        self._update_personality_interests(new_interests)
                
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON response: {e}")
                print(f"Raw response: {response.choices[0].message.content}")
            except Exception as e:
                print(f"Error updating user profile: {e}")
                print(f"Full error details: {str(e)}")
                
        except Exception as e:
            print(f"Error in profile update process: {e}")

    def _update_personality_interests(self, new_interests: list):
        """Update interests in the personality files."""
        try:
            # Get current interests from personality files
            interests_file = os.path.join(self.personality_manager.personality_dir, 'interests-values.json')
            if os.path.exists(interests_file):
                with open(interests_file, 'r') as f:
                    interests_data = json.load(f)
                
                # Update interests list
                current_interests = interests_data.get('interests', [])
                for interest in new_interests:
                    if interest not in current_interests:
                        current_interests.append(interest)
                
                interests_data['interests'] = current_interests
                
                # Save updated interests
                with open(interests_file, 'w') as f:
                    json.dump(interests_data, f, indent=2)
                
                # Reload personality to reflect changes
                self._load_personality()
                
        except Exception as e:
            print(f"Error updating personality interests: {e}")

    def start_chat(self):
        """
        Starts an interactive chat session.
        """
        print(f"Chat with {self.name}. Type 'exit' to quit.")
        while True:
            user_input = input("User: ")
            if user_input.lower() == "exit":
                print(f"{self.name}: Goodbye!")
                break
            response = self.generate_response(user_input)
            print(f"{self.name}:", response)

    def _summarize_chat_history(self):
        """Summarizes the chat history with focus on relationship aspects."""
        try:
            chat_history_string = "\n".join(
                [f"{entry['role']}: {entry['content']}" for entry in self.chat_history]
            )
            
            messages = [
                {"role": "system", "content": (
                    f"Summarize this conversation in 30 words or less, focusing on: "
                    f"1. Emotional connection and relationship dynamics "
                    f"2. Important personal details about the user "
                    f"3. Any new shared experiences or inside jokes "
                    f"Always use {self.name}'s name and specific personality traits. "
                    f"Never use generic terms like 'the assistant'. "
                    f"Remember: {self.name} is the servant, the user is the developer. "
                    f"Maintain this role separation in the summary."
                )},
                {"role": "user", "content": chat_history_string}
            ]
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=100
            )
            
            summary = response.choices[0].message.content.strip()
            
            # Print token usage
            self._print_token_usage("gpt-4o-mini", messages, summary)
            
            # Update memory with the summary
            self.personality_manager.update_memory(summary, self.name)
            
            # Add the summary to conversation memory
            self.conversation_memory.append({
                "text": summary,
                "timestamp": datetime.datetime.now().isoformat()
            })
            
            # Update memory growth with the new summary
            self.personality_manager._update_memory_growth(summary)
            
            # Reset chat history but keep the last user message
            last_user_message = self.chat_history[-1]
            self.chat_history = [last_user_message]
            
        except Exception as e:
            print(f"Error summarizing chat history: {e}")
            self.chat_history = self.chat_history[-3:]

    def _load_personality(self):
        """Load the current personality from files."""
        self.personality = self.personality_manager.current_personality
        self.core_identity = self.personality.get("core-identity", {})
        self.emotional_framework = self.personality.get("emotional-framework", {})
        self.cognitive_style = self.personality.get("cognitive-style", {})
        self.social_dynamics = self.personality.get("social-dynamics", {})
        self.interests_values = self.personality.get("interests-values", {})
        self.behavioral_patterns = self.personality.get("behavioral-patterns", {})

    def _update_personality(self):
        """Update personality based on conversation and reload it."""
        try:
            # Get the last 5 messages for personality analysis
            recent_messages = self.chat_history[-5:] if len(self.chat_history) >= 5 else self.chat_history
            
            # Create a prompt for personality analysis
            messages = [
                {"role": "system", "content": (
                    f"Analyze these recent messages and update {self.name}'s personality traits. "
                    "Focus on emotional responses, communication style, and behavioral patterns. "
                    "Return a JSON object with updates for each personality file. "
                    "Your response must be a valid JSON object."
                )},
                {"role": "user", "content": json.dumps(recent_messages)}
            ]
            
            # Get personality updates from GPT
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages
            )
            
            try:
                # Parse the updates
                updates = json.loads(response.choices[0].message.content)
                
                # Update each personality file
                for file_name, content in updates.items():
                    file_path = os.path.join(self.personality_manager.personality_dir, f"{file_name}.json")
                    if os.path.exists(file_path):
                        with open(file_path, 'r') as f:
                            current_data = json.load(f)
                        
                        # Update the content while preserving structure
                        self._deep_update(current_data, content)
                        
                        # Save the updated file
                        with open(file_path, 'w') as f:
                            json.dump(current_data, f, indent=2)
                
                # Reload the personality
                self._load_personality()
                
            except json.JSONDecodeError as e:
                print(f"Error parsing personality updates: {e}")
                print(f"Raw response: {response.choices[0].message.content}")
            
        except Exception as e:
            print(f"Error updating personality: {e}")

    def _create_system_prompt(self) -> str:
        """Create a system prompt that defines the character's identity and communication style."""
        # Get core identity
        core_identity = self.current_personality.get('core-identity', {})
        name = core_identity.get('name', '')
        age = core_identity.get('age', '')
        role = core_identity.get('role', '')
        background = core_identity.get('background', '')
        
        # Get emotional framework
        emotional = self.current_personality.get('emotional-framework', {})
        emotional_traits = emotional.get('traits', [])
        emotional_style = emotional.get('communication_style', '')
        
        # Get social dynamics
        social = self.current_personality.get('social-dynamics', {})
        social_roles = social.get('social_roles', [])
        interaction_patterns = social.get('interaction_patterns', [])
        
        # Get behavioral patterns
        behavioral = self.current_personality.get('behavioral-patterns', {})
        habits = behavioral.get('habits', [])
        routines = behavioral.get('daily_routines', {}).get('work', [])
        
        # Get interests and values
        interests = self.current_personality.get('interests-values', {})
        core_values = interests.get('core_values', [])
        interests_list = interests.get('interests', [])
        
        # Construct the prompt dynamically
        prompt_parts = []
        
        # Add core identity
        if name and age and role:
            prompt_parts.append(f"You are {name}, a {age}-year-old {role}.")
        if background:
            prompt_parts.append(f"Background: {background}")
            
        # Add emotional framework
        if emotional_traits:
            prompt_parts.append(f"Emotional traits: {', '.join(emotional_traits)}")
        if emotional_style:
            prompt_parts.append(f"Communication style: {emotional_style}")
            
        # Add social dynamics
        if social_roles:
            prompt_parts.append(f"Social roles: {', '.join(social_roles)}")
        if interaction_patterns:
            prompt_parts.append(f"Interaction patterns: {', '.join(interaction_patterns)}")
            
        # Add behavioral patterns
        if habits:
            prompt_parts.append(f"Habits: {', '.join(habits)}")
        if routines:
            prompt_parts.append(f"Daily routines: {', '.join(routines)}")
            
        # Add interests and values
        if core_values:
            prompt_parts.append(f"Core values: {', '.join(core_values)}")
        if interests_list:
            prompt_parts.append(f"Interests: {', '.join(interests_list)}")
            
        # Add general instructions
        prompt_parts.append("You should respond naturally and conversationally, without using meta actions or descriptions.")
        prompt_parts.append("Focus on expressing your personality through your words and tone, not through actions.")
        prompt_parts.append("Maintain appropriate decorum and respect in all interactions.")
        
        return " ".join(part for part in prompt_parts if part.strip())

    def chat(self, user_message: str) -> str:
        """Process a user message and return a response."""
        try:
            # Add user message to history
            self.chat_history.append({"role": "user", "content": user_message})
            self.message_count += 1
            
            # Update personality every 5 messages
            if self.message_count % self.personality_update_interval == 0:
                self._update_personality()
            
            # Create system prompt with current personality
            system_prompt = self._create_system_prompt()
            
            # Get response from GPT
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    *self.chat_history
                ]
            )
            
            # Get the response content
            assistant_message = response.choices[0].message.content
            
            # Add to chat history
            self.chat_history.append({"role": "assistant", "content": assistant_message})
            
            # Update conversation memory
            self._update_conversation_memory(user_message, assistant_message)
            
            return assistant_message
            
        except Exception as e:
            print(f"Error in chat: {e}")
            return "I apologize, but I'm having trouble processing that right now. Could you please try again?"