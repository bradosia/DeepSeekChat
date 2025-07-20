# python_interface.py
import os
import sys
import requests
import json
from dotenv import load_dotenv

# Set UTF-8 encoding for stdout to handle Unicode characters
import codecs
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())

# Load environment variables from .env file
load_dotenv()
API_KEY = os.getenv("GMI_API_KEY")

# Debug: Print API key status (to stderr to avoid polluting output)
if API_KEY:
    print(f"Debug: API key loaded successfully (length: {len(API_KEY)})", file=sys.stderr)
    print(f"Debug: API key starts with: {API_KEY[:10]}...", file=sys.stderr)
else:
    print("Debug: No API key found in environment variables", file=sys.stderr)
    print("Debug: Available env vars:", [k for k in os.environ.keys() if 'API' in k or 'GMI' in k], file=sys.stderr)

def test_api_connection():
    """Test the API connection and return detailed error information"""
    if not API_KEY:
        return "No API key available"
    
    url = "https://api.gmi-serving.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    payload = {
        "model": "deepseek-ai/DeepSeek-R1-0528",
        "messages": [{"role": "user", "content": "Hello"}],
        "max_tokens": 10
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        if response.status_code == 200:
            return "API connection successful"
        else:
            return f"API returned status {response.status_code}: {response.text[:200]}"
    except requests.exceptions.Timeout:
        return "API timeout"
    except requests.exceptions.ConnectionError:
        return "API connection error"
    except Exception as e:
        return f"API test error: {str(e)}"

# Test API connection on startup
print(f"Debug: API test result: {test_api_connection()}", file=sys.stderr)

def load_speaker_configs():
    """Load speaker configurations from speakers.json"""
    # Try multiple possible paths for speakers.json
    possible_paths = [
        'speakers.json',  # Current directory
        '../speakers.json',  # Parent directory
        '../../speakers.json',  # Grandparent directory
        os.path.join(os.path.dirname(__file__), 'speakers.json'),  # Same directory as script
        os.path.join(os.path.dirname(__file__), '..', 'speakers.json'),  # Parent of script directory
    ]
    
    for path in possible_paths:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"Debug: Successfully loaded speakers.json from {path}", file=sys.stderr)
                return {speaker['name']: speaker for speaker in data['speakers']}
        except FileNotFoundError:
            continue
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in {path}", file=sys.stderr)
            continue
    
    print("Error: speakers.json not found in any of the expected locations", file=sys.stderr)
    print("Searched paths:", possible_paths, file=sys.stderr)
    return {}

