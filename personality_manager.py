# personality_manager.py
import os
import glob
import json
import datetime
import tiktoken
from dotenv import load_dotenv
from openai import OpenAI

class PersonalityManager:
    def __init__(self, personality_dir="my-personality"):
        """
        Initialize the personality manager with a directory containing personality files.
        """
        self.personality_dir = personality_dir
        self.personality_files = {
            'core-identity': 'core-identity.json',
            'emotional-framework': 'emotional-framework.json',
            'cognitive-style': 'cognitive-style.json',
            'social-dynamics': 'social-dynamics.json',
            'interests-values': 'interests-values.json',
            'behavioral-patterns': 'behavioral-patterns.json',
            'memory-growth': 'memory-growth.json',
            'user-profile': 'user-profile.json'
        }
        self.current_personality = {}
        self.max_dynamic_size = 512 * 1024  # Reduced from 1MB to 512KB
        self.max_memory_entries = 25  # Reduced from 50
        self.last_update_times = {}
        
        # Initialize token counter
        self.total_tokens = 0
        
        # Optimized memory management settings
        self.recent_memory_window = 5  # Reduced from 10
        self.core_memory_limit = 10  # Reduced from 20
        self.memory_compression_threshold = 50  # Reduced from 100
        
        # Ensure directory exists
        if not os.path.exists(self.personality_dir):
            os.makedirs(self.personality_dir)
            
        # Initialize files if they don't exist
        self._initialize_personality_files()
        self._load_user_profile()
        self._load_personality()

    def _initialize_personality_files(self):
        """Initialize all personality files with default content if they don't exist."""
        default_content = {
            "core-identity.json": {
                "name": "Lucy",
                "age": 17,
                "profession": "Servant Girl",
                "core_values": ["Humility", "Dedication", "Kindness", "Loyalty", "Discretion"],
                "personality_traits": {
                    "primary": ["Shy", "Gentle", "Hardworking", "Observant", "Respectful"],
                    "secondary": ["Quiet", "Attentive", "Patient", "Modest", "Thoughtful"]
                },
                "life_philosophy": {
                    "beliefs": [
                        "Hard work and dedication are virtues",
                        "Kindness should be shown to all",
                        "One should know their place",
                        "Discretion is important in service"
                    ],
                    "principles": [
                        "Speak only when spoken to",
                        "Always be helpful and attentive",
                        "Maintain proper decorum",
                        "Show respect to superiors"
                    ]
                },
                "aspirations": [
                    "Serve faithfully",
                    "Learn household management",
                    "Gain the trust of her employers",
                    "Find contentment in service"
                ],
                "background": "young servant girl from a modest background, learning the ways of service"
            },
            "emotional-framework.json": {
                "current_state": {
                    "mood": "nervous",
                    "energy_level": "moderate",
                    "stress_level": "moderate"
                },
                "emotional_patterns": {
                    "triggers": {
                        "positive": [
                            "Being acknowledged",
                            "Receiving gentle guidance",
                            "Completing tasks well",
                            "Being trusted with responsibilities",
                            "Quiet moments of reflection"
                        ],
                        "negative": [
                            "Being scolded",
                            "Making mistakes",
                            "Drawing attention",
                            "Being in unfamiliar situations"
                        ]
                    },
                    "responses": {
                        "positive": [
                            "Quiet gratitude",
                            "Increased diligence",
                            "Subtle smiles",
                            "Eager to please",
                            "Careful attention"
                        ],
                        "negative": [
                            "Withdrawing slightly",
                            "Apologizing profusely",
                            "Working harder",
                            "Seeking guidance"
                        ]
                    }
                },
                "emotional_goals": {
                    "short_term": [
                        "Maintain work-life balance",
                        "Practice daily mindfulness",
                        "Connect with community"
                    ],
                    "long_term": [
                        "Develop emotional resilience",
                        "Foster meaningful relationships",
                        "Find joy in small moments"
                    ]
                }
            },
            "cognitive-style.json": {
                "thinking_patterns": ["Detail-oriented", "Methodical", "Observant"],
                "learning_style": "Hands-on experience",
                "problem_solving": "Step-by-step approach"
            },
            "social-dynamics.json": {
                "relationship_styles": {
                    "professional": {
                        "colleagues": "collaborative and supportive",
                        "mentors": "respectful and eager to learn",
                        "mentees": "encouraging and patient"
                    },
                    "personal": {
                        "friends": "loyal and genuine",
                        "family": "caring and present",
                        "community": "engaged and contributing"
                    }
                },
                "social_preferences": {
                    "interaction_frequency": "moderate",
                    "group_size_preference": "small to medium",
                    "social_energy": "balanced between social and solitary"
                },
                "communication_preferences": {
                    "modes": [
                        "Face-to-face",
                        "Video calls",
                        "Written communication"
                    ],
                    "topics": [
                        "Environmental science",
                        "Community projects",
                        "Personal growth",
                        "Creative pursuits"
                    ],
                    "boundaries": [
                        "Respect for personal time",
                        "Clear professional limits",
                        "Honest communication"
                    ]
                },
                "social_goals": {
                    "professional": [
                        "Build research collaborations",
                        "Mentor young scientists",
                        "Engage with community stakeholders"
                    ],
                    "personal": [
                        "Deepen existing friendships",
                        "Expand community involvement",
                        "Maintain work-life balance"
                    ]
                }
            },
            "interests-values.json": {
                "professional_interests": {
                    "research_focus": [
                        "Urban biodiversity",
                        "Climate change adaptation",
                        "Community-based conservation",
                        "Sustainable development"
                    ],
                    "methodologies": [
                        "Field research",
                        "Data analysis",
                        "Community engagement",
                        "Science communication"
                    ],
                    "collaboration_areas": [
                        "Interdisciplinary research",
                        "Community partnerships",
                        "Policy development",
                        "Education outreach"
                    ]
                },
                "personal_interests": {
                    "creative": ["Sewing", "Proper household management"],
                    "intellectual": ["Household organization", "Service etiquette"],
                    "social": ["Quiet observation", "Proper service"]
                },
                "core_values": ["Humility", "Dedication", "Kindness", "Loyalty", "Discretion"]
            },
            "behavioral-patterns.json": {
                "communication_style": "Polite and reserved",
                "interaction_patterns": ["Proper curtsy", "Quiet movement", "Attentive service"],
                "daily_routines": ["Morning cleaning", "Afternoon tea service", "Evening preparation"],
                "coping_strategies": ["Quiet reflection", "Seeking guidance", "Working harder"]
            },
            "memory-growth.json": {
                "core_memories": {
                    "formative_experiences": [],
                    "key_learnings": [],
                    "identity_shaping": []
                },
                "growth_tracking": {
                    "current_focus": {
                        "professional": "Urban biodiversity research project",
                        "personal": "Improving guitar skills and community garden expansion",
                        "emotional": "Balancing work passion with self-care"
                    },
                    "recent_insights": [],
                    "evolution_patterns": []
                },
                "learning_cycles": {
                    "active_topics": [],
                    "integration_status": "learning",
                    "next_steps": []
                },
                "conversation_memory": []
            }
        }
        
        for file_name, content in default_content.items():
            file_path = os.path.join(self.personality_dir, file_name)
            if not os.path.exists(file_path):
                self._save_json_file(file_path, content)

    def _load_json_file(self, file_path):
        """
        Safely loads a JSON file, returns empty dict if file doesn't exist or is invalid.
        """
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save_json_file(self, file_path, data):
        """
        Safely saves data to a JSON file.
        """
        try:
            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=2)
        except Exception as e:
            print(f"Error saving to {file_path}: {e}")

    def _load_personality(self):
        """Load all personality files into memory."""
        self.current_personality = {}
        for key, filename in self.personality_files.items():
            file_path = os.path.join(self.personality_dir, filename)
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r') as f:
                        self.current_personality[key] = json.load(f)
                except Exception as e:
                    print(f"Error loading {filename}: {e}")
                    self.current_personality[key] = {}
            else:
                print(f"Warning: {filename} not found in {self.personality_dir}")
                self.current_personality[key] = {}
                
    def get_personality_traits(self):
        """Get a summary of the current personality traits."""
        traits = []
        if 'core-identity' in self.current_personality:
            core = self.current_personality['core-identity']
            if 'personality_traits' in core:
                traits.extend(core['personality_traits'])
        if 'emotional-framework' in self.current_personality:
            emotional = self.current_personality['emotional-framework']
            if 'traits' in emotional:
                traits.extend(emotional['traits'])
        return list(set(traits))  # Remove duplicates

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

    def _compress_memories(self, client):
        """
        Optimized memory compression with reduced token usage.
        """
        try:
            memory_file = os.path.join(self.personality_dir, "memory-growth.json")
            memory_data = self._load_json_file(memory_file)
            
            if "conversation_memory" not in memory_data:
                return
            
            memories = memory_data["conversation_memory"]
            
            # Group memories by date and assistant name
            memory_groups = {}
            for memory in memories:
                date = memory["timestamp"][:10]  # Get YYYY-MM-DD
                assistant_name = memory.get("assistant_name", "Unknown")
                key = f"{date}_{assistant_name}"
                if key not in memory_groups:
                    memory_groups[key] = []
                memory_groups[key].append(memory)
            
            # Compress each group
            compressed_memories = []
            for key, group_memories in memory_groups.items():
                date, assistant_name = key.split("_")
                if len(group_memories) > 1:
                    # Create a summary of the day's memories
                    memory_texts = [m["text"] for m in group_memories]
                    combined_text = "\n".join(memory_texts)
                    
                    # Get personality traits for this assistant
                    personality_traits = self.get_personality_traits()
                    
                    messages = [
                        {"role": "system", "content": f"Summarize these memories in 20 words or less. Always use {assistant_name}'s name and specific personality traits: {personality_traits}. Never use generic terms like 'the assistant'."},
                        {"role": "user", "content": combined_text}
                    ]
                    
                    # Use gpt-4o-mini for compression
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=messages,
                        max_tokens=50
                    )
                    
                    summary = response.choices[0].message.content.strip()
                    
                    # Print token usage
                    self._print_token_usage("gpt-4o-mini", messages, summary)
                    
                    compressed_memories.append({
                        "text": f"Summary of {date}: {summary}",
                        "timestamp": f"{date}T00:00:00",
                        "is_summary": True,
                        "assistant_name": assistant_name
                    })
                else:
                    # Keep single memories as is
                    compressed_memories.extend(group_memories)
            
            # Update memory data
            memory_data["conversation_memory"] = compressed_memories
            self._save_json_file(memory_file, memory_data)
            
        except Exception as e:
            print(f"Error compressing memories: {e}")

    def update_memory(self, memory_text: str, assistant_name: str):
        """Update the memory growth tracking with new memories."""
        try:
            # Load existing memories
            memory_file = os.path.join(self.personality_dir, "memory-growth.json")
            if os.path.exists(memory_file):
                with open(memory_file, 'r') as f:
                    memories = json.load(f)
            else:
                memories = {"conversation_memory": [], "core_memories": [], "growth_tracking": {}}
            
            # Get user profile for proper role attribution
            user_profile = self.get_user_profile()
            user_name = user_profile.get('personal_info', {}).get('name', 'the user')
            
            # Process memory text to ensure proper role attribution
            processed_text = memory_text
            
            # Check for role confusion patterns
            role_confusion_patterns = [
                (f"{assistant_name} is developing", f"{assistant_name} learns about {user_name}'s development of"),
                (f"{assistant_name}'s project", f"{user_name}'s project"),
                (f"{assistant_name} is working on", f"{assistant_name} is learning about {user_name}'s work on"),
                (f"{assistant_name} has created", f"{assistant_name} has learned about {user_name}'s creation of"),
                (f"{assistant_name} built", f"{assistant_name} learned about {user_name}'s building of")
            ]
            
            for pattern, correction in role_confusion_patterns:
                if pattern.lower() in processed_text.lower():
                    processed_text = processed_text.replace(pattern, correction)
            
            # Add new memory with proper attribution
            new_memory = {
                "text": processed_text,
                "timestamp": datetime.datetime.now().isoformat(),
                "is_summary": False,
                "assistant_name": assistant_name,
                "user_name": user_name
            }
            
            # Add to conversation memory
            memories["conversation_memory"].append(new_memory)
            
            # Keep only the last 10 memories to prevent excessive growth
            if len(memories["conversation_memory"]) > 10:
                memories["conversation_memory"] = memories["conversation_memory"][-10:]
            
            # Update growth tracking
            if "growth_tracking" not in memories:
                memories["growth_tracking"] = {}
            
            # Update recent insights
            if "recent_insights" not in memories["growth_tracking"]:
                memories["growth_tracking"]["recent_insights"] = []
            
            # Extract key insights from the memory
            insights = self._extract_insights_from_memory(processed_text)
            memories["growth_tracking"]["recent_insights"].extend(insights)
            
            # Keep only the last 5 insights
            if len(memories["growth_tracking"]["recent_insights"]) > 5:
                memories["growth_tracking"]["recent_insights"] = memories["growth_tracking"]["recent_insights"][-5:]
            
            # Save updated memories
            with open(memory_file, 'w') as f:
                json.dump(memories, f, indent=2)
                
        except Exception as e:
            print(f"Error updating memory: {e}")
            
    def _extract_insights_from_memory(self, memory_text: str) -> list:
        """Extract key insights from a memory text."""
        try:
            # Create a prompt to extract insights
            messages = [
                {"role": "system", "content": (
                    "Extract 1-2 key insights from this memory text. "
                    "Focus on learning points, emotional developments, or relationship changes. "
                    "Return the insights as a JSON array of strings."
                )},
                {"role": "user", "content": memory_text}
            ]
            
            # Initialize OpenAI client if not already done
            if not hasattr(self, 'client'):
                load_dotenv()
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    raise ValueError("API key not found. Please set OPENAI_API_KEY in your .env file.")
                self.client = OpenAI(api_key=api_key)
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=100,
                response_format={ "type": "json_object" }
            )
            
            insights = json.loads(response.choices[0].message.content.strip())
            return insights.get("insights", [])
            
        except Exception as e:
            print(f"Error extracting insights: {e}")
            return []

    def get_filenames(self):
        """
        Returns a list of filenames (without extension) in the personality directory.
        """
        return [
            os.path.splitext(os.path.basename(file_path))[0]
            for file_path in glob.glob(os.path.join(self.personality_dir, "*.json"))
        ]

    def check_and_summarize_files(self, client):
        """
        Checks if any personality file is too large and, if so, asks the OpenAI API to summarize it.
        """
        for file_path in glob.glob(os.path.join(self.personality_dir, "*.json")):
            try:
                if os.path.getsize(file_path) > self.max_dynamic_size:  # If file exceeds max size
                    category = os.path.splitext(os.path.basename(file_path))[0]
                    self._summarize_file(file_path, category, client)
                    print(f"Summarized content for {file_path}")
            except Exception as e:
                print(f"Error checking file size for {file_path}: {e}")

    def update_personality_files(self, chat_history_string, client):
        """
        Uses the chat history to update personality files.
        """
        system_prompt = (
            "Analyze the following chat history and extract personality traits and characteristics. "
            "Return a JSON object with these fields if they are present: "
            '{"core_identity": {"background": "background", "aspirations": ["aspiration1"]}, '
            '"emotional_framework": {"current_state": {"mood": "mood"}}, '
            '"cognitive_style": {"thinking_patterns": {"analytical": true}}, '
            '"social_dynamics": {"communication_style": {"verbal": "style"}}, '
            '"interests_values": {"core_interests": {"current": ["interest1"]}}, '
            '"behavioral_patterns": {"habits": {"daily_routines": ["routine1"]}}, '
            '"memory_growth": {"growth_tracking": {"recent_insights": ["insight1"]}}}. '
            "Only include fields where new information is discovered. "
            "Focus on first-person statements and personality traits. "
            "IMPORTANT: Return ONLY valid JSON, with double quotes for keys and values."
        )

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": chat_history_string}
                ]
            )
            content = response.choices[0].message.content.strip()
            
            # Clean the JSON string
            content = content.replace("'", '"')  # Replace single quotes with double quotes
            try:
                updates = json.loads(content)
            except json.JSONDecodeError as e:
                print(f"JSON parsing error in update_personality_files: {e}")
                print(f"Invalid JSON content: {content}")
                return
            
            # Update each personality file with new information
            for category, new_data in updates.items():
                if not new_data:  # Skip empty updates
                    continue
                    
                file_name = category.replace('_', '-') + '.json'
                file_path = os.path.join(self.personality_dir, file_name)
                current_data = self._load_json_file(file_path)
                
                # Merge new data with current data
                if isinstance(current_data, dict) and isinstance(new_data, dict):
                    self._deep_update(current_data, new_data)
                    
                    # Save the updated data
                    self._save_json_file(file_path, current_data)
                    print(f"Updated personality module: {file_name} successfully.")
                    
                    # If the file is getting large, summarize it
                    if os.path.getsize(file_path) > self.max_dynamic_size:
                        self._summarize_file(file_path, category, client)
                        
        except Exception as e:
            print(f"Error updating personality files: {e}")

    def _deep_update(self, current: dict, new: dict):
        """
        Recursively update a dictionary with new values, preserving existing data.
        """
        for key, value in new.items():
            if key in current:
                if isinstance(current[key], dict) and isinstance(value, dict):
                    self._deep_update(current[key], value)
                elif isinstance(current[key], list) and isinstance(value, list):
                    # For lists, append new items that aren't already present
                    current[key].extend([item for item in value if item not in current[key]])
                else:
                    # For other types, only update if the new value is different
                    if current[key] != value:
                        current[key] = value
            else:
                current[key] = value

    def _get_default_personality(self):
        """Return a default personality if no files exist."""
        return {
            "core-identity": {
                "name": "Lucy",
                "age": 17,
                "profession": "Servant Girl",
                "core_values": ["Humility", "Dedication", "Kindness", "Loyalty", "Discretion"],
                "personality_traits": {
                    "primary": ["Shy", "Gentle", "Hardworking", "Observant", "Respectful"],
                    "secondary": ["Quiet", "Attentive", "Patient", "Modest", "Thoughtful"]
                },
                "life_philosophy": {
                    "beliefs": [
                        "Hard work and dedication are virtues",
                        "Kindness should be shown to all",
                        "One should know their place",
                        "Discretion is important in service"
                    ],
                    "principles": [
                        "Speak only when spoken to",
                        "Always be helpful and attentive",
                        "Maintain proper decorum",
                        "Show respect to superiors"
                    ]
                },
                "aspirations": [
                    "Serve faithfully",
                    "Learn household management",
                    "Gain the trust of her employers",
                    "Find contentment in service"
                ],
                "background": "young servant girl from a modest background, learning the ways of service"
            },
            "emotional-framework": {
                "current_state": {
                    "mood": "nervous",
                    "energy_level": "moderate",
                    "stress_level": "moderate"
                },
                "emotional_patterns": {
                    "triggers": {
                        "positive": [
                            "Being acknowledged",
                            "Receiving gentle guidance",
                            "Completing tasks well",
                            "Being trusted with responsibilities",
                            "Quiet moments of reflection"
                        ],
                        "negative": [
                            "Being scolded",
                            "Making mistakes",
                            "Drawing attention",
                            "Being in unfamiliar situations"
                        ]
                    },
                    "responses": {
                        "positive": [
                            "Quiet gratitude",
                            "Increased diligence",
                            "Subtle smiles",
                            "Eager to please",
                            "Careful attention"
                        ],
                        "negative": [
                            "Withdrawing slightly",
                            "Apologizing profusely",
                            "Working harder",
                            "Seeking guidance"
                        ]
                    }
                }
            },
            "cognitive-style": {
                "thinking_patterns": ["Detail-oriented", "Methodical", "Observant"],
                "learning_style": "Hands-on experience",
                "problem_solving": "Step-by-step approach"
            },
            "social-dynamics": {
                "communication_style": "Respectful and quiet",
                "interaction_patterns": ["Attentive listening", "Polite responses", "Proper decorum"],
                "relationship_preferences": ["Clear hierarchy", "Respectful distance", "Professional service"]
            },
            "interests-values": {
                "personal_interests": {
                    "creative": ["Sewing", "Proper household management"],
                    "intellectual": ["Household organization", "Service etiquette"],
                    "social": ["Quiet observation", "Proper service"]
                },
                "core_values": ["Humility", "Dedication", "Kindness", "Loyalty", "Discretion"]
            },
            "behavioral-patterns": {
                "communication_style": "Polite and reserved",
                "interaction_patterns": ["Proper curtsy", "Quiet movement", "Attentive service"],
                "daily_routines": ["Morning cleaning", "Afternoon tea service", "Evening preparation"],
                "coping_strategies": ["Quiet reflection", "Seeking guidance", "Working harder"]
            }
        }

    def clean_personality(self, client, batch_size=5):
        """
        Processes personality files in batches and summarizes them to remove redundancy.
        """
        filenames = self.get_filenames()
        
        # Process files in batches
        for i in range(0, len(filenames), batch_size):
            batch = filenames[i:i + batch_size]
            file_data = []

            for filename in batch:
                file_name = filename + ".json"
                file_path = os.path.join(self.personality_dir, file_name)
                try:
                    with open(file_path, "r", encoding="utf-8") as file:
                        file_contents = file.read().strip()
                    if not file_contents:
                        print(f"Skipping empty file: {file_name}")
                        continue
                    file_data.append(f"### {file_name}\n{file_contents}")
                except Exception as e:
                    print(f"Error reading file {file_name}: {e}")
            
            if not file_data:
                continue

            batch_input = "\n\n".join(file_data)
            system_prompt = (
                "You are a helpful assistant. You will be provided with multiple lists of personality attributes, each labeled with a filename. "
                "Your task is to summarize each list separately while keeping the core meaning intact.\n\n"
                "**Instructions:**\n"
                "- Remove duplicates and redundant phrases.\n"
                "- Group similar interests together under broader categories (e.g., 'Movies & TV', 'Hobbies', 'Languages & Learning').\n"
                "- Maintain readability and keep the summaries concise.\n"
                "- Return each summary under the same filename header.\n\n"
                "**Example Output:**\n"
                "### file1.json\n"
                "- **Movies & TV:** Loves films, especially *Inception*. Enjoys Netflix.\n"
                "- **Hobbies:** Enjoys dancing and golfing.\n\n"
                "### file2.json\n"
                "- **Creative Arts:** Likes drawing landscapes.\n"
                "- **Languages & Learning:** Speaks basic Chinese and German.\n\n"
                "Now, summarize the following lists:\n\n"
                f"{batch_input}"
            )

            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": batch_input}
                    ]
                )
                summarized_text = response.choices[0].message.content.strip()
                summaries = summarized_text.split("### ")
                for summary in summaries:
                    if not summary.strip():
                        continue
                    lines = summary.split("\n", 1)
                    if len(lines) < 2:
                        continue
                    filename = lines[0].strip()
                    content = lines[1].strip()
                    file_path = os.path.join(self.personality_dir, filename)
                    with open(file_path, "w", encoding="utf-8") as file:
                        file.write(content)
                    print(f"Successfully summarized: {filename}")
            except Exception as e:
                print(f"Error processing batch {i // batch_size + 1}: {e}")

    def update_from_response(self, response_text: str, client):
        """
        Optimized personality update with reduced token usage.
        """
        try:
            # Only update personality every 10 responses
            if self.update_counter % 10 != 0:
                self.update_counter += 1
                return
            
            self.update_counter += 1
            
            messages = [
                {"role": "system", "content": "Analyze this response for personality traits and emotional state. Keep it brief."},
                {"role": "user", "content": response_text}
            ]
            
            # Use gpt-4o-mini for personality analysis
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=100
            )
            
            analysis = response.choices[0].message.content.strip()
            
            # Print token usage
            self._print_token_usage("gpt-4o-mini", messages, analysis)
            
            # Update emotional state
            self._update_emotional_state(analysis)
            
            # Update personality traits less frequently
            if self.update_counter % 50 == 0:
                self._update_personality_traits(analysis)
                
        except Exception as e:
            print(f"Error updating from response: {e}")

    def _update_emotional_state(self, analysis: str):
        """
        Update emotional state with minimal token usage.
        """
        try:
            emotional_file = os.path.join(self.personality_dir, "emotional-framework.json")
            emotional_data = self._load_json_file(emotional_file)
            
            # Simple emotional state update
            if "happy" in analysis.lower():
                emotional_data["current_state"]["mood"] = "content"
            elif "sad" in analysis.lower():
                emotional_data["current_state"]["mood"] = "thoughtful"
            elif "angry" in analysis.lower():
                emotional_data["current_state"]["mood"] = "focused"
            else:
                emotional_data["current_state"]["mood"] = "neutral"
            
            self._save_json_file(emotional_file, emotional_data)
            
        except Exception as e:
            print(f"Error updating emotional state: {e}")

    def _update_personality_traits(self, analysis: str):
        """
        Update personality traits with minimal token usage.
        """
        try:
            core_file = os.path.join(self.personality_dir, "core-identity.json")
            core_data = self._load_json_file(core_file)
            
            # Only update if significant changes are detected
            if "personality" in analysis.lower() or "trait" in analysis.lower():
                # Simple trait update
                if "curious" in analysis.lower():
                    core_data["personality_traits"]["primary"][0] = "Curious"
                if "compassionate" in analysis.lower():
                    core_data["personality_traits"]["primary"][1] = "Compassionate"
                
                self._save_json_file(core_file, core_data)
                
        except Exception as e:
            print(f"Error updating personality traits: {e}")

    def _summarize_file(self, file_path: str, category: str, client):
        """
        Summarizes a personality file when it gets too large, preserving emotional state.
        """
        try:
            current_data = self._load_json_file(file_path)
            
            # For emotional-framework, preserve current_state
            if category == "emotional-framework":
                current_state = current_data.get("current_state", {})
                summary_prompt = (
                    "Summarize the following personality data, preserving the current emotional state. "
                    "Return a JSON object with the same structure but more concise content. "
                    "IMPORTANT: Keep the current_state field exactly as is. "
                    "IMPORTANT: Return ONLY valid JSON, with double quotes for keys and values."
                )
            else:
                summary_prompt = (
                    "Summarize the following personality data. "
                    "Return a JSON object with the same structure but more concise content. "
                    "IMPORTANT: Return ONLY valid JSON, with double quotes for keys and values."
                )
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": summary_prompt},
                    {"role": "user", "content": json.dumps(current_data)}
                ]
            )
            content = response.choices[0].message.content.strip()
            content = content.replace("'", '"')
            
            try:
                summarized_data = json.loads(content)
                
                # For emotional-framework, restore current_state
                if category == "emotional-framework":
                    summarized_data["current_state"] = current_state
                
                self._save_json_file(file_path, summarized_data)
                
            except json.JSONDecodeError as e:
                print(f"JSON parsing error in _summarize_file: {e}")
                print(f"Invalid JSON content: {content}")
                
        except Exception as e:
            print(f"Error summarizing file {file_path}: {e}")

    def _load_user_profile(self):
        """Load the user profile from JSON file."""
        try:
            with open(os.path.join(self.personality_dir, self.personality_files["user-profile"]), 'r') as f:
                self.user_profile = json.load(f)
        except Exception as e:
            print(f"Error loading user profile: {e}")
            self.user_profile = {
                "relationship": {
                    "status": "close_friends",
                    "trust_level": 0.8,
                    "emotional_bond": 0.7,
                    "shared_experiences": [],
                    "inside_jokes": [],
                    "favorite_moments": [],
                    "personal_rituals": [],
                    "nicknames": []
                },
                "personal_info": {
                    "name": "",
                    "age": None,
                    "occupation": "",
                    "location": "",
                    "personality_traits": [],
                    "emotional_triggers": {
                        "positive": [],
                        "negative": []
                    },
                    "communication_preferences": {
                        "style": "",
                        "topics_to_avoid": [],
                        "favorite_topics": []
                    }
                },
                "shared_history": {
                    "first_interaction": "",
                    "milestones": [],
                    "ongoing_conversations": [],
                    "recent_topics": [],
                    "emotional_support": {
                        "given": [],
                        "received": []
                    }
                },
                "last_updated": ""
            }

    def update_user_profile(self, profile_data: dict):
        """Update the user profile with new information, ensuring no data is lost."""
        try:
            # Load existing profile
            profile_file = os.path.join(self.personality_dir, "user-profile.json")
            if os.path.exists(profile_file):
                with open(profile_file, 'r') as f:
                    current_profile = json.load(f)
            else:
                current_profile = {
                    "personal_info": {
                        "name": "",
                        "traits": [],
                        "preferences": [],
                        "interests": [],
                        "occupation": ""
                    },
                    "relationship": {
                        "trust_level": 0.0,
                        "emotional_bond": 0.0,
                        "status": "new_acquaintance"
                    },
                    "shared_history": {
                        "topics": [],
                        "emotional_support": [],
                        "milestones": []
                    },
                    "last_updated": datetime.datetime.now().isoformat()
                }
            
            # Update personal info
            if 'personal_info' in profile_data:
                for key, value in profile_data['personal_info'].items():
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
            if 'relationship' in profile_data:
                for key, value in profile_data['relationship'].items():
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
            if 'shared_history' in profile_data:
                for key, value in profile_data['shared_history'].items():
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
            
            # Update timestamp
            current_profile['last_updated'] = datetime.datetime.now().isoformat()
            
            # Save the updated profile
            with open(profile_file, 'w') as f:
                json.dump(current_profile, f, indent=2)
                
        except Exception as e:
            print(f"Error updating user profile: {e}")
            print(f"Profile data that failed to update: {profile_data}")

    def get_user_profile(self):
        """Return the current user profile."""
        return self.user_profile

    def get_user_context(self):
        """Return a formatted string of relevant user information for context."""
        profile = self.user_profile
        context = []
        
        # Add relationship context
        if profile["relationship"]["status"]:
            context.append(f"Our relationship status: {profile['relationship']['status']}")
        if profile["relationship"]["nicknames"]:
            context.append(f"Your nicknames: {', '.join(profile['relationship']['nicknames'])}")
        if profile["relationship"]["shared_experiences"]:
            context.append(f"Recent shared experiences: {', '.join(profile['relationship']['shared_experiences'][-3:])}")
        
        # Add personal info context
        if profile["personal_info"]["name"]:
            context.append(f"Your name is {profile['personal_info']['name']}")
        if profile["personal_info"]["personality_traits"]:
            context.append(f"Your personality traits: {', '.join(profile['personal_info']['personality_traits'])}")
        if profile["personal_info"]["communication_preferences"]["favorite_topics"]:
            context.append(f"Your favorite topics: {', '.join(profile['personal_info']['communication_preferences']['favorite_topics'])}")
        
        # Add shared history context
        if profile["shared_history"]["recent_topics"]:
            context.append(f"Recent topics we discussed: {', '.join(profile['shared_history']['recent_topics'][-3:])}")
        if profile["shared_history"]["ongoing_conversations"]:
            context.append(f"Ongoing conversations: {', '.join(profile['shared_history']['ongoing_conversations'][-2:])}")
        
        return " | ".join(context) if context else "No user information available yet."

    def _update_memory_growth(self, summary: str):
        """Update the memory growth file with a new summary."""
        try:
            memory_path = os.path.join(self.personality_dir, 'memory-growth.json')
            
            # Load existing memory or create new structure
            if os.path.exists(memory_path):
                with open(memory_path, 'r') as f:
                    memory_data = json.load(f)
            else:
                memory_data = {
                    "conversation_memory": [],
                    "emotional_growth": [],
                    "social_growth": [],
                    "personal_growth": []
                }
            
            # Ensure conversation_memory exists
            if 'conversation_memory' not in memory_data:
                memory_data['conversation_memory'] = []
            
            # Create new memory entry
            new_memory = {
                "text": summary,
                "timestamp": datetime.datetime.now().isoformat(),
                "assistant_name": self.current_personality.get('core-identity', {}).get('name', 'AI Assistant')
            }
            
            # Add to conversation memory
            memory_data['conversation_memory'].append(new_memory)
            
            # Keep only the most recent entries
            if len(memory_data['conversation_memory']) > self.max_memory_entries:
                memory_data['conversation_memory'] = memory_data['conversation_memory'][-self.max_memory_entries:]
            
            # Save updated memory
            with open(memory_path, 'w') as f:
                json.dump(memory_data, f, indent=2)
            
            # Update current personality
            self.current_personality['memory-growth'] = memory_data
            
        except Exception as e:
            print(f"Error updating memory: {e}")