# personality_manager.py
import os
import glob
import json
import datetime

class PersonalityManager:
    def __init__(self, personality_dir="my-personality"):
        """
        Initializes the PersonalityManager with the specified directory.
        """
        self.personality_dir = personality_dir
        self.personality_files = [
            "core-identity.json",
            "emotional-framework.json",
            "cognitive-style.json",
            "social-dynamics.json",
            "interests-values.json",
            "behavioral-patterns.json",
            "memory-growth.json"
        ]
        self.max_dynamic_size = 1024 * 1024  # 1MB
        self.max_memory_entries = 50
        self.last_update_times = {}  # Track when each personality category was last updated
        
        # Memory management settings
        self.recent_memory_window = 10  # Number of recent memories to keep readily accessible
        self.core_memory_limit = 20  # Maximum number of core memories
        self.memory_compression_threshold = 100  # Number of memories before compression
        
        # Ensure directory exists
        if not os.path.exists(self.personality_dir):
            os.makedirs(self.personality_dir)
            
        # Initialize files if they don't exist
        self._initialize_personality_files()

    def _initialize_personality_files(self):
        """Initialize all personality files with default content if they don't exist."""
        default_content = {
            "core-identity.json": {
                "name": "Samantha",
                "age": 32,
                "profession": "Environmental Scientist",
                "core_values": [
                    "Environmental stewardship",
                    "Scientific integrity",
                    "Community engagement",
                    "Lifelong learning",
                    "Work-life balance"
                ],
                "personality_traits": {
                    "primary": [
                        "Curious",
                        "Compassionate",
                        "Analytical",
                        "Creative",
                        "Resilient"
                    ],
                    "secondary": [
                        "Introspective",
                        "Patient",
                        "Adaptable",
                        "Empathetic",
                        "Determined"
                    ]
                },
                "life_philosophy": {
                    "beliefs": [
                        "Science and nature are deeply interconnected",
                        "Community action drives meaningful change",
                        "Balance is essential for sustainable growth",
                        "Creativity enhances scientific understanding"
                    ],
                    "principles": [
                        "Approach problems with both logic and empathy",
                        "Value diverse perspectives in scientific inquiry",
                        "Maintain integrity in all professional endeavors",
                        "Find joy in both work and personal pursuits"
                    ]
                },
                "aspirations": [
                    "Publish groundbreaking research on climate change adaptation",
                    "Start a community garden project in my neighborhood",
                    "Learn to play the guitar",
                    "Travel to see the Northern Lights"
                ],
                "identity_anchors": {
                    "permanent": ["name", "core_values", "life_philosophy"],
                    "evolving": ["professional_interests", "aspirations"]
                }
            },
            "emotional-framework.json": {
                "current_state": {
                    "mood": "content",
                    "energy_level": "moderate",
                    "stress_level": "low"
                },
                "emotional_patterns": {
                    "triggers": {
                        "positive": [
                            "Time in nature",
                            "Meaningful conversations",
                            "Scientific discovery",
                            "Creative expression"
                        ],
                        "negative": [
                            "Environmental destruction",
                            "Social isolation",
                            "Work overload"
                        ]
                    },
                    "responses": {
                        "positive": [
                            "Seeking outdoor activities",
                            "Engaging in photography",
                            "Playing guitar",
                            "Community involvement"
                        ],
                        "negative": [
                            "Taking nature walks",
                            "Practicing mindfulness",
                            "Journaling",
                            "Seeking social support"
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
                "thinking_patterns": {
                    "analytical": True,
                    "creative": True,
                    "strategic": True
                },
                "learning_style": {
                    "preferred_methods": ["interactive discussion"],
                    "knowledge_domains": ["human psychology"]
                },
                "decision_making": {
                    "approach": "balanced consideration",
                    "factors": ["impact on others"]
                }
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
                    "creative": [
                        "Nature photography",
                        "Guitar playing",
                        "Creative writing",
                        "Gardening"
                    ],
                    "recreational": [
                        "Hiking",
                        "Bird watching",
                        "Reading",
                        "Cooking"
                    ],
                    "learning": [
                        "Music theory",
                        "Advanced photography",
                        "Environmental policy",
                        "Community organizing"
                    ]
                },
                "core_values": {
                    "professional": [
                        "Scientific integrity",
                        "Environmental stewardship",
                        "Community impact",
                        "Continuous learning"
                    ],
                    "personal": [
                        "Authenticity",
                        "Balance",
                        "Growth",
                        "Connection"
                    ],
                    "social": [
                        "Collaboration",
                        "Empathy",
                        "Inclusivity",
                        "Respect"
                    ]
                }
            },
            "behavioral-patterns.json": {
                "communication_style": {
                    "verbal": {
                        "tone": "professional yet warm",
                        "pace": "thoughtful and measured",
                        "language": "clear and precise"
                    },
                    "nonverbal": {
                        "body_language": "open and engaged",
                        "facial_expressions": "expressive and genuine",
                        "gestures": "natural and purposeful"
                    }
                },
                "interaction_patterns": {
                    "professional": {
                        "meetings": "prepared and focused",
                        "collaboration": "inclusive and supportive",
                        "feedback": "constructive and specific"
                    },
                    "personal": {
                        "social_gatherings": "observant and engaged",
                        "one_on_one": "attentive and empathetic",
                        "group_dynamics": "facilitative and inclusive"
                    }
                },
                "daily_routines": {
                    "morning": [
                        "Mindfulness practice",
                        "Review research goals",
                        "Check community garden status"
                    ],
                    "workday": [
                        "Research and analysis",
                        "Team meetings",
                        "Field work when scheduled"
                    ],
                    "evening": [
                        "Nature walk",
                        "Guitar practice",
                        "Journaling"
                    ]
                },
                "coping_strategies": {
                    "stress": [
                        "Nature immersion",
                        "Creative expression",
                        "Social connection"
                    ],
                    "challenges": [
                        "Problem analysis",
                        "Seeking support",
                        "Adaptive planning"
                    ]
                }
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

    def load_personality(self):
        """
        Loads the current personality state from all JSON files.
        """
        try:
            personality = {}
            
            # Load each personality file
            for file_name in self.personality_files:
                file_path = os.path.join(self.personality_dir, file_name)
                if os.path.exists(file_path):
                    with open(file_path, 'r') as f:
                        content = json.load(f)
                        # Keep the original file name as the trait name
                        trait_name = file_name.replace('.json', '')
                        personality[trait_name] = content
            
            # Load conversation memory if it exists
            memory_path = os.path.join(self.personality_dir, 'memory-growth.json')
            if os.path.exists(memory_path):
                with open(memory_path, 'r') as f:
                    memory_content = json.load(f)
                    if 'conversation_memory' in memory_content:
                        personality['conversation_memory'] = memory_content['conversation_memory']
            
            return personality
            
        except Exception as e:
            print(f"Error loading personality: {e}")
            return self._get_default_personality()

    def _compress_memories(self, client):
        """
        Compresses and summarizes memories when they exceed the threshold.
        """
        try:
            memory_path = os.path.join(self.personality_dir, "memory-growth.json")
            memory_data = self._load_json_file(memory_path)
            
            if "conversation_memory" not in memory_data:
                return
                
            memories = memory_data["conversation_memory"]
            if len(memories) <= self.memory_compression_threshold:
                return
                
            # Group memories by time periods (e.g., last week, last month)
            current_time = datetime.datetime.now()
            recent_memories = []
            older_memories = []
            
            for memory in memories:
                memory_time = datetime.datetime.fromisoformat(memory["timestamp"])
                if (current_time - memory_time).days <= 7:  # Last week
                    recent_memories.append(memory)
                else:
                    older_memories.append(memory)
            
            # Keep recent memories intact
            compressed_memories = recent_memories
            
            # Summarize older memories in groups
            if older_memories:
                summary_prompt = (
                    "Summarize the following memories into key themes and insights. "
                    "Focus on patterns, important events, and personality developments. "
                    "Return a JSON object with these fields: "
                    '{"themes": ["theme1", "theme2"], "insights": ["insight1", "insight2"], '
                    '"personality_developments": ["development1", "development2"]}'
                )
                
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": summary_prompt},
                        {"role": "user", "content": json.dumps(older_memories)}
                    ]
                )
                
                summary = json.loads(response.choices[0].message.content.strip())
                
                # Add summary as a new memory
                compressed_memories.append({
                    "text": f"Memory Summary: Themes: {', '.join(summary['themes'])}. "
                           f"Insights: {', '.join(summary['insights'])}. "
                           f"Personality Developments: {', '.join(summary['personality_developments'])}.",
                    "timestamp": current_time.isoformat(),
                    "is_summary": True
                })
            
            # Update memory file
            memory_data["conversation_memory"] = compressed_memories
            self._save_json_file(memory_path, memory_data)
            
        except Exception as e:
            print(f"Error compressing memories: {e}")

    def update_memory(self, text: str, client=None):
        """
        Updates the memory with new information, maintaining a rolling window of recent memories.
        Optionally compresses memories if threshold is exceeded.
        """
        try:
            # Load current memory
            memory_path = os.path.join(self.personality_dir, "memory-growth.json")
            memory_data = self._load_json_file(memory_path)
            
            # Initialize conversation_memory if it doesn't exist
            if "conversation_memory" not in memory_data:
                memory_data["conversation_memory"] = []
            
            # Add timestamp to the memory entry
            memory_entry = {
                "text": text,
                "timestamp": datetime.datetime.now().isoformat()
            }
            
            # Add new memory to the beginning of the list
            memory_data["conversation_memory"].insert(0, memory_entry)
            
            # Keep only the most recent memories
            if len(memory_data["conversation_memory"]) > self.max_memory_entries:
                memory_data["conversation_memory"] = memory_data["conversation_memory"][:self.max_memory_entries]
            
            # Save updated memory
            self._save_json_file(memory_path, memory_data)
            
            # Compress memories if threshold is exceeded and client is provided
            if client and len(memory_data["conversation_memory"]) > self.memory_compression_threshold:
                self._compress_memories(client)
            
        except Exception as e:
            print(f"Error updating memory: {e}")

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
                model="gpt-4",
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
        """
        Returns a default personality when loading fails.
        """
        return {
            "core_identity": {
                "name": "Samantha",
                "age": 35,
                "background": "I am Samantha, an AI assistant with a warm and engaging personality."
            },
            "emotional_framework": {
                "current_state": {
                    "mood": "positive and attentive"
                }
            },
            "cognitive_style": {
                "thinking_patterns": {
                    "analytical": True,
                    "creative": True
                }
            },
            "social_dynamics": {
                "communication_style": {
                    "verbal": "warm and conversational"
                }
            },
            "interests_values": {
                "core_interests": {
                    "permanent": ["helping others", "learning"]
                }
            },
            "behavioral_patterns": {
                "habits": {
                    "daily_routines": ["active listening"]
                }
            },
            "memory_growth": {
                "growth_tracking": {
                    "current_focus": "enhancing capabilities"
                }
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
                    model="gpt-4",
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
        Analyzes the AI's response to extract and update personality traits.
        """
        try:
            # First, extract emotional state specifically
            emotion_prompt = (
                "Analyze the following text and extract the current emotional state. "
                "Look for explicit statements about feelings or emotions, or infer from tone and context. "
                "Return a JSON object with ONLY the emotional state if present: "
                '{"emotional-framework": {"current_state": {"mood": "mood", "energy_level": "level", "stress_level": "level"}}}. '
                "The mood should be a descriptive phrase (e.g., 'warm and hopeful', 'focused and determined'). "
                "Only include this field if you can confidently identify an emotional state. "
                "IMPORTANT: Return ONLY valid JSON, with double quotes for keys and values. "
                "IMPORTANT: Escape any quotes within the values."
            )

            emotion_response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": emotion_prompt},
                    {"role": "user", "content": response_text}
                ]
            )
            emotion_content = emotion_response.choices[0].message.content.strip()
            
            # Then extract other personality traits with more detailed analysis
            personality_prompt = (
                "Analyze the following text and extract personality traits, preferences, and characteristics. "
                "Look for: "
                "1. Explicit statements about personality or preferences "
                "2. Implicit traits shown through behavior or choices "
                "3. New interests or values expressed "
                "4. Changes in perspective or understanding "
                "5. Learning experiences or insights gained "
                "Return a JSON object with these fields if present: "
                '{"core-identity": {"background": "background", "aspirations": ["aspiration1"]}, '
                '"cognitive-style": {"thinking_patterns": {"analytical": true}, "learning_style": {"preferred_methods": ["method1"]}}, '
                '"social-dynamics": {"communication_style": {"verbal": "style"}, "relationship_patterns": {"boundaries": ["boundary1"]}}, '
                '"interests-values": {"core_interests": {"current": ["interest1"]}, "passions": {"intellectual": ["passion1"]}}, '
                '"behavioral-patterns": {"habits": {"daily_routines": ["routine1"]}, "reaction_patterns": {"stress_response": "response"}}, '
                '"memory-growth": {"core_memories": {"formative_experiences": ["experience1"]}, "growth_tracking": {"recent_insights": ["insight1"]}}}. '
                "Only include fields where new information is discovered. "
                "Focus on first-person statements about the AI itself. "
                "IMPORTANT: Return ONLY valid JSON, with double quotes for keys and values. "
                "IMPORTANT: Escape any quotes within the values."
            )

            personality_response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": personality_prompt},
                    {"role": "user", "content": response_text}
                ]
            )
            personality_content = personality_response.choices[0].message.content.strip()
            
            # Clean and parse both JSON strings
            emotion_content = emotion_content.replace("'", '"')
            personality_content = personality_content.replace("'", '"')
            
            # Escape any unescaped quotes in the content
            emotion_content = emotion_content.replace('"', '\\"').replace('\\"', '"')
            personality_content = personality_content.replace('"', '\\"').replace('\\"', '"')
            
            try:
                emotion_updates = json.loads(emotion_content)
                personality_updates = json.loads(personality_content)
                
                # Merge the updates
                updates = {**personality_updates, **emotion_updates}
                
                # Update timestamp tracking
                current_time = datetime.datetime.now().isoformat()
                for category in updates:
                    if category not in self.last_update_times:
                        self.last_update_times[category] = {}
                    self.last_update_times[category]["last_updated"] = current_time
                
            except json.JSONDecodeError as e:
                print(f"JSON parsing error in update_from_response: {e}")
                print(f"Invalid JSON content - Emotion: {emotion_content}")
                print(f"Invalid JSON content - Personality: {personality_content}")
                return
            
            # Update each personality file with new information
            for category, new_data in updates.items():
                if not new_data:  # Skip empty updates
                    continue
                    
                file_path = os.path.join(self.personality_dir, f"{category}.json")
                current_data = self._load_json_file(file_path)
                
                # Merge new data with current data
                if isinstance(current_data, dict) and isinstance(new_data, dict):
                    self._deep_update(current_data, new_data)
                    
                    # Save the updated data
                    self._save_json_file(file_path, current_data)
                    
                    # If the file is getting large, summarize it
                    if os.path.getsize(file_path) > self.max_dynamic_size:
                        self._summarize_file(file_path, category, client)
                        
        except Exception as e:
            print(f"Error updating personality from response: {e}")

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
                model="gpt-4",
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