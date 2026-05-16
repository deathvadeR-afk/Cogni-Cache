import logging
import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, StreamingResponse
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from app.middleware.timeout import TimeoutMiddleware
from app.dependencies import get_db_client, get_ollama_client_dep
from app.schemas import HealthResponse, ErrorResponse, IngestRequest, IngestResponse, TaskResponse, SourcesResponse, QueryRequest, QueryResponse
from app.task_storage import TaskStorage
from app.ingest_tasks import process_ingest_task
from app.rag_pipeline import RAGPipeline

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
    
    # Initialize task storage
    app.state.task_storage = TaskStorage()
    
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
    
    # Initialize RAG pipeline
    try:
        if app.state.chromadb_client and app.state.ollama_client:
            app.state.rag_pipeline = RAGPipeline(
                app.state.chromadb_client,
                app.state.ollama_client
            )
            logger.info("RAG pipeline initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize RAG pipeline: {e}")
        app.state.rag_pipeline = None
    
    # Initialize APScheduler for daily cleanup
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        func=lambda: app.state.task_storage.cleanup_old_tasks(days=7),
        trigger=CronTrigger(hour=0, minute=0, timezone="UTC"),
        id="cleanup_old_tasks",
        name="Daily cleanup of tasks older than 7 days",
    )
    scheduler.start()
    app.state.scheduler = scheduler
    logger.info("APScheduler started with daily cleanup job")
    
    yield
    
    # Cleanup
    scheduler.shutdown()
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

# Request size limit middleware (10MB)
class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Check content-length header for POST/PUT requests
        if request.method in ("POST", "PUT", "PATCH"):
            content_length = request.headers.get("content-length")
            if content_length:
                size = int(content_length)
                max_size = 10 * 1024 * 1024  # 10MB
                if size > max_size:
                    return JSONResponse(
                        status_code=413,
                        content={
                            "error": "Request entity too large",
                            "detail": f"Request size {size} bytes exceeds 10MB limit",
                            "request_id": getattr(request.state, "request_id", "unknown"),
                        },
                    )
        
        response: Response = await call_next(request)
        return response

app.add_middleware(RequestSizeLimitMiddleware)

# Add timeout middleware for /api/v1/query endpoint
app.add_middleware(TimeoutMiddleware, timeout_seconds=600)

# Health endpoint
@app.get("/api/v1/health", response_model=HealthResponse)
@limiter.limit("10/minute")
async def health_check(request: Request):
    """Health check endpoint with detailed service status."""
    # Use app state clients (already initialized during lifespan)
    # This avoids blocking on client initialization during health check
    chromadb_client = request.app.state.chromadb_client
    ollama_client = request.app.state.ollama_client
    
    return HealthResponse(
        status="healthy",
        version="0.1.0",
        services={
            "ollama": ollama_client.get_status() if ollama_client else {"status": "not_initialized"},
            "chromadb": chromadb_client.get_status() if chromadb_client else {"status": "not_initialized"},
        },
        request_id=request.state.request_id,
    )

# Ingest endpoint
@app.post("/api/v1/ingest", response_model=IngestResponse)
@limiter.limit("10/minute")
async def ingest(
    request: Request,
    ingest_request: IngestRequest,
    background_tasks: BackgroundTasks,
):
    """
    Ingest content from article or YouTube video.
    
    For articles: content field should contain extracted text.
    For YouTube: content is ignored, transcript is fetched server-side.
    """
    task_storage: TaskStorage = request.app.state.task_storage
    chromadb_client = request.app.state.chromadb_client
    
    # Create task
    task_id = task_storage.create_task(
        source_type=ingest_request.source_type.value,
        url=ingest_request.url,
        content=ingest_request.content,
    )
    
    # Add background task
    background_tasks.add_task(
        process_ingest_task,
        task_id=task_id,
        source_type=ingest_request.source_type.value,
        url=ingest_request.url,
        content=ingest_request.content,
        task_storage=task_storage,
        chromadb_client=chromadb_client,
    )
    
    return IngestResponse(
        task_id=task_id,
        status="processing",
        message="Ingestion started",
    )

# Task status endpoint
@app.get("/api/v1/tasks/{task_id}", response_model=TaskResponse)
@limiter.limit("10/minute")
async def get_task(
    request: Request,
    task_id: str,
):
    """Get task status and result."""
    task_storage: TaskStorage = request.app.state.task_storage
    task_data = task_storage.get_task(task_id)
    
    if not task_data:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Task not found")
    
    return TaskResponse(
        task_id=task_data["task_id"],
        status=task_data["status"],
        source_type=task_data.get("source_type"),
        url=task_data.get("url"),
        created_at=task_data.get("created_at"),
        completed_at=task_data.get("completed_at"),
        result=task_data.get("result"),
        error=task_data.get("error"),
    )

# Sources endpoint
@app.get("/api/v1/sources", response_model=SourcesResponse)
@limiter.limit("10/minute")
async def get_sources(request: Request):
    """Get all ingested sources with metadata."""
    chromadb_client = request.app.state.chromadb_client
    if not chromadb_client:
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail="ChromaDB client not initialized")
    sources = chromadb_client.get_sources()
    return SourcesResponse(sources=sources)

# Query endpoint
@app.post("/api/v1/query")
@limiter.limit("10/minute")
async def query(
    request: Request,
    query_request: QueryRequest,
):
    """
    Query the RAG system with streaming response.
    
    Supports multi-turn conversation history and returns inline citations.
    """
    rag_pipeline: RAGPipeline = request.app.state.rag_pipeline
    
    if not rag_pipeline:
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail="RAG pipeline not initialized")
    
    # Generate conversation_id if not provided
    conversation_id = query_request.conversation_id or str(uuid.uuid4())
    
    # Run the query
    result = rag_pipeline.query(
        query=query_request.query,
        filter=None,
        history=query_request.history
    )
    
    return QueryResponse(
        response=result["response"],
        citations=result["citations"],
        conversation_id=conversation_id
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
