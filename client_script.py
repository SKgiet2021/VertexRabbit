import os
import sys
import base64
import json
import httpx
import traceback
from openai import OpenAI, OpenAIError
from colorama import init, Fore, Style

# Initialize colorama
init()

# --- CONFIGURATION ---
# --- CONFIGURATION ---
BASE_URL = "https://formatting-powered-physiology-philips.trycloudflare.com/v1"
API_KEY = "vtx-YF7CPuIdnovMLF6lucpmF9iaD3Zvc0Z-"  # Hardcoded for convenience

DEFAULT_MODEL = "glm-4.6"
VISION_MODEL = "glm-4.6" # defaulting to 4.6 as requested "not 4.6v"
REASONING_MODEL = "glm-4.7"

# Custom Headers to bypass firewall/WAF
CUSTOM_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
}

def print_colored(text, color=Fore.WHITE):
    print(f"{color}{text}{Style.RESET_ALL}")

def encode_image(image_path):
    """Encodes an image to base64 and detects MIME type."""
    try:
        with open(image_path, "rb") as image_file:
            data = image_file.read()
            b64 = base64.b64encode(data).decode("utf-8")
            
            # Detect MIME type from file header (magic bytes)
            if data[:8] == b'\x89PNG\r\n\x1a\n':
                mime = "image/png"
            elif data[:2] == b'\xff\xd8':
                mime = "image/jpeg"
            elif data[:6] in (b'GIF87a', b'GIF89a'):
                mime = "image/gif"
            elif data[:4] == b'RIFF' and data[8:12] == b'WEBP':
                mime = "image/webp"
            else:
                mime = "image/jpeg"  # fallback
            
            print_colored(f"Detected MIME: {mime}", Fore.CYAN)
            return b64, mime
    except Exception as e:
        print_colored(f"Error reading image: {e}", Fore.RED)
        return None, None

def test_tool_calling(client):
    """
    Probes the API to see if it supports function calling.
    """
    print_colored("\n🕵️  Probing Tool Support on 'glm-4.7'...", Fore.CYAN)
    
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_current_weather",
                "description": "Get the current weather in a given location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state, e.g. San Francisco, CA",
                        },
                    },
                    "required": ["location"],
                },
            },
        }
    ]

    try:
        response = client.chat.completions.create(
            model="glm-4.7",
            messages=[
                {"role": "system", "content": "You are a helpful assistant. If asked about weather, you MUST use the get_current_weather tool."},
                {"role": "user", "content": "What is the weather in Tokyo?"}
            ],
            tools=tools,
            tool_choice="auto",
            stream=False 
        )

        message = response.choices[0].message
        
        if message.tool_calls:
            print_colored("✅ SUCCESS: The model attempted to call a tool!", Fore.GREEN)
            for tool_call in message.tool_calls:
                print_colored(f"   Function: {tool_call.function.name}", Fore.GREEN)
                print_colored(f"   Arguments: {tool_call.function.arguments}", Fore.GREEN)
        else:
            print_colored("⚠️  No tool call triggered.", Fore.YELLOW)
            print_colored(f"Response: {message.content}", Fore.YELLOW)
            print_colored("The API accepts the schema but the model ignored it.", Fore.YELLOW)

    except Exception as e:
        print_colored("❌ FAILED: API Error.", Fore.RED)
        print_colored(str(e), Fore.RED)

