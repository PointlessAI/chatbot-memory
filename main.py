# main.py
from chatbot import ChatBot, AutonomousChat

def main():
    print("\nWelcome! Choose an option:")
    print("1. Chat with an AI personality")
    print("2. Watch Jack and Lucy have a conversation")
    
    while True:
        try:
            choice = input("\nEnter your choice (1 or 2): ").strip()
            
            if choice == "1":
                chat_bot = ChatBot()  # Will prompt for personality selection
                chat_bot.start_chat()
                break
            elif choice == "2":
                num_turns = input("How many turns should they talk? (default 20): ").strip()
                num_turns = int(num_turns) if num_turns.isdigit() else 20
                
                autonomous_chat = AutonomousChat("jack", "lucy")
                autonomous_chat.start_conversation(num_turns)
                break
            else:
                print("Invalid choice. Please enter 1 or 2.")
                
        except ValueError as e:
            print(f"Invalid input: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()