import logging
import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from app.middleware.timeout import TimeoutMiddleware
from app.dependencies import get_db_client, get_ollama_client_dep
from app.schemas import HealthResponse, ErrorResponse

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Rate limiter setup
limiter = Limiter(key_func=get_remote_address)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager."""
    logger.info("Starting FastAPI application")
    
    # Initialize ChromaDB client
    try:
        from app.dependencies import get_chromadb_client
        chromadb_client = get_chromadb_client()
        app.state.chromadb_client = chromadb_client
        logger.info("ChromaDB client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize ChromaDB: {e}")
        app.state.chromadb_client = None
    
    # Initialize Ollama client
    try:
        from app.dependencies import get_ollama_client
        ollama_client = get_ollama_client()
        app.state.ollama_client = ollama_client
        logger.info("Ollama client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Ollama: {e}")
        app.state.ollama_client = None
    
    yield
    
    # Cleanup
    logger.info("Shutting down FastAPI application")

# Initialize FastAPI with lifespan and API prefix
app = FastAPI(
    title="Cognitive Cache API",
    description="Backend API for Cognitive Cache RAG system",
    version="0.1.0",
    lifespan=lifespan,
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add GZip compression middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Add rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Request ID middleware
class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        response: Response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

app.add_middleware(RequestIDMiddleware)

# Add timeout middleware for /api/v1/query endpoint
app.add_middleware(TimeoutMiddleware, timeout_seconds=30)

# Health endpoint
@app.get("/api/v1/health", response_model=HealthResponse)
@limiter.limit("10/minute")
async def health_check(
    request: Request,
    chromadb_client = Depends(get_db_client),
    ollama_client = Depends(get_ollama_client_dep),
):
    """Health check endpoint with detailed service status."""
    return HealthResponse(
        status="healthy",
        version="0.1.0",
        services={
            "ollama": ollama_client.get_status(),
            "chromadb": chromadb_client.get_status(),
        },
        request_id=request.state.request_id,
    )

# Custom exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if app.debug else "An unexpected error occurred",
            "request_id": getattr(request.state, "request_id", "unknown"),
        },
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
