import os
import json
import glob
import math
from dotenv import load_dotenv
from openai import OpenAI  # type: ignore

class ChatBot:
    def __init__(self):
        # Load environment variables from the .env file
        load_dotenv()
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("API key not found. Please set OPENAI_API_KEY in your .env file.")
        self.client = OpenAI(api_key=self.api_key)

        # Initialize attributes
        self.directory = "my-personality"  # Set directory before calling personality()
        self.chat_history_summary_count = 15

        # Generate personality
        personality = self.personality()
        self.human = "You are a person. Always act as this person, never break character. Always respond in the first person."

        # Initialize personality
        self.chat_history = [
            {"role": "system", "content": f"{self.human} Your personality is {personality}"}
        ]

    def personality(self):
        # This function reads each file in the my-personality folder and then appends them to form the users personality ready for processing.
        personality_parts = []
        for file_path in glob.glob(os.path.join(self.directory, "*.txt")):
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    content = file.read().strip()
                    file_name = os.path.basename(file_path).rsplit(".", 1)[0].replace("-", " ")
                    personality_parts.append(f"{file_name}: {content}")
            except Exception as e:
                print(f"Error reading file {file_path}: {e}")
        # Personality is returned as an array
        return " ".join(personality_parts)

    def get_filenames(self):
        return [
            os.path.splitext(os.path.basename(file_path))[0]
            for file_path in glob.glob(os.path.join(self.directory, "*.txt"))
        ]

    def check_and_summarize_files(self):
        for file_path in glob.glob(os.path.join(self.directory, "*.txt")):
            try:
                if os.path.getsize(file_path) > 500:  # Check if file size exceeds 500 bytes
                    with open(file_path, "r", encoding="utf-8") as file:
                        content = file.read()

                        # Summarize the content
                        system_prompt = (
                            "You are a helpful assistant. Summarize the following text into a more concise version: "
                        )
                    try:
                        response = self.client.chat.completions.create(
                            model="gpt-4",
                            messages=[
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": content}
                            ]
                        )
                        summarized_content = response.choices[0].message.content.strip()
                        print(summarized_content)

                        # Write the summarized content back to the file
                        with open(file_path, "w", encoding="utf-8") as file:
                            file.write(summarized_content)
                        print(f"Summarized content for {file_path}")

                    except Exception as e:
                        print(f"Error summarizing file {file_path}: {e}")

            except Exception as e:
                print(f"Error checking file size for {file_path}: {e}")

    def update_personality_files(self, chat_history_string):
        filenames = self.get_filenames()
        filename_list_str = ", ".join(f'"{filename}"' for filename in filenames)

        system_prompt = (
            f"Categorize the following chat history string into a JSON object. "
            f"Keys should be one of the following categories: {filename_list_str}. "
            f"The values should be the related text. Example format: {{\"my-hobbies\": \"painting\", \"my-mood\": \"happy\"}}."
        )

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": chat_history_string}
                ]
            )

            print("Raw API Response:", response)  # Debugging
            content = response.choices[0].message.content.strip()
            print("API Content:", content)  # Debugging

            # Parse the content into a JSON object
            categorized_content = json.loads(content)

        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            return
        except Exception as e:
            print(f"Error during API call or parsing response: {e}")
            return

        for category, content in categorized_content.items():
            file_path = os.path.join(self.directory, f"{category}.txt")
            try:
                with open(file_path, "a", encoding="utf-8") as file:
                    file.write(f"\n{content.strip()}")
                    print(f"Updated personality module: {category}.txt successfully.")
            except Exception as e:
                print(f"Error writing to file {file_path}: {e}")

        # Check and summarize files if needed
        self.check_and_summarize_files()


    def clean_personality(self, batch_size=5):
        filenames = self.get_filenames()
        
        # Process files in batches
        for i in range(0, len(filenames), batch_size):
            batch = filenames[i:i + batch_size]  # Take batch_size number of files
            file_data = []

            for filename in batch:
                filename = filename + ".txt"
                file_path = os.path.join(self.directory, filename)

                try:
                    with open(file_path, "r", encoding="utf-8") as file:
                        file_contents = file.read().strip()

                    if not file_contents:
                        print(f"Skipping empty file: {filename}")
                        continue

                    # Store the file content with a delimiter
                    file_data.append(f"### {filename}\n{file_contents}")

                except Exception as e:
                    print(f"Error reading file {filename}: {e}")
            
            if not file_data:
                continue  # Skip batch if all files are empty

            # Join all file contents with clear separation
            batch_input = "\n\n".join(file_data)

            # Construct system prompt
            system_prompt = (
                "You are a helpful assistant. You will be provided with multiple lists of personality attributes, each labeled with a filename. "
                "Your task is to summarize each list separately while keeping the core meaning intact.\n\n"
                "**Instructions:**\n"
                "- Remove duplicates and redundant phrases.\n"
                "- Group similar interests together under broader categories (e.g., 'Movies & TV', 'Hobbies', 'Languages & Learning').\n"
                "- Maintain readability and keep the summaries concise.\n"
                "- Return each summary under the same filename header.\n\n"
                "**Example Output:**\n"
                "### file1.txt\n"
                "- **Movies & TV:** Loves films, especially *Inception*. Enjoys Netflix.\n"
                "- **Hobbies:** Enjoys dancing and golfing.\n\n"
                "### file2.txt\n"
                "- **Creative Arts:** Likes drawing landscapes.\n"
                "- **Languages & Learning:** Speaks basic Chinese and German.\n\n"
                "Now, summarize the following lists:\n\n"
                f"{batch_input}"
            )

            try:
                # Call OpenAI API for batch summarization
                response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": batch_input}
                    ]
                )

                summarized_text = response.choices[0].message.content.strip()

                # Split the summarized output back into individual files
                summaries = summarized_text.split("### ")
                for summary in summaries:
                    if not summary.strip():
                        continue  # Skip empty segments
                    
                    lines = summary.split("\n", 1)
                    if len(lines) < 2:
                        continue  # Skip incorrectly formatted responses

                    filename = lines[0].strip()
                    content = lines[1].strip()

                    file_path = os.path.join(self.directory, filename)
                    with open(file_path, "w", encoding="utf-8") as file:
                        file.write(content)

                    print(f"Successfully summarized: {filename}")

            except Exception as e:
                print(f"Error processing batch {i//batch_size + 1}: {e}")


    def summarize_chat_history(self, chat_history_string):
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
        self.update_personality_files(chat_history_string)
        self.clean_personality()
        return chat_history_summary

    def generate_response(self, user_input):
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

        # Check if chat history is too large and if so summarize:
        num_chat_history = len(self.chat_history)
        print(f"\nNumber of chat history entries: {num_chat_history}\n")
        print(self.chat_history)

        if num_chat_history >= self.chat_history_summary_count:
            chat_history_string = "\n".join([f"{entry['role']}: {entry['content']}" for entry in self.chat_history])
            chat_history_summary = self.summarize_chat_history(chat_history_string)
            updated_personality = self.personality()
            self.chat_history = [
                {"role": "system", "content": f"{self.human} Your personality is {updated_personality}"},
                {"role": "developer", "content": chat_history_summary}
            ]
        return friend_response

    def start_chat(self):
        print("Chat with me. Type 'exit' to quit.")
        while True:
            user_input = input("User: ")
            if user_input.lower() == "exit":
                print("Goodbye!")
                break
            friend_response = self.generate_response(user_input)
            print("Friend:", friend_response)

if __name__ == "__main__":
    chat_bot = ChatBot()
    chat_bot.start_chat()