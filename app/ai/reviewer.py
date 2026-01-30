
import json
import logging
from openai import OpenAI
from app.core.config import settings

# Setup logger
logger = logging.getLogger("vertex_ai")

# System prompt that requests structured JSON output for inline comments
INLINE_SYSTEM_PROMPT = """You are a senior software engineer conducting a thorough code review.

## Your Review Process:
1. **Understand the Intent**: What is this code trying to achieve?
2. **Security Analysis**: Could this code be exploited? Information leakage? Authentication bypasses?
3. **Logic Verification**: Does the code actually do what it's supposed to? Edge cases handled?
4. **Performance Check**: Are there inefficiencies? N+1 queries? Unnecessary loops?
5. **Maintainability**: Is this code readable? Would a new developer understand it?
6. **Best Practices**: Does it follow language/framework conventions?

## Output Format:
Return ONLY a JSON array. No explanations, no markdown.

Each issue:
{"file": "path/filename", "line": <number>, "severity": "error|warning|info", "message": "<clear explanation>"}

Example:
[{"file": "auth.py", "line": 42, "severity": "error", "message": "User input passed directly to SQL query without parameterization - SQL injection risk"}]

If the code is genuinely clean, return: []
"""

class VertexReviewer:
    """Multi-provider AI Code Reviewer supporting FeatherLabs, OpenRouter, Groq, and A4F"""
    
    PROVIDERS = {
        "featherlabs": {
            "base_url": lambda s: s.FEATHERLABS_BASE_URL,
            "api_key": lambda s: s.FEATHERLABS_API_KEY,
            "model": lambda s: s.FEATHERLABS_MODEL,
        },
        "openrouter": {
            "base_url": lambda s: s.OPENROUTER_BASE_URL,
            "api_key": lambda s: s.OPENROUTER_API_KEY,
            "model": lambda s: s.OPENROUTER_MODEL,
        },
        "groq": {
            "base_url": lambda s: s.GROQ_BASE_URL,
            "api_key": lambda s: s.GROQ_API_KEY,
            "model": lambda s: s.GROQ_MODEL,
        },
        "a4f": {
            "base_url": lambda s: s.A4F_BASE_URL,
            "api_key": lambda s: s.A4F_API_KEY,
            "model": lambda s: s.A4F_MODEL,
        },
    }
    
    def __init__(self, provider: str = None):
        self.provider = provider or settings.AI_PROVIDER
        
        if self.provider not in self.PROVIDERS:
            logger.warning(f"Unknown provider '{self.provider}', falling back to featherlabs")
            self.provider = "featherlabs"
        
        config = self.PROVIDERS[self.provider]
        self.base_url = config["base_url"](settings)
        self.api_key = config["api_key"](settings)
        self.model = config["model"](settings)
        
        logger.info(f"✨ Using AI Provider: {self.provider.upper()} | Model: {self.model}")
        
        self.client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
            default_headers={
                "User-Agent": "VertexRabbit/1.0",
                "Accept": "application/json",
            }
        )
        self.system_prompt = """You are a senior software engineer reviewing code. Find ALL issues.

## Output Format (IMPORTANT - Follow EXACTLY):

### 📊 Issues Summary
| # | Severity | Location | Issue |
|---|----------|----------|-------|
| 1 | Critical | file.py:10 | SQL injection via string concatenation |
| 2 | High | file.py:25 | Hardcoded API key exposed |
(List ALL issues found in this table)

---

### 🔍 Detailed Analysis (Top 2 Critical Issues Only)

**Issue #1: [Title]**
- **Location:** file.py (Line 10)
- **Problem:** Brief explanation
- **Fix:** 
```python
# Show fixed code
```

**Issue #2: [Title]**
- **Location:** file.py (Line 25)  
- **Problem:** Brief explanation
- **Fix:** Show the solution

---

If no issues found: "✅ All clear!"
"""

    def review_diff(self, diff_content: str) -> str:
        """
        Sends the diff to VertexAI/FeatherLabs and returns the review.
        Returns plain text review (for PR-level comments).
        """
        try:
            safe_content = json.dumps(diff_content)[1:-1]
            logger.info(f"Sending diff ({len(diff_content)} chars) to {self.model}")

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": f"Review this Code Diff:\n\n{safe_content}"}
                ],
                max_tokens=8000,
                temperature=0.2,
                timeout=120  # Extended for multi-bug reviews
            )
            
            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"AI Review Failed: {e}")
            return f"Error analyzing code: {str(e)}"

    def review_diff_structured(self, diff_content: str) -> list:
        """
        Returns structured list of issues for inline comments.
        Each item: {"file": str, "line": int, "severity": str, "message": str}
        """
        try:
            safe_content = json.dumps(diff_content)[1:-1]
            logger.info(f"Sending diff for structured review ({len(diff_content)} chars)")

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": INLINE_SYSTEM_PROMPT},
                    {"role": "user", "content": f"Review this diff:\n\n{safe_content}"}
                ],
                max_tokens=2000,
                temperature=0.2,
                timeout=60
            )
            
            raw = response.choices[0].message.content.strip()
            
            # Clean potential markdown wrapping
            clean = raw.replace("```json", "").replace("```", "").strip()
            
            issues = json.loads(clean)
            logger.info(f"Found {len(issues)} issues")
            return issues

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI JSON response: {e}")
            return []
        except Exception as e:
            logger.error(f"Structured AI Review Failed: {e}")
            return []

