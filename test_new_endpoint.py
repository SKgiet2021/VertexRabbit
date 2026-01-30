import os
import sys
import base64
import json
from openai import OpenAI
from colorama import init, Fore, Style

init()

BASE_URL = "https://formatting-powered-physiology-philips.trycloudflare.com/v1"
API_KEY = "vtx-YF7CPuIdnovMLF6lucpmF9iaD3Zvc0Z-"

CUSTOM_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
}

def print_colored(text, color=Fore.WHITE):
    print(f"{color}{text}{Style.RESET_ALL}")

def encode_image(image_path):
    if not os.path.exists(image_path):
        print_colored(f"File not found: {image_path}", Fore.RED)
        return None, None
        
    with open(image_path, "rb") as image_file:
        data = image_file.read()
        b64 = base64.b64encode(data).decode("utf-8")
        
        if data[:8] == b'\x89PNG\r\n\x1a\n': mime = "image/png"
        elif data[:2] == b'\xff\xd8': mime = "image/jpeg"
        else: mime = "image/jpeg"
        
        return b64, mime

def test_image(client, image_path, model):
    print_colored(f"\n--- Testing {model} with {os.path.basename(image_path)} ---", Fore.CYAN)
    
    b64, mime = encode_image(image_path)
    if not b64: return

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Describe this image."},
                        {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}}
                    ]
                }
            ],
            max_tokens=300,
            timeout=60
        )
        content = response.choices[0].message.content
        if content:
            print_colored(f"✅ Success ({model}): {content}", Fore.GREEN)
        else:
            print_colored(f"⚠️ Empty Response ({model})", Fore.YELLOW)
            print(response)

    except Exception as e:
        print_colored(f"❌ Error ({model}): {e}", Fore.RED)

def main():
    client = OpenAI(base_url=BASE_URL, api_key=API_KEY, default_headers=CUSTOM_HEADERS)
    
    files = [
        r"C:\Users\swadh\Documents\A4F.co Model WebUI Chat\random.jpg",
        r"C:\Users\swadh\Documents\A4F.co Model WebUI Chat\Safety_B.png"
    ]
    
    models = ["glm-4.7", "glm-4.6"]
    
    for file in files:
        for model in models:
            test_image(client, file, model)

if __name__ == "__main__":
    main()
