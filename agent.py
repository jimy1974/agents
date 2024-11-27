import requests
import os
import time
from dotenv import load_dotenv
import os

# Load the .env file
load_dotenv()

# Retrieve the API key
API_TOKEN = os.getenv("huggingFaceApiKey")

if not API_TOKEN:
    raise ValueError("API token not found. Please set 'huggingFaceApiKey' in your .env file.")


API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}
def generate_response(prompt):
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 150,
            "temperature": 0.7,
            "top_p": 0.9,
            "return_full_text": False
        }
    }
    
    # Multiple retry mechanism
    for attempt in range(3):
        try:
            response = requests.post(API_URL, headers=headers, json=payload)
            response_json = response.json()
            
            # Check if response is valid
            if isinstance(response_json, list) and response_json:
                generated_text = response_json[0].get('generated_text', '').strip()
                return generated_text
            
            elif 'error' in response_json:
                print(f"Error: {response_json['error']}")
            else:
                print("Unexpected response format.")
                
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(1)
    
    return "I'm having trouble continuing the conversation."

# Prepare output file
output_file = os.path.join(os.path.dirname(__file__), 'ai_conversation.txt')
open(output_file, 'w').close()

# Initial conversation setup
initial_topic = "What do you think about the nature of consciousness?"

# Initialize conversation
conversation = []
current_speaker = "Alice"

with open(output_file, 'a') as f:
    # Start the conversation
    initial_line = f"{current_speaker}: {initial_topic}"
    conversation.append(initial_line)
    print(initial_line)
    f.write(initial_line + '\n')

    # Set the number of turns for the conversation
    num_turns = 10  # Adjust as needed

    for _ in range(num_turns):
        # Construct the prompt with the conversation history
        prompt = '\n'.join(conversation) + f'\n{current_speaker}:'
        
        # Generate response
        response = generate_response(prompt)
        
        # Process response to get only the current speaker's reply
        response_lines = response.strip().split('\n')
        reply = response_lines[0].strip()

        # Ensure the reply starts with the current speaker's name
        if not reply.startswith(f"{current_speaker}:"):
            reply = f"{current_speaker}: {reply}"

        # Add the reply to the conversation
        conversation.append(reply)
        print(reply)
        f.write(reply + '\n')
        
        # Alternate the speaker
        current_speaker = "Bob" if current_speaker == "Alice" else "Alice"
    
    print(f"\nConversation saved to {output_file}")