def generate_topic():
    """Generate a debate topic using GMI API"""
    # Fallback topics for when API fails
    fallback_topics = [
        "The Ethics of Artificial Intelligence",
        "The Future of Renewable Energy", 
        "Universal Basic Income: Solution or Problem?",
        "Space Exploration vs. Earth Conservation",
        "The Role of Government in Technology",
        "Privacy vs. Security in the Digital Age",
        "The Future of Work and Automation",
        "Climate Change: Individual vs. Systemic Action",
        "The Impact of Social Media on Democracy",
        "Genetic Engineering: Progress or Peril?",
        "The Future of Education in the AI Era",
        "Free Speech in the Age of Social Media",
        "The Ethics of Human Enhancement",
        "Centralized vs. Decentralized Systems",
        "The Future of Transportation and Mobility",
        "Digital Currency vs. Traditional Banking",
        "The Role of Art in Society",
        "Scientific Progress vs. Ethical Boundaries",
        "The Future of Healthcare Technology",
        "Urban Development vs. Environmental Protection"
    ]
    
    # If no API key, use fallback
    if not API_KEY:
        import random
        random.seed()
        topic = random.choice(fallback_topics)
        print(f"Debug: No API key available, using fallback topic: {topic}", file=sys.stderr)
        print(topic)
        return
    
    url = "https://api.gmi-serving.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    # More varied prompts for topic generation
    topic_prompts = [
        "Generate a debate topic about technology and society",
        "Create a debate topic about environmental challenges",
        "Suggest a debate topic about economic systems",
        "Propose a debate topic about human rights and freedoms",
        "Generate a debate topic about scientific advancement",
        "Create a debate topic about education and learning",
        "Suggest a debate topic about healthcare and medicine",
        "Propose a debate topic about space and exploration",
        "Generate a debate topic about privacy and security",
        "Create a debate topic about innovation and progress"
    ]
    
    import random
    random.seed()
    selected_prompt = random.choice(topic_prompts)

    payload = {
        "model": "deepseek-ai/DeepSeek-R1-0528",
        "messages": [
            {
                "role": "system", 
                "content": "Generate a debate topic (5-10 words max). Return ONLY the topic, nothing else."
            },
            {
                "role": "user", 
                "content": selected_prompt
            }
        ],
        "temperature": 0.9,
        "stream": "false"
    }

    try:
        # Check if API key is valid
        if not API_KEY or len(API_KEY.strip()) < 10:
            topic = random.choice(fallback_topics)
            print(f"Debug: Invalid or missing API key (length: {len(API_KEY) if API_KEY else 0}), using fallback topic: {topic}", file=sys.stderr)
            print(topic)
            return
            
        # Log request details to stderr (for audience debug)
        print(f"🔍 TOPIC GENERATION REQUEST DEBUG:", file=sys.stderr)
        print(f"URL: {url}", file=sys.stderr)
        print(f"Headers: {json.dumps(headers, separators=(',', ':'))}", file=sys.stderr)
        print(f"Payload: {json.dumps(payload, separators=(',', ':'))}", file=sys.stderr)
        print(f"API Key (first 20 chars): {API_KEY[:20]}...", file=sys.stderr)
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        # Log response details to stderr (for audience debug)
        print(f"🔍 TOPIC GENERATION RESPONSE DEBUG:", file=sys.stderr)
        print(f"Status Code: {response.status_code}", file=sys.stderr)
        print(f"Response Headers: {json.dumps(dict(response.headers), separators=(',', ':'))}", file=sys.stderr)
        print(f"Response Text: {response.text[:1000]}", file=sys.stderr)
        
        print(f"Debug: Topic Generation Response status: {response.status_code}", file=sys.stderr)
        
        try:
            resp_json = response.json()
            print(f"Debug: Topic Generation Response: {json.dumps(resp_json, indent=2)}", file=sys.stderr)
        except json.JSONDecodeError as e:
            topic = random.choice(fallback_topics)
            print(f"Debug: Failed to parse JSON response: {str(e)}, using fallback topic: {topic}", file=sys.stderr)
            print(topic)
            return
        
        if response.status_code == 200 and "choices" in resp_json and resp_json["choices"]:
            choice = resp_json["choices"][0]
            message = choice.get("message", {})
            
            # Check for content first, then reasoning_content as fallback
            result = message.get("content", "")
            if not result and "reasoning_content" in message:
                # Extract the final response from reasoning_content
                reasoning = message.get("reasoning_content", "")
                # Try to find the actual response in the reasoning
                lines = reasoning.split('\n')
                for line in reversed(lines):  # Start from the end
                    line = line.strip()
                    if line and not line.startswith('Okay,') and not line.startswith('Hmm') and not line.startswith('I need') and not line.startswith('Key points:') and not line.startswith('Remember,') and not line.startswith('As') and not line.startswith('The tension') and not line.startswith('I recall') and not line.startswith('Right,') and not line.startswith('But since') and not line.startswith('We are discussing'):
                        # This looks like the actual response
                        result = line
                        break
                
                if not result:
                    # If we can't extract from reasoning, use the last meaningful line
                    for line in reversed(lines):
                        line = line.strip()
                        if line and len(line) > 20:  # Reasonable length for a response
                            result = line
                            break
            
            # Clean up the result - remove quotes, extra formatting
            result = result.strip('"').strip("'").strip()
            if result and result.lower() != "none" and len(result) > 5:
                print(result)
            else:
                # Use fallback if API returns invalid content
                topic = random.choice(fallback_topics)
                print(f"Debug: API returned invalid content, using fallback topic: {topic}", file=sys.stderr)
                print(topic)
        else:
            # Use fallback if API response is invalid
            error_msg = resp_json.get('error', {}).get('message', 'Unknown error') if isinstance(resp_json, dict) else 'Unknown error'
            topic = random.choice(fallback_topics)
            print(f"Debug: Invalid API response (status {response.status_code}: {error_msg}), using fallback topic: {topic}", file=sys.stderr)
            print(topic)
    except requests.exceptions.Timeout:
        topic = random.choice(fallback_topics)
        print(f"Debug: API timeout, using fallback topic: {topic}", file=sys.stderr)
        print(topic)
    except requests.exceptions.ConnectionError:
        topic = random.choice(fallback_topics)
        print(f"Debug: API connection error, using fallback topic: {topic}", file=sys.stderr)
        print(topic)
    except Exception as e:
        topic = random.choice(fallback_topics)
        print(f"Debug: Unexpected error in topic generation: {str(e)}, using fallback topic: {topic}", file=sys.stderr)
        print(topic)

