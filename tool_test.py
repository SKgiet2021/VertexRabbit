import requests
import json
from colorama import init, Fore, Style

# Initialize colorama
init()

API_KEY = "vtx-lhdkoKai9kBJsyukljqSNuz7_Z2cwc58"
URL = "https://api-glm.featherlabs.online/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}

def print_colored(text, color=Fore.WHITE):
    print(f"{color}{text}{Style.RESET_ALL}")

def test_tool_support():
    print_colored("\n--- Testing Tool Support on glm-4.7 ---", Fore.CYAN)
    
    # Define a tool schema
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get current weather",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string", "description": "City name"},
                    },
                    "required": ["location"],
                },
            },
        }
    ]

    payload = {
        "model": "glm-4.7",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is the weather in Paris right now?"}
        ],
        "tools": tools,
        "tool_choice": "auto",
        "stream": False
    }

    try:
        response = requests.post(URL, headers=HEADERS, json=payload, timeout=20)
        
        if response.status_code == 200:
            data = response.json()
            message = data['choices'][0]['message']
            
            # Check for tool_calls
            if 'tool_calls' in message and message['tool_calls']:
                print_colored("✅ SUCCESS: The API returned a Tool Call!", Fore.GREEN)
                print(json.dumps(message['tool_calls'], indent=2))
                return True
            else:
                print_colored("⚠️  Ambiguous: Response received, but no tool call.", Fore.YELLOW)
                print_colored(f"Content: {message.get('content')}", Fore.YELLOW)
                return False
        else:
            print_colored(f"❌ Failed with status {response.status_code}", Fore.RED)
            print(response.text)
            return False

    except Exception as e:
        print_colored(f"❌ Exception: {e}", Fore.RED)
        return False

if __name__ == "__main__":
    test_tool_support()
