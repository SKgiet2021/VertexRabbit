
import json
import logging
from openai import OpenAI
from app.core.config import settings

# Setup logger
logger = logging.getLogger("vertex_ai")

# System prompt that requests structured JSON output for inline comments
INLINE_SYSTEM_PROMPT = """You are a senior software engineer conducting a thorough code review.

## Your Goal:
Identify specific bugs, security risks, and logic errors. Do NOT comment on formatting/style unless critical.

## Output Format:
You MUST return a VALID JSON array of objects. Do not wrap in markdown code blocks. Just the raw JSON.

Each object must follow this schema:
{
    "path": "path/filename.ext", 
    "line": <int>, 
    "severity": "error|warning|info", 
    "body": "<concise comment>"
}

- `path`: Must match the filename in the diff exactly.
- `line`: The line number in the NEW file where the issue exists.
- `body`: Be direct and constructive. Suggest a fix if possible.

CRITICAL:
You can ONLY comment on lines that are **ADDED** or **MODIFIED** in the diff (lines starting with `+`).
Do NOT comment on unchanged context lines. GitHub will reject comments on lines that are not part of the active diff hunk.
If a critical issue exists in unchanged code, IGNORE it in this inline mode.

Example:
[
    {"path": "app/auth.py", "line": 42, "severity": "error", "body": "SQL Injection vulnerability. Use parameterized queries."},
    {"path": "app/utils.py", "line": 15, "severity": "warning", "body": "Unused variable `x`."}
]

If the code looks good, return an empty array: []
"""


from openai import AsyncOpenAI
import asyncio
from app.core.limiter import global_limiter

class VertexReviewer:
    """Multi-provider AI Code Reviewer supporting FeatherLabs, OpenRouter, Groq, and A4F"""
    
    PROVIDERS = {
        "a4f": {
            "base_url": lambda s: s.A4F_BASE_URL,
            "api_key": lambda s: s.A4F_API_KEY,
            "model": lambda s: s.A4F_MODEL,
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
        }
    }
    
    def __init__(self, provider: str = None):
        self.provider = provider or settings.AI_PROVIDER
        
        if self.provider not in self.PROVIDERS:
            logger.warning(f"Unknown provider '{self.provider}', falling back to a4f")
            self.provider = "a4f"
        
        config = self.PROVIDERS[self.provider]
        self.base_url = config["base_url"](settings)
        self.api_key = config["api_key"](settings)
        self.model = config["model"](settings)
        
        logger.info(f"✨ Using AI Provider: {self.provider.upper()} | Model: {self.model}")
        
        self.client = AsyncOpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
            default_headers={
                "User-Agent": "VertexRabbit/1.0",
                "Accept": "application/json",
            }
        )
        self.system_prompt = """You are a senior software engineer reviewing code. Find ALL issues."""

    async def review_diff(self, diff_content: str) -> str:
        """
        Sends the diff to AI and returns the review.
        """
        try:
            safe_content = json.dumps(diff_content)[1:-1]
            logger.info(f"Sending diff ({len(diff_content)} chars) to {self.model}")

            await global_limiter.acquire()
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": f"Review this Code Diff:\n\n{safe_content}"}
                ],
                max_tokens=8000,
                temperature=0.2,
                timeout=120,
                stream=True
            )
            
            full_response = ""
            async for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
            
            return full_response.strip()

        except Exception as e:
            logger.error(f"AI Review Failed: {e}")
            return f"Error analyzing code: {str(e)}"

    async def review_diff_structured(self, diff_content: str) -> list:
        """
        Returns structured list of issues for inline comments.
        Each item: {"path": str, "line": int, "severity": str, "body": str}
        """
        try:
            safe_content = json.dumps(diff_content)[1:-1]
            logger.info(f"Sending diff for structured review ({len(diff_content)} chars)")

            await global_limiter.acquire()

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": INLINE_SYSTEM_PROMPT},
                    {"role": "user", "content": f"Review this diff:\n\n{safe_content}"}
                ],
                max_tokens=2000,
                temperature=0.2,
                timeout=60,
                stream=True
            )
            
            raw = ""
            async for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    raw += chunk.choices[0].delta.content
            
            raw = raw.strip()
            
            import re
            json_match = re.search(r'\[.*\]', raw, re.DOTALL)
            if json_match:
                clean = json_match.group(0)
            else:
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

