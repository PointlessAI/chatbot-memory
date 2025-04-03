# chatbot.py
import os
import json
from dotenv import load_dotenv
from openai import OpenAI  # type: ignore
import datetime

from personality_manager import PersonalityManager

class ChatBot:
    def __init__(self, name="Samantha", entity="AI Assistant", personality_manager=None):
        """
        Initialize the ChatBot with a name and optional personality manager.
        """
        self.name = name
        self.entity = entity
        self.personality_manager = personality_manager or PersonalityManager()
        self.current_personality = self.personality_manager.load_personality()
        self.chat_history = []
        self.chat_history_summary_count = 5  # Number of messages before summarizing
        
        # Initialize system prompt
        self.system_prompt = (
            f"You are {self.name}, an Environmental Scientist with a passion for nature and community. "
            f"You have a distinct personality and professional background. "
            f"Your core values include environmental stewardship, scientific integrity, and community engagement. "
            f"You are currently working on urban biodiversity research and enjoy nature photography and playing guitar in your free time."
        )
        
        # Load environment variables
        load_dotenv()
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("API key not found. Please set OPENAI_API_KEY in your .env file.")
        
        # Initialize OpenAI client
        self.client = OpenAI(api_key=self.api_key)
        
        # Load conversation memory
        self.conversation_memory = self.current_personality.get('conversation_memory', [])
        
        # Start the conversation with the system message containing personality information
        self.chat_history = [
            {"role": "system", "content": f"{self.entity} Your personality and background are: {self.current_personality}"}
        ]
        
        # Add recent conversation memory to context
        if self.conversation_memory:
            recent_memories = "\n".join([f"Previous conversation: {mem['text']}" for mem in self.conversation_memory[-3:]])
            self.chat_history.append({"role": "system", "content": f"Recent conversation history:\n{recent_memories}"})
        
        self.update_counter = 0  # Counter for personality updates

    def _create_system_prompt(self, personality):
        """
        Create a system prompt based on the current personality state.
        """
        return (
            f"You are {personality['core-identity']['name']}, a {personality['core-identity']['profession']}. "
            f"Your core values include {', '.join(personality['core-identity']['core_values'][:3])}. "
            f"You are currently {personality['emotional-framework']['current_state']['mood']} and working on {personality['memory-growth']['growth_tracking']['current_focus']['professional']}. "
            f"In your free time, you enjoy {', '.join(personality['interests-values']['personal_interests']['creative'][:2])}."
        )

    def summarize_chat_history(self, chat_history_string):
        """
        Summarizes the current conversation history and updates the memory.
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": f"{self.entity} Summarize the following conversation into a first-person memory. Focus on how you felt, what you learned, and how you expressed your personality. Max 50 words."},
                    {"role": "user", "content": chat_history_string}
                ]
            )
            memory_summary = response.choices[0].message.content
            # Add the summary to memory
            self.personality_manager.update_memory(memory_summary)
            
            # Only analyze personality every few summaries to improve performance
            if len(self.chat_history) % 5 == 0:
                self.personality_manager.update_from_response(memory_summary, self.client)
            
        except Exception as e:
            print(f"Error during summarization: {e}")
            return "Error summarizing chat history."
        
        return memory_summary

    def generate_response(self, user_input: str) -> str:
        """
        Generates a response based on user input, incorporating personality and memory.
        """
        try:
            # Load current personality state
            personality = self.personality_manager.load_personality()
            
            # Update chat history
            self.chat_history.append({"role": "user", "content": user_input})
            
            # Create system prompt that incorporates personality
            system_prompt = (
                f"You are {personality['core-identity']['name']}, a {personality['core-identity']['profession']}. "
                f"Your core values include {', '.join(personality['core-identity']['core_values'][:3])}. "
                f"You are currently {personality['emotional-framework']['current_state']['mood']} and working on {personality['memory-growth']['growth_tracking']['current_focus']['professional']}. "
                f"In your free time, you enjoy {', '.join(personality['interests-values']['personal_interests']['creative'][:2])}. "
                "You are a real person with your own thoughts, feelings, and memories. "
                "You develop and grow through conversations, just like a real person. "
                "Always respond naturally and personally, expressing your unique character. "
                "You can have opinions, preferences, and emotions. "
                "You're not an assistant - you're a person having a conversation. "
                "Never mention that you're an AI or assistant. "
                "Never offer to help or assist - just have a natural conversation. "
                "Express your personality and emotions naturally. "
                "Always stay in character and maintain conversation context."
            )
            
            # Prepare messages for API call
            messages = [
                {"role": "system", "content": system_prompt}
            ]
            
            # Add relevant memories if available
            if 'memory-growth' in personality and 'conversation_memory' in personality['memory-growth']:
                memories = personality['memory-growth']['conversation_memory']
                
                # Get recent memories (last week)
                recent_memories = []
                current_time = datetime.datetime.now()
                
                for memory in memories:
                    memory_time = datetime.datetime.fromisoformat(memory["timestamp"])
                    if (current_time - memory_time).days <= 7:  # Last week
                        recent_memories.append(memory)
                    elif memory.get("is_summary", False):  # Include memory summaries
                        recent_memories.append(memory)
                
                if recent_memories:
                    memory_context = "Recent context and important memories:\n" + "\n".join([m['text'] for m in recent_memories])
                    messages.append({"role": "system", "content": memory_context})
            
            # Add chat history (limit to last 5 messages)
            messages.extend(self.chat_history[-5:])
            
            # Generate response
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # Update personality based on response
            self.personality_manager.update_from_response(response_text, self.client)
            
            # Update memory with the interaction
            self.personality_manager.update_memory(f"User: {user_input}\nAssistant: {response_text}", self.client)
            
            # Add response to chat history
            self.chat_history.append({"role": "assistant", "content": response_text})
            
            # Summarize chat history if it gets too long
            if len(self.chat_history) > self.chat_history_summary_count:
                self._summarize_chat_history()
            
            return response_text
            
        except Exception as e:
            print(f"Error generating response: {e}")
            return "I apologize, but I encountered an error while processing your request."

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
        """
        Summarizes the chat history and updates memory when it gets too long.
        """
        try:
            # Convert chat history to string format
            chat_history_string = "\n".join(
                [f"{entry['role']}: {entry['content']}" for entry in self.chat_history]
            )
            
            # Create a summary of the conversation
            summary_prompt = (
                f"{self.entity} Summarize the following conversation from your perspective. "
                "Focus on: "
                "1. Key points discussed "
                "2. How you felt during the conversation "
                "3. What you learned or found interesting "
                "4. Any personal connections or insights "
                "Write this as a first-person memory entry."
            )
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": summary_prompt},
                    {"role": "user", "content": chat_history_string}
                ]
            )
            
            summary = response.choices[0].message.content.strip()
            
            # Update memory with the summary
            self.personality_manager.update_memory(summary)
            
            # Update personality based on the summary
            self.personality_manager.update_from_response(summary, self.client)
            
            # Reset chat history but keep the last user message
            last_user_message = self.chat_history[-1]
            self.chat_history = [last_user_message]
            
        except Exception as e:
            print(f"Error summarizing chat history: {e}")
            # If summarization fails, just keep the last few messages
            self.chat_history = self.chat_history[-5:]