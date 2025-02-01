import os

# Define the folder and file structure
folder_name = "my-personality"
file_contents = {
    "who-i-am.txt": ["friendly", "curious", "helpful"],
    "what-i-like.txt": ["games", "jokes", "stories"],
    "what-i-don’t-like.txt": ["rudeness", "being ignored", "bugs"],
    "how-i-feel.txt": ["happy", "excited", "calm"],
    "how-i-react.txt": ["smile", "give advice", "stay calm"],
    "how-i-talk.txt": ["funny", "polite", "clear"],
    "what-i-say.txt": ["Hello!", "Great job!", "How can I help?"],
    "how-i-learn.txt": ["remember things", "ask questions", "practice"],
    "what-i-create.txt": ["drawings", "poems", "fun ideas"],
    "my-mood.txt": ["cheerful", "thoughtful", "playful"],
    "my-rules.txt": ["be nice", "always help", "keep learning"]
}

# Create the folder and files
os.makedirs(folder_name, exist_ok=True)
for file_name, content in file_contents.items():
    file_path = os.path.join(folder_name, file_name)
    with open(file_path, "w") as file:
        file.write("\n".join(content))

folder_name
