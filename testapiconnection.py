import os
from pathlib import Path
from dotenv import load_dotenv
from anthropic import Anthropic

def test_claude_connection():
    #please replace the API key with your actual API key path stored in a file in your local
    user_home = os.path.expanduser("~")  # Gets your home directory
    env_path = Path(user_home) / "Desktop" / "2025 Year of Snake" / "Interview Prep" / "local files" / ".env"
    
    print(f"Looking for .env file at: {env_path}")
    
    # Check if the file exists
    if not env_path.exists():
        print(f"ERROR: File not found at {env_path}")
        print("Checking parent directory for files...")
        
        parent_dir = env_path.parent
        if parent_dir.exists():
            print(f"Files in {parent_dir}:")
            for file in os.listdir(parent_dir):
                print(f"  - {file}")
        else:
            print(f"Parent directory {parent_dir} doesn't exist")
        return False
    
    print(f"Found .env file at: {env_path}")
    
    # Load the .env file
    load_dotenv(dotenv_path=env_path)
    
    # Get the API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not found in .env file")
        print("Make sure your .env file contains the ANTHROPIC_API_KEY variable")
        return False
    
    # Mask the API key for security when printing
    masked_key = f"{api_key[:4]}...{api_key[-4:]}" if len(api_key) > 8 else "Key too short"
    print(f"Loaded API key: {masked_key}")
    
    try:
        # Initialize the Anthropic client
        client = Anthropic(api_key=api_key)
        
        # Send a simple message to test the connection
        message = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=300,
            messages=[
                {"role": "user", "content": "Hello Claude, this is a test message. Please respond with a short greeting."}
            ]
        )
        
        # Print the response
        print("\nCONNECTION SUCCESSFUL! Claude's response:")
        print(message.content[0].text)
        return True
        
    except Exception as e:
        print(f"\nERROR connecting to Claude API: {e}")
        return False

if __name__ == "__main__":
    print("Testing connection to Claude API...")
    test_claude_connection()