# chatbot/chatbot.py
import os
from dotenv import load_dotenv
from openai import OpenAI
from typing import Optional, Dict

from .personality_manager import PersonalityManager  # Update this import
from .token_manager import TokenManager
from .prompt_manager import PromptManager
from .memory_manager import MemoryManager
from .personality_updater import PersonalityUpdater
from .chat_utils import create_welcome_message

# chatbot/chatbot.py
class ChatBot:
    def __init__(self, personality_name: Optional[str] = None):
        """
        Initialize the chatbot with an optional personality name.
        If no personality is specified, the user will be prompted to choose one.
        """
        self.personality_manager = PersonalityManager()
        
        if not personality_name:
            personality_name = self._select_personality()
        
        if not self.personality_manager.load_personality(personality_name):
            raise ValueError(f"Failed to load personality: {personality_name}")
        
        self.current_personality = self.personality_manager.current_personality
        
        # Get name from core identity
        core_identity = self.current_personality.get('core-identity', {})
        self.name = core_identity.get('name', 'AI Assistant')
        
        # Initialize OpenAI client
        load_dotenv()
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("API key not found. Please set OPENAI_API_KEY in your .env file.")
        self.client = OpenAI(api_key=self.api_key)
        
        # Initialize managers
        self.token_manager = TokenManager()
        self.prompt_manager = PromptManager(self.personality_manager)
        self.memory_manager = MemoryManager(self.client, self.personality_manager, self.name)
        self.personality_updater = PersonalityUpdater(self.personality_manager)
        
        # Initialize chat
        self._initialize_chat()
        
        self.update_counter = 0
        self.message_count = 0
        self.personality_update_interval = 5
    
    def _select_personality(self) -> str:
        """Prompt the user to select a personality."""
        while True:
            print("\nAvailable personalities:")
            personalities = self.personality_manager.list_available_personalities()
            for i, name in enumerate(personalities, 1):
                print(f"{i}. {name}")
            
            try:
                choice = input("\nSelect a personality (enter number): ").strip()
                idx = int(choice) - 1
                if 0 <= idx < len(personalities):
                    return personalities[idx]
                else:
                    print("Invalid selection. Please try again.")
            except ValueError:
                print("Please enter a valid number.")
    
    def _initialize_chat(self):
        user_profile = self.personality_manager.get_user_profile()
        user_name = user_profile.get('personal_info', {}).get('name', 'the user')
        
        welcome_message = create_welcome_message(
            user_name,
            user_profile,
            self.current_personality.get('core-identity', {}),
            self.current_personality.get('emotional-framework', {})
        )
        
        self.chat_history = [
            {"role": "system", "content": self.prompt_manager.create_json_system_prompt()},
            {"role": "assistant", "content": welcome_message}
        ]
    
    def chat(self, user_input: str) -> str:
        # Add user message to chat history
        self.chat_history.append({"role": "user", "content": user_input})
        
        try:
            # Get response from OpenAI
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=self.chat_history,
                max_tokens=1000
            )
            
            assistant_response = response.choices[0].message.content
            
            # Add assistant response to chat history
            self.chat_history.append({"role": "assistant", "content": assistant_response})
            
            # Update token usage
            self.token_manager.print_token_usage("gpt-4o-mini", self.chat_history, assistant_response)
            
            # Update message count and check if we need to update personality
            self.message_count += 1
            print(f"\nMessage count: {self.message_count}")
            if self.message_count % self.personality_update_interval == 0:
                print(f"\nTriggering personality update at message {self.message_count}")
                self.personality_updater.update_personality_from_conversation(self.chat_history)
            
            return assistant_response
            
        except Exception as e:
            print(f"Error in chat: {e}")
            return "I apologize, but I encountered an error processing your message."
        

    def start_chat(self):
        """Start an interactive chat session with the user."""
        print(f"\nWelcome! {self.chat_history[1]['content']}\n")
        
        try:
            while True:
                user_input = input("You: ").strip()
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    print(f"\n{self.name}: Goodbye! Have a great day!")
                    break
                
                response = self.chat(user_input)
                print(f"\n{self.name}: {response}\n")
                
        except KeyboardInterrupt:
            print(f"\n\n{self.name}: Chat session ended. Goodbye!")
        except Exception as e:
            print(f"\nError in chat session: {e}")