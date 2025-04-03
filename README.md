# Long Term Memory Chatbot

A sophisticated AI chatbot with persistent personality and memory, designed to maintain consistent character traits and conversation history across sessions.

## Features

- **Persistent Personality**: Maintains a consistent personality across conversations through structured personality files
- **Dynamic Memory System**: Remembers past conversations and uses them to inform future interactions
- **Emotional Intelligence**: Tracks and evolves emotional states based on interactions
- **Natural Conversation**: Engages in human-like dialogue while maintaining character consistency

## Personality Structure

The AI's personality is maintained through several JSON files in the `my-personality` directory:

- `core-identity.json`: Defines fundamental traits, values, and life philosophy
- `emotional-framework.json`: Tracks current emotional state and patterns
- `cognitive-style.json`: Describes thinking and learning patterns
- `social-dynamics.json`: Outlines communication and relationship styles
- `interests-values.json`: Lists professional and personal interests
- `behavioral-patterns.json`: Details daily routines and interaction patterns
- `memory-growth.json`: Stores conversation history and personal growth

## Memory Management

The system implements a sophisticated memory management approach:

- **Recent Memory Window**: Maintains a rolling window of the most recent conversations
- **Memory Compression**: Summarizes older conversations to maintain context while managing size
- **Core Memories**: Preserves important formative experiences and key learnings
- **Growth Tracking**: Monitors personal development and current focus areas

## Conversation Features

- **Natural Dialogue**: Engages in human-like conversation while maintaining character
- **Context Awareness**: Uses recent memories to inform responses
- **Personality Evolution**: Updates traits based on conversation patterns
- **Emotional Response**: Maintains and evolves emotional states through interactions

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up your OpenAI API key in a `.env` file:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

## Usage

Run the chatbot:
```bash
python main.py
```

The chatbot will:
1. Load existing personality files or create new ones
2. Initialize conversation memory
3. Begin an interactive chat session

## Personality Files

### Core Identity (`core-identity.json`)
- Name, age, and profession
- Core values and life philosophy
- Personality traits (primary and secondary)
- Aspirations and identity anchors

### Emotional Framework (`emotional-framework.json`)
- Current emotional state (mood, energy, stress)
- Emotional patterns and triggers
- Coping strategies and emotional goals

### Memory Growth (`memory-growth.json`)
- Core memories and formative experiences
- Recent conversation history
- Growth tracking and learning cycles
- Current focus areas

## Development

The system is built with extensibility in mind:
- New personality traits can be added to existing files
- Memory management can be adjusted through configuration
- Conversation patterns can be modified to suit different use cases

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.