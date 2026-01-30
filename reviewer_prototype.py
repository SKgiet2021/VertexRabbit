"""Reviewer Prototype: Validates if the AI can catch bugs in a diff."""

import os
import json
from openai import OpenAI
from colorama import init, Fore, Style

init()

# Config
BASE_URL = "https://api-glm.featherlabs.online/v1"
API_KEY = "vtx-lhdkoKai9kBJsyukljqSNuz7_Z2cwc58" # From tool_test.py
MODEL = "glm-4.6"

SYSTEM_PROMPT = """
You are an expert Senior Software Engineer doing a Code Review.
Analyze the provided GIT DIFF and identify ANY issues.

Focus on:
1. Security Vulnerabilities (Injection, PII leaks, etc.)
2. Logic Errors
3. Performance Issues
4. Best Practices

Output JSON format:
{
    "reviews": [
        {
            "file": "filename",
            "line": line_number,
            "type": "issue|suggestion|praise",
            "severity": "critical|warning|info",
            "message": "Brief explanation",
            "suggestion": "Corrected code snippet (optional)"
        }
    ],
    "summary": "Brief summary of the PR"
}
"""

def read_diff(path):
    with open(path, "r") as f:
        return f.read()

def review_diff(diff_content):
    client = OpenAI(
        base_url=BASE_URL, 
        api_key=API_KEY,
        default_headers={
            "User-Agent": "VertexRabbit-Test/1.0",
            "Accept": "application/json"
        }
    )
    
    print(f"{Fore.CYAN}Sending Diff to {MODEL}...{Style.RESET_ALL}")
    
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Review this Diff:\n\n{diff_content}"}
            ],
            # response_format={"type": "json_object"},  <-- REMOVED (causes 500 on some proxies)
            max_tokens=2000
        )
        
        content = response.choices[0].message.content
        
        # Clean up code blocks if present
        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "")
        elif content.startswith("```"):
            content = content.replace("```", "")
            
        return content.strip()
        
    except Exception as e:
        print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
        return None

def main():
    diff_path = "sample_buggy_diff.txt"
    
    if not os.path.exists(diff_path):
        print(f"File not found: {diff_path}")
        return

    diff = read_diff(diff_path)
    print(f"{Fore.YELLOW}Analyzing {diff_path}...{Style.RESET_ALL}\n")
    
    result = review_diff(diff)
    
    if result:
        print(f"\n{Fore.GREEN}--- AI Review Result ---{Style.RESET_ALL}")
        print(result)
        
        # Validation
        print(f"\n{Fore.MAGENTA}--- Validation ---{Style.RESET_ALL}")
        if "SQL Injection" in result or "injection" in result.lower():
            print("✅ Caught SQL Injection")
        else:
            print("❌ Added SQL Injection")
            
        if "password" in result.lower() and "log" in result.lower():
             print("✅ Caught Password Logging")
        else:
             print("❌ Missed Password Logging")

if __name__ == "__main__":
    main()
