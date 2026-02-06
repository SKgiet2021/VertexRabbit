
import time
import asyncio
import logging

logger = logging.getLogger("limiter")

class RateLimiter:
    """
    Token Bucket Rate Limiter to ensure we don't exceed API limits.
    Default: 10 RPM (Requests Per Minute)
    """
    def __init__(self, max_tokens: int = 10, refill_period: int = 60):
        self.max_tokens = max_tokens
        self.tokens = max_tokens
        self.refill_period = refill_period # 60 seconds
        self.last_refill = time.monotonic()
        self.lock = asyncio.Lock()
    
    async def acquire(self):
        """
        Wait until a token is available.
        """
        async with self.lock:
            # Refill tokens based on time passed
            now = time.monotonic()
            elapsed = now - self.last_refill
            
            # Refill rate: max_tokens per refill_period
            # Example: 10 tokens / 60s = 0.166 tokens/sec
            refill_amount = elapsed * (self.max_tokens / self.refill_period)
            
            if refill_amount > 0:
                self.tokens = min(self.max_tokens, self.tokens + refill_amount)
                self.last_refill = now
            
            # If we have tokens, consume one and return
            if self.tokens >= 1:
                self.tokens -= 1
                return
            
            # If no tokens, calculate wait time
            # We need 1.0 token. We have self.tokens (e.g. 0.2). We need 0.8 more.
            # Time needed = needed_tokens / (tokens_per_sec)
            # tokens_per_sec = max / period
            needed = 1.0 - self.tokens
            tokens_per_sec = self.max_tokens / self.refill_period
            wait_time = needed / tokens_per_sec
            
            logger.warning(f"Rate limit reached. Waiting {wait_time:.2f}s...")
            await asyncio.sleep(wait_time)
            
            # After waiting, we technically have enough, but let's just reset logic
            # simple recursion or just consume. 
            # To be precise, we just consumed the time, so we take the token.
            self.tokens = 0 # effectively 0 after consumption
            self.last_refill = time.monotonic()

# Global Limiter Instance
# 10 reqs / 60 sec
global_limiter = RateLimiter(max_tokens=10, refill_period=60)
