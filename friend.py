import os
import json
import glob
from dotenv import load_dotenv
from openai import OpenAI  # type: ignore

class ChatBot:
    def __init__(self):
        # Load environment variables from the .env file
        load_dotenv()
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key)
        personality = self.personality()
        self.chat_history = [
            {"role": "system", "content": f"You are a person. Always act as this person, never break character. Always respond in the first person. Your personality is {personality}"}
        ]

    def personality(self):
        # Define the directory containing text files
        directory = "personality_mod"
        personality_parts = []

        # Iterate through all text files in the directory
        for file_path in glob.glob(os.path.join(directory, "*.txt")):
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    # Read content
                    content = file.read().strip()
                    
                    # Get the filename without directory and extension
                    file_name = os.path.basename(file_path)
                    formatted_name = file_name.replace("-", " ").replace("_", " ").rsplit(".", 1)[0]
                    
                    # Append both the content and formatted name
                    personality_parts.append(f"{formatted_name}: {content}")
            except Exception as e:
                print(f"Error reading file {file_path}: {e}")

        # Combine all parts into a single string
        personality = " ".join(personality_parts)
        return personality
    
    def summarize_chat_history(self, chat_history_string):
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a person. Always act as this person, never break character. Always respond in the first person. Summarize the following conversation history into a detailed first person memory. Max 100 words."},
                {"role": "user", "content": chat_history_string}
            ]
        )
        
        chat_history_summary = response.choices[0].message.content
        return chat_history_summary
    
    def generate_response(self, user_input):
        self.chat_history.append({"role": "user", "content": user_input})
        
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=self.chat_history
        )
        
        friend_response = response.choices[0].message.content
        self.chat_history.append({"role": "developer", "content": friend_response})

        num_chat_history = len(self.chat_history)
        # print(f"Number of chat history entries: {num_chat_history}")
        # print(self.chat_history)
        
        # Summarize the chat history if it exceeds 15 messages
        if num_chat_history >= 15:
            chat_history_string = json.dumps(self.chat_history, indent=4)
            chat_history_summary = self.summarize_chat_history(chat_history_string)
            
            # Reset chat history with a summary as context
            self.chat_history = [
                {"role": "system", "content": f"You are a person. Always act as this person, never break character. Always respond in the first person. Your personality is {self.personality()}"},
                {"role": "developer", "content": chat_history_summary}
            ]
        
        return friend_response

    def start_chat(self):
        print("Chat with me")
        while True:
            user_input = input("User: ")
            friend_response = self.generate_response(user_input)
            print("Friend:", friend_response)

if __name__ == "__main__":
    chat_bot = ChatBot()
    chat_bot.start_chat()