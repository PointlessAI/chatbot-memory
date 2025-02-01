import os
from dotenv import load_dotenv
from openai import OpenAI # type: ignore

from personality_manager import PersonalityManager

class ChatBot:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("API key not found. Please set OPENAI_API_KEY in your .env file.")
        
        # Initialize OpenAI client
        self.client = OpenAI(api_key=self.api_key)
        
        # Initialize PersonalityManager and load personality
        self.personality_manager = PersonalityManager(directory="my-personality")
        personality = self.personality_manager.load_personality()
        self.human = "You are a person. Always act as this person, never break character. Always respond in the first person."
        
        # Start the conversation with the system message containing personality information
        self.chat_history = [
            {"role": "system", "content": f"{self.human} Your personality is {personality}"}
        ]
        self.chat_history_summary_count = 15

    def summarize_chat_history(self, chat_history_string):
        """
        Summarizes the current conversation history and updates the personality files.
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": f"{self.human} Summarize the following conversation history into a detailed first person memory. Max 100 words."},
                    {"role": "user", "content": chat_history_string}
                ]
            )
            chat_history_summary = response.choices[0].message.content
        except Exception as e:
            print(f"Error during summarization: {e}")
            return "Error summarizing chat history."
        
        # Update personality files and clean them
        self.personality_manager.update_personality_files(chat_history_string, self.client)
        self.personality_manager.clean_personality(self.client)
        return chat_history_summary

    def generate_response(self, user_input):
        """
        Adds the user input to the chat history, calls the OpenAI API to generate a response,
        and updates the conversation. It also checks if summarization is needed.
        """
        self.chat_history.append({"role": "user", "content": user_input})
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=self.chat_history
            )
            friend_response = response.choices[0].message.content
            self.chat_history.append({"role": "developer", "content": friend_response})
        except Exception as e:
            print(f"Error generating response: {e}")
            return "Error generating response."

        # Debugging: print number of entries and current chat history
        num_chat_history = len(self.chat_history)
        print(f"\nNumber of chat history entries: {num_chat_history}\n")
        print(self.chat_history)

        # If chat history grows too long, summarize it
        if num_chat_history >= self.chat_history_summary_count:
            chat_history_string = "\n".join(
                [f"{entry['role']}: {entry['content']}" for entry in self.chat_history]
            )
            chat_history_summary = self.summarize_chat_history(chat_history_string)
            updated_personality = self.personality_manager.load_personality()
            self.chat_history = [
                {"role": "system", "content": f"{self.human} Your personality is {updated_personality}"},
                {"role": "developer", "content": chat_history_summary}
            ]
        return friend_response

    def start_chat(self):
        """
        Starts an interactive chat session.
        """
        print("Chat with me. Type 'exit' to quit.")
        while True:
            user_input = input("User: ")
            if user_input.lower() == "exit":
                print("Goodbye!")
                break
            friend_response = self.generate_response(user_input)
            print("Friend:", friend_response)