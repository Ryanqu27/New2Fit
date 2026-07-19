from slowapi import Limiter
from slowapi.util import get_remote_address

# Global limiter instance — imported by main.py (middleware) and user_router.py (decorators).
# Uses the client's IP address as the rate limit key.
# Swap MemoryStorage for RedisStorage here if you ever scale to multiple servers.
limiter = Limiter(key_func=get_remote_address)
