import anthropic
from anthropic import Anthropic
import my_secrets

def setup_claude_client(api_key):
    """
    Set up a Claude API client with the provided API key.
    
    Parameters:
        api_key (str): Your Anthropic API key
    
    Returns:
        anthropic.Anthropic: Configured Claude client
    """
    return Anthropic(api_key=api_key)

def send_message(client, message, model="claude-3-opus-20240229", max_tokens=1000):
    """
    Send a message to Claude and get the response.
    
    Parameters:
        client (anthropic.Anthropic): The configured Claude client
        message (str): The message to send to Claude
        model (str): The model to use (default: claude-3-opus-20240229)
        max_tokens (int): Maximum tokens in response
    
    Returns:
        str: Claude's response
    """
    try:
        message = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            messages=[{
                "role": "user",
                "content": message
            }]
        )
        return message.content[0].text
        
    except Exception as e:
        raise Exception(f"Error sending message: {str(e)}")

def run_query(query):
    # Replace with your actual API key
    API_KEY = my_secrets.ANTHROPIC_KEY
    
    try:
        # Set up the client
        claude = setup_claude_client(API_KEY)
        
        # Send a simple message
        response = send_message(
            claude,
            query,
            model="claude-3-5-haiku-20241022",
            max_tokens=4096
        )
        
        return response
        
    except Exception as e:
        print(f"Error: {e}")

# Example of a more complex conversation
def have_conversation(client, messages, model="claude-3-opus-20240229"):
    """
    Have a multi-turn conversation with Claude.
    
    Parameters:
        client (anthropic.Anthropic): The configured Claude client
        messages (list): List of message dictionaries with 'role' and 'content'
        model (str): The model to use
    
    Returns:
        str: Claude's response
    """
    try:
        response = client.messages.create(
            model=model,
            max_tokens=1000,
            messages=messages
        )
        return response.content[0].text
        
    except Exception as e:
        raise Exception(f"Error in conversation: {str(e)}")

# Example of using the conversation function:
conversation_messages = [
    {"role": "user", "content": "What's the capital of France?"},
    {"role": "assistant", "content": "The capital of France is Paris."},
    {"role": "user", "content": "What's interesting about this city?"}
]