def send_query(speaker_name, topic, context="", user_question="", is_debate_continuation=False):
    """Send a query to GMI API with speaker-specific prompting"""
    
    print(f"Debug: send_query called with speaker='{speaker_name}', topic='{topic}', context='{context[:50]}...', user_question='{user_question}', is_debate_continuation={is_debate_continuation}", file=sys.stderr)
    
    # Handle topic generation
    if speaker_name == "topic_generator":
        generate_topic()
        return
    
    # Load speaker configurations
    speakers = load_speaker_configs()
    
    if speaker_name not in speakers:
        print(f"Error: Speaker '{speaker_name}' not found in configuration", file=sys.stderr)
        print(f"Debug: Available speakers: {list(speakers.keys())}", file=sys.stderr)
        return
    
    # Generate fallback response if API fails
    def generate_fallback_response():
        # More varied and context-aware fallback responses
        fallback_responses = {
            "Elon Musk": [
                "The future is not something we wait for, it's something we create. We need to think big and act boldly.",
                "Innovation requires taking risks and challenging the status quo. That's how we move humanity forward.",
                "Technology should serve humanity, not the other way around. We must be thoughtful about its development.",
                "We're at a critical juncture where our decisions today will shape the next century. Let's be bold.",
                "The status quo is not an option. We need revolutionary thinking to solve our biggest challenges.",
                "Progress comes from questioning everything and being willing to fail spectacularly.",
                "The best way to predict the future is to build it ourselves. Let's get to work.",
                "We need to think in terms of exponential growth, not linear progress.",
                "The most important thing is to have a vision and execute it relentlessly."
            ],
            "Steve Jobs": [
                "Design is not just what it looks like and feels like. Design is how it works.",
                "Innovation distinguishes between a leader and a follower. We must think differently.",
                "The best way to predict the future is to invent it. Let's create something amazing.",
                "Quality is more important than quantity. One home run is much better than two doubles.",
                "Stay hungry, stay foolish. That's how we keep pushing boundaries.",
                "The intersection of technology and liberal arts is where magic happens.",
                "We're here to put a dent in the universe. Otherwise why else even be here?",
                "Simple can be harder than complex. You have to work hard to get your thinking clean.",
                "Your work is going to fill a large part of your life. Make sure it's something you love."
            ],
            "Albert Einstein": [
                "Imagination is more important than knowledge. Knowledge is limited, imagination encircles the world.",
                "The important thing is not to stop questioning. Curiosity has its own reason for existence.",
                "We cannot solve our problems with the same thinking we used when we created them.",
                "The most incomprehensible thing about the world is that it is comprehensible.",
                "Logic will get you from A to B. Imagination will take you everywhere.",
                "The true sign of intelligence is not knowledge but imagination.",
                "In the middle of difficulty lies opportunity. We must embrace uncertainty.",
                "The world is a dangerous place, not because of those who do evil, but because of those who look on and do nothing.",
                "Peace cannot be kept by force; it can only be achieved by understanding."
            ],
            "Marie Curie": [
                "Nothing in life is to be feared, it is only to be understood. Now is the time to understand more.",
                "Be less curious about people and more curious about ideas. That's where true progress lies.",
                "I am among those who think that science has great beauty. It brings us closer to truth.",
                "The way of progress is neither swift nor easy. We must be patient and persistent.",
                "I have no dress except the one I wear every day. If you are going to be kind enough to give me one, please let it be practical and dark so that I can put it on afterwards to go to the laboratory.",
                "One never notices what has been done; one can only see what remains to be done.",
                "I believe that science has great beauty. A scientist in his laboratory is not only a technician: he is also a child placed before natural phenomena which impress him like a fairy tale.",
                "The future belongs to those who believe in the beauty of their dreams.",
                "We must have perseverance and above all confidence in ourselves."
            ],
            "Nikola Tesla": [
                "The present is theirs; the future, for which I really worked, is mine. Let's build the future together.",
                "The scientists of today think deeply instead of clearly. We need both depth and clarity.",
                "Invention is the most important product of man's creative brain. Let's invent the impossible.",
                "The day science begins to study non-physical phenomena, it will make more progress in one decade than in all the previous centuries of its existence.",
                "I don't care that they stole my idea. I care that they don't have any of their own.",
                "The spread of civilization may be likened to a fire; first, a feeble spark, next a flickering flame, then a mighty blaze, ever increasing in speed and power.",
                "Let the future tell the truth, and evaluate each one according to his work and accomplishments.",
                "The present is theirs; the future, for which I really worked, is mine.",
                "The scientists of today think deeply instead of clearly. One must be sane to think clearly, but one can think deeply and be quite insane."
            ],
            "Ada Lovelace": [
                "The Analytical Engine weaves algebraic patterns just as the Jacquard loom weaves flowers and leaves.",
                "Imagination is the Discovering Faculty, pre-eminently. It is that which penetrates into the unseen worlds.",
                "The more I study, the more insatiable do I feel my genius for it to be. Knowledge is power.",
                "The science of operations, as derived from mathematics more especially, is a science of itself, and has its own abstract truth and value.",
                "I want to put in something about Bernoulli's numbers, in one of my notes, as an example of how the implicit function may be worked out by the engine, without having been worked out by human head and hands first.",
                "The Analytical Engine has no pretensions whatever to originate anything. It can do whatever we know how to order it to perform.",
                "I am much pleased to find how very well I stand work and how my powers of attention and continued effort increase.",
                "The intellectual, the moral, the religious seem to me all naturally bound up and interlinked together.",
                "That brain of mine is something more than merely mortal; as time will show."
            ]
        }
        
        import random
        responses = fallback_responses.get(speaker_name, ["I have important thoughts on this matter that deserve consideration."])
        
        # Use debate round to add some variety and avoid immediate repetition
        random.seed(hash(f"{speaker_name}_{topic}_{len(context)}") % 1000)
        return random.choice(responses)
    
    speaker = speakers[speaker_name]
    
    # Build the prompt based on the context
    if user_question:
        # User question mode
        prompt = f"{speaker['prompt_template']}\n\n"
        prompt += f"Topic: {topic}\n\n"
        if context:
            prompt += f"Previous conversation context:\n{context}\n\n"
        prompt += f"Audience question: \"{user_question}\"\n\n"
        prompt += f"Respond as {speaker_name} in 2-3 sentences. Be direct and authentic to your character."
    elif is_debate_continuation:
        # Debate continuation mode
        prompt = f"{speaker['prompt_template']}\n\n"
        prompt += f"Topic: {topic}\n\n"
        if context:
            prompt += f"Previous conversation context:\n{context}\n\n"
        prompt += f"Continue the debate about {topic} as {speaker_name}. Respond in 2-3 sentences. Stay in character and be direct."
    else:
        # Initial debate mode
        prompt = f"{speaker['prompt_template']}\n\n"
        prompt += f"Topic: {topic}\n\n"
        prompt += f"Start the debate about {topic} as {speaker_name}. Give your initial thoughts in 2-3 sentences. Be engaging and authentic to your character."

    url = "https://api.gmi-serving.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    payload = {
        "model": "deepseek-ai/DeepSeek-R1-0528",
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"Respond as {speaker_name} about {topic}"}
        ],
        "temperature": speaker.get('temperature', 0.7),
        "stream": "false"
    }

    try:
        # Check if API key is valid
        if not API_KEY or len(API_KEY.strip()) < 10:
            print(f"Error: Invalid or missing API key (length: {len(API_KEY) if API_KEY else 0})", file=sys.stderr)
            print("API_FAILED:INVALID_API_KEY")
            print("Using fallback response due to invalid API key")
            print(generate_fallback_response())
            return
        
        # Log request details to stderr (for audience debug)
        print(f"🔍 API REQUEST DEBUG:", file=sys.stderr)
        print(f"URL: {url}", file=sys.stderr)
        print(f"Headers: {json.dumps(headers, separators=(',', ':'))}", file=sys.stderr)
        print(f"Payload: {json.dumps(payload, separators=(',', ':'))}", file=sys.stderr)
        print(f"API Key (first 20 chars): {API_KEY[:20]}...", file=sys.stderr)
            
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        # Log response details to stderr (for audience debug)
        print(f"🔍 API RESPONSE DEBUG:", file=sys.stderr)
        print(f"Status Code: {response.status_code}", file=sys.stderr)
        print(f"Response Headers: {json.dumps(dict(response.headers), separators=(',', ':'))}", file=sys.stderr)
        print(f"Response Text: {response.text[:1000]}", file=sys.stderr)
        
        # Debug response to stderr
        print(f"Debug: API Response status: {response.status_code}", file=sys.stderr)
        print(f"Debug: API Response headers: {dict(response.headers)}", file=sys.stderr)
        
        try:
            resp_json = response.json()
            print(f"Debug: API Response: {json.dumps(resp_json, indent=2)}", file=sys.stderr)
        except json.JSONDecodeError as e:
            print(f"Error: Failed to parse JSON response: {str(e)}", file=sys.stderr)
            print(f"Debug: Raw response text: {response.text[:500]}", file=sys.stderr)
            print("API_FAILED:INVALID_JSON")
            print("Using fallback response due to invalid JSON")
            print(generate_fallback_response())
            return
        
        if response.status_code != 200:
            error_msg = resp_json.get('error', {}).get('message', 'Unknown error') if isinstance(resp_json, dict) else 'Unknown error'
            print(f"Error: API returned status code {response.status_code}: {error_msg}", file=sys.stderr)
            print("API_FAILED:HTTP_ERROR")
            print("Using fallback response due to HTTP error")
            print(generate_fallback_response())
            return
            
        if "choices" in resp_json and resp_json["choices"] and len(resp_json["choices"]) > 0:
            choice = resp_json["choices"][0]
            message = choice.get("message", {})
            
            # Check for content first, then reasoning_content as fallback
            result = message.get("content", "")
            if not result and "reasoning_content" in message:
                # Extract the final response from reasoning_content
                reasoning = message.get("reasoning_content", "")
                # Try to find the actual response in the reasoning
                lines = reasoning.split('\n')
                for line in reversed(lines):  # Start from the end
                    line = line.strip()
                    if line and not line.startswith('Okay,') and not line.startswith('Hmm') and not line.startswith('I need') and not line.startswith('Key points:') and not line.startswith('Remember,') and not line.startswith('As') and not line.startswith('The tension') and not line.startswith('I recall') and not line.startswith('Right,') and not line.startswith('But since') and not line.startswith('We are discussing'):
                        # This looks like the actual response
                        result = line
                        break
                
                if not result:
                    # If we can't extract from reasoning, use the last meaningful line
                    for line in reversed(lines):
                        line = line.strip()
                        if line and len(line) > 20:  # Reasonable length for a response
                            result = line
                            break
            
            if result and result.lower() != "none" and len(result) > 10:
                # Handle Unicode characters properly
                try:
                    print(result)
                except UnicodeEncodeError:
                    # Fallback: encode as UTF-8 and decode, replacing problematic characters
                    print(result.encode('utf-8', errors='replace').decode('utf-8'))
            else:
                print(f"Error: Invalid response content: '{result}'", file=sys.stderr)
                print("API_FAILED:INVALID_CONTENT")
                print("Using fallback response due to invalid content")
                print(generate_fallback_response())
        else:
            print("Error: No 'choices' in API response or empty choices", file=sys.stderr)
            print("API_FAILED:NO_CHOICES")
            print("Using fallback response due to missing choices")
            print(generate_fallback_response())
    except requests.exceptions.RequestException as e:
        print(f"Network Error: {str(e)}", file=sys.stderr)
        print("API_FAILED:NETWORK_ERROR")
        print("Using fallback response due to network error")
        print(generate_fallback_response())
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {str(e)}", file=sys.stderr)
        print("API_FAILED:JSON_ERROR")
        print("Using fallback response due to JSON error")
        print(generate_fallback_response())
    except Exception as e:
        print(f"Unexpected Error: {str(e)}", file=sys.stderr)
        print("API_FAILED:UNEXPECTED_ERROR")
        print("Using fallback response due to unexpected error")
        print(generate_fallback_response())

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python python_interface.py <speaker_name> <topic> [context] [user_question] [is_debate_continuation]")
        print("Example: python python_interface.py 'Elon Musk' 'AI Ethics'")
        print("Example: python python_interface.py 'Steve Jobs' 'Design Philosophy' 'Previous context here' 'User question here' 'true'")
    else:
        speaker_name = sys.argv[1]
        topic = sys.argv[2]
        context = sys.argv[3] if len(sys.argv) > 3 else ""
        user_question = sys.argv[4] if len(sys.argv) > 4 else ""
        is_debate_continuation = sys.argv[5].lower() == 'true' if len(sys.argv) > 5 else False
        
        send_query(speaker_name, topic, context, user_question, is_debate_continuation)
