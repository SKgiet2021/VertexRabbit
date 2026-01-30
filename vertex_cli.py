
import os
import sys
import json
import argparse
from colorama import init, Fore, Style
from app.ai.reviewer import VertexReviewer

init()

# Prompt to ensure AI gives us machine-readable line numbers
CLI_SYSTEM_PROMPT = """You are a code reviewer. Find bugs in this code.
Output strictly Valid JSON list of objects. No markdown.
Format:
[
    {"line": 10, "message": "SQL Injection risk", "severity": "error"},
    {"line": 25, "message": "Typo", "severity": "warning"}
]
If no bugs, output [].
"""

def create_fake_diff(file_path, content):
    """Wraps file content in a git-like diff format."""
    return f"""diff --git a/{file_path} b/{file_path}
new file mode 100644
--- /dev/null
+++ b/{file_path}
@@ -0,0 +1,{len(content.splitlines())} @@
{'+ ' + content.replace(os.linesep, os.linesep + '+ ')}
"""

def generate_sarif(issues, project_root):
    """Converts a list of issues into a SARIF log."""
    runs = []
    
    # Group by file
    for file_path, bugs in issues.items():
        results = []
        for bug in bugs:
            results.append({
                "level": bug.get("severity", "warning"),
                "message": {"text": bug.get("message", "Issue detected")},
                "locations": [{
                    "physicalLocation": {
                        "artifactLocation": {"uri": file_path.replace("\\", "/")},
                        "region": {"startLine": bug.get("line", 1)}
                    }
                }],
                "ruleId": "AI-REVIEW"
            })
        
        if results:
            runs.append({
                "tool": {"driver": {"name": "VertexRabbit", "version": "1.0"}},
                "results": results
            })

    return {
        "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
        "version": "2.1.0",
        "runs": runs
    }

def scan_directory(path, reviewer):
    print(f"{Fore.CYAN}🐰 VertexRabbit CLI - Scanning: {path}{Style.RESET_ALL}")
    
    files_to_scan = []
    supported_ext = {'.py', '.js', '.ts', '.tsx', '.jsx', '.java', '.go', '.rs', '.cpp', '.c'}

    for root, _, files in os.walk(path):
        for file in files:
            if any(file.endswith(ext) for ext in supported_ext):
                files_to_scan.append(os.path.join(root, file))

    if not files_to_scan:
        print(f"{Fore.RED}No supported code files found.{Style.RESET_ALL}")
        return

    print(f"Found {len(files_to_scan)} files. Starting review...\n")
    
    all_issues = {}

    for file_path in files_to_scan:
        rel_path = os.path.relpath(file_path, path)
        print(f"{Fore.YELLOW}Analyzing {rel_path}...{Style.RESET_ALL}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if not content.strip(): continue

            # Override system prompt to force JSON
            reviewer.system_prompt = CLI_SYSTEM_PROMPT
            
            # Send file content as a diff
            diff = create_fake_diff(rel_path, content)
            raw_response = reviewer.review_diff(diff)
            
            # Parse JSON response
            try:
                # Clean potential markdown wrapping
                clean_json = raw_response.replace("```json", "").replace("```", "").strip()
                bugs = json.loads(clean_json)
                
                if bugs:
                    all_issues[rel_path] = bugs
                    print(f"{Fore.RED}Found {len(bugs)} issues.{Style.RESET_ALL}")
                else:
                    print(f"{Fore.GREEN}Clean.{Style.RESET_ALL}")

            except json.JSONDecodeError:
                print(f"{Fore.RED}AI returned invalid JSON: {raw_response[:50]}...{Style.RESET_ALL}")

        except Exception as e:
            print(f"{Fore.RED}Failed to analyze {rel_path}: {e}{Style.RESET_ALL}")

    # Generate SARIF Report
    if all_issues:
        sarif_data = generate_sarif(all_issues, path)
        output_file = os.path.join(path, "vertex_report.sarif")
        with open(output_file, "w") as f:
            json.dump(sarif_data, f, indent=2)
            
        print(f"\n{Fore.MAGENTA}✅ Scan Complete! Report saved to: {output_file}{Style.RESET_ALL}")
        print(f"👉 Install 'SARIF Viewer' extension in VS Code and open this file to see bugs inline!")
    else:
        print(f"\n{Fore.GREEN}✅ Scan Complete! No bugs found.{Style.RESET_ALL}")

def main():
    parser = argparse.ArgumentParser(description="VertexRabbit Local Scanner")
    parser.add_argument("path", help="Path to the project folder to review")
    args = parser.parse_args()
    
    if not os.path.exists(args.path):
        print(f"Error: Path '{args.path}' does not exist.")
        return

    reviewer = VertexReviewer()
    scan_directory(args.path, reviewer)

if __name__ == "__main__":
    main()
