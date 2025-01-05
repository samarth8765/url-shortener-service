from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import redis
import os

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),  
    port=int(os.getenv("REDIS_PORT", 6379)),  
    decode_responses=True
)
class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, limit: int, window: int):
        super().__init__(app)
        self.limit = limit
        self.window = window

    async def dispatch(self, request: Request, call_next):
        try:
            client_ip = request.client.host
            redis_key = f"rate_limit:{client_ip}"

            current_count = redis_client.incr(redis_key)

            if current_count == 1:
                redis_client.expire(redis_key, self.window)

            if current_count > self.limit:
                ttl = redis_client.ttl(redis_key) 
                response = JSONResponse(
                    status_code=429,
                    content={"detail": f"Rate limit exceeded. Try again in {ttl} seconds."},
                )
                return response

            return await call_next(request)

        except redis.RedisError as e:
            response = JSONResponse(
                status_code=500,
                content={"detail": "Rate limiter service unavailable."},
            )
            return response
