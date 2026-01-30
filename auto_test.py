import os
import sys
from openai import OpenAI
from colorama import init, Fore, Style

# Initialize colorama
init()

API_KEY = "vtx-lhdkoKai9kBJsyukljqSNuz7_Z2cwc58"
BASE_URL = "https://api-glm.featherlabs.online/v1"

def print_colored(text, color=Fore.WHITE):
    print(f"{color}{text}{Style.RESET_ALL}")

def test_chat():
    print_colored("\n--- 1. Testing Basic Chat (glm-4.6) ---", Fore.CYAN)
    client = OpenAI(base_url=BASE_URL, api_key=API_KEY)
    try:
        response = client.chat.completions.create(
            model="glm-4.6",
            messages=[{"role": "user", "content": "Hello, say 'Test Successful' if you can hear me."}],
            max_tokens=50
        )
        print_colored(f"Response: {response.choices[0].message.content}", Fore.GREEN)
    except Exception as e:
        print_colored(f"Chat Failed: {e}", Fore.RED)

def test_tools():
    print_colored("\n--- 2. Testing Tool Support (glm-4.7) ---", Fore.CYAN)
    client = OpenAI(base_url=BASE_URL, api_key=API_KEY)
    
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_stock_price",
                "description": "Get the current stock price for a symbol",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "symbol": {"type": "string", "description": "The stock symbol, e.g. AAPL"},
                    },
                    "required": ["symbol"],
                },
            },
        }
    ]

    try:
        response = client.chat.completions.create(
            model="glm-4.7",
            messages=[
                {"role": "system", "content": "You are a helpful assistant who MUST use tools when needed."},
                {"role": "user", "content": "What is the stock price of Apple (AAPL) right now?"}
            ],
            tools=tools,
            tool_choice="auto" 
        )

        message = response.choices[0].message
        
        if message.tool_calls:
            print_colored("✅ RESULT: Tool Calls DETECTED!", Fore.GREEN)
            for tool in message.tool_calls:
                print_colored(f"   Function: {tool.function.name}", Fore.GREEN)
                print_colored(f"   Args: {tool.function.arguments}", Fore.GREEN)
        else:
            print_colored("❌ RESULT: No tool calls generated.", Fore.YELLOW)
            print_colored(f"   Response Content: {message.content}", Fore.YELLOW)

    except Exception as e:
        print_colored(f"Tool Test Error: {e}", Fore.RED)

if __name__ == "__main__":
    test_chat()
    test_tools()
