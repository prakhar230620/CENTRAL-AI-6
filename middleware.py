from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import time
from config import settings

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.request_counts = {}

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        current_time = time.time()

        # Clean up old entries
        self.request_counts = {ip: [t for t in times if current_time - t < 60]
                               for ip, times in self.request_counts.items()}

        if client_ip in self.request_counts:
            if len(self.request_counts[client_ip]) >= settings.api_rate_limit:
                raise HTTPException(status_code=429, detail="Rate limit exceeded")
            self.request_counts[client_ip].append(current_time)
        else:
            self.request_counts[client_ip] = [current_time]

        response = await call_next(request)
        return response

class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            return JSONResponse(status_code=500, content={"detail": str(e)})