def main():
    print_colored("==========================================", Fore.CYAN)
    print_colored("    Vertex AI (FeatherLabs) Terminal      ", Fore.CYAN)
    print_colored("==========================================", Fore.CYAN)
    print_colored("Commands:", Fore.MAGENTA)
    print_colored(" /model <name>   - Switch models (glm-4.6, 4.7, 4.6v)", Fore.MAGENTA)
    print_colored(" /image <path>   - Analyze image (switches to 4.6v)", Fore.MAGENTA)
    print_colored(" /tools          - Test function calling", Fore.MAGENTA)
    print_colored(" /quit           - Exit", Fore.MAGENTA)
    print_colored("==========================================", Fore.CYAN)

    # Initialize Client with Custom Headers using httpx
    # We must pass the default_headers directly to the http_client or the OpenAI client
    # The clean way in newer openai versions is passing 'default_headers'
    
    try:
        client = OpenAI(
            base_url=BASE_URL, 
            api_key=API_KEY,
            default_headers=CUSTOM_HEADERS
        )
    except Exception as e:
        print_colored(f"Failed to initialize client: {e}", Fore.RED)
        return

    current_model = DEFAULT_MODEL
    messages = [{"role": "system", "content": "You are a helpful AI assistant."}]

    print_colored(f"\nConnected to {BASE_URL}", Fore.GREEN)
    print_colored(f"Current Model: {current_model}\n", Fore.GREEN)

    while True:
        try:
            user_input = input(f"{Fore.BLUE}You ({current_model}): {Style.RESET_ALL}").strip()
            
            if not user_input:
                continue

            # --- Command Handling ---
            if user_input.lower() in ["/quit", "/exit"]:
                break
                
            if user_input.startswith("/model"):
                parts = user_input.split()
                if len(parts) > 1:
                    current_model = parts[1]
                    print_colored(f"Switched to model: {current_model}", Fore.YELLOW)
                return_to_prompt = True
                continue

            if user_input.startswith("/tools"):
                test_tool_calling(client)
                continue

            if user_input.startswith("/image"):
                # Handle /image <path> [optional prompt]
                raw_args = user_input[len("/image"):].strip()
                
                image_path = ""
                user_prompt = "Describe this image in detail." # Default prompt

                # robust parsing for quoted paths
                if raw_args.startswith('"'):
                    # Start of quoted string
                    end_quote = raw_args.find('"', 1)
                    if end_quote != -1:
                        image_path = raw_args[1:end_quote]
                        if len(raw_args) > end_quote + 1:
                            user_prompt = raw_args[end_quote+1:].strip()
                else:
                    # No quotes, split by first space
                    parts = raw_args.split(" ", 1)
                    image_path = parts[0]
                    if len(parts) > 1:
                        user_prompt = parts[1]

                # If prompt is empty after splitting
                if not user_prompt:
                     user_prompt = "Describe this image in detail."

                if not os.path.exists(image_path):
                    print_colored(f"File not found: '{image_path}'", Fore.RED)
                    continue
                
                base64_image, mime_type = encode_image(image_path)
                if not base64_image:
                    continue

                # Check image size
                # User requested 4.7 and 4.6, explicitly NOT 4.6v
                VISION_CAPABLE = ["glm-4.6", "glm-4.7"]
                if current_model in VISION_CAPABLE:
                    model_to_use = current_model
                else:
                    model_to_use = "glm-4.7"  # default fallback if on unknown model
                    
                img_size = len(base64_image) * 3 / 4 / 1024 # approx in KB
                print_colored(f"Sending image ({img_size:.1f} KB) to {model_to_use}...", Fore.MAGENTA)
                print_colored(f"Prompt: {user_prompt}", Fore.MAGENTA)
                
                vision_messages = [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": user_prompt},
                            {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{base64_image}"}},
                        ],
                    }
                ]
                
                try:
                    resp = client.chat.completions.create(
                        model=model_to_use,
                        messages=vision_messages,
                        max_tokens=800,
                        timeout=60
                    )
                    content = resp.choices[0].message.content
                    if not content:
                        print_colored(f"⚠️  Warning: The API returned an empty response.", Fore.YELLOW)
                        print_colored(f"Full Response Object: {resp}", Fore.YELLOW)
                    else:
                        print_colored(f"\nAI: {content}\n", Fore.WHITE)
                except Exception as e:
                    print_colored(f"❌ Image Error: {type(e).__name__}: {e}", Fore.RED)
                    print_colored("--- Full Traceback ---", Fore.RED)
                    traceback.print_exc()
                    print_colored("--- End Traceback ---", Fore.RED)
                
                continue

            # --- Chat ---
            messages.append({"role": "user", "content": user_input})
            print(f"{Fore.GREEN}AI: {Style.RESET_ALL}", end="", flush=True)
            
            full_response = ""
            stream = client.chat.completions.create(
                model=current_model,
                messages=messages,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    print(content, end="", flush=True)
                    full_response += content
            print()
            messages.append({"role": "assistant", "content": full_response})

        except KeyboardInterrupt:
            break
        except Exception as e:
            print_colored(f"\n❌ Error: {type(e).__name__}: {e}", Fore.RED)
            print_colored("--- Full Traceback ---", Fore.RED)
            traceback.print_exc()
            print_colored("--- End Traceback ---", Fore.RED)

if __name__ == "__main__":
    main()
