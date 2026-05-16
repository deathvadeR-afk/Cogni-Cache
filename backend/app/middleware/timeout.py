import asyncio
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
import logging

logger = logging.getLogger(__name__)

class TimeoutMiddleware(BaseHTTPMiddleware):
    """Middleware to enforce timeout on specific endpoints."""
    
    def __init__(self, app, timeout_seconds: int = 600):
        super().__init__(app)
        self.timeout_seconds = timeout_seconds
        self.target_path = "/api/v1/query"
    
    async def dispatch(self, request: Request, call_next):
        if request.url.path == self.target_path:
            try:
                return await asyncio.wait_for(
                    call_next(request), 
                    timeout=self.timeout_seconds
                )
            except asyncio.TimeoutError:
                logger.warning(f"Request to {self.target_path} timed out after {self.timeout_seconds}s")
                return JSONResponse(
                    status_code=504,
                    content={
                        "error": "Gateway Timeout",
                        "detail": f"Request timed out after {self.timeout_seconds} seconds",
                        "request_id": getattr(request.state, "request_id", "unknown"),
                    },
                )
        return await call_next(request)
