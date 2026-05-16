# Cognitive Cache

A hyper-personalized, fully private AI companion that acts as an extension of your memory by silently ingesting, cataloging, and recalling your web consumption.

## Overview

Cognitive Cache is a 100% local, open-source "Second Brain" AI assistant that:

1. **Ingests** text from web articles and YouTube transcripts via a browser extension
2. **Processes** and stores content in a local vector database (ChromaDB)
3. **Queries** your ingested content using a locally hosted Small Language Model (SLM) via a chat interface
4. **Cites** the specific URL or video title used to generate each answer

## Features

### Core Features

- **One-Click Ingestion**: Save articles and YouTube videos to your knowledge base with a single click
- **Local RAG Pipeline**: Background processing with semantic chunking and vector embeddings
- **Conversational Recall**: Chat interface to query your saved content
- **Source Attribution**: Clickable citations showing exactly where answers came from

### Browser Extension

- Chrome Side Panel integration
- Auto-detects articles and YouTube videos
- Keyboard shortcut (Ctrl+Shift+S) for quick saving
- Right-click context menu for links and text selections
- Real-time ingestion status feedback
- Badge showing your knowledge base size

### Backend

- FastAPI server with async support
- LangGraph orchestration for RAG workflows
- ChromaDB for persistent vector storage
- Ollama integration with Phi-3.5-mini model
- Automatic model pulling on first run

## Tech Stack

| Component | Technology |
|-----------|------------|
| **Frontend** | Vanilla JavaScript, HTML, CSS (Manifest V3) |
| **API Framework** | FastAPI (Python) |
| **Orchestration** | LangGraph |
| **Embeddings** | all-MiniLM-L6-v2 (HuggingFace) |
| **Vector Database** | ChromaDB |
| **LLM** | Phi-3.5-mini via Ollama |
| **Text Extraction** | Readability.js |

## Project Structure

```
cognitive-cache/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI application
│   │   ├── schemas.py        # Pydantic models
│   │   ├── dependencies.py   # Dependency injection
│   │   ├── chromadb_client.py  # ChromaDB integration
│   │   ├── ollama_client.py  # Ollama client
│   │   ├── rag_pipeline.py   # LangGraph RAG pipeline
│   │   ├── ingest_tasks.py   # Background task processing
│   │   ├── task_storage.py   # Task persistence
│   │   ├── youtube_transcript.py  # YouTube transcript fetcher
│   │   └── middleware/
│   │       └── timeout.py    # Request timeout middleware
│   ├── tests/
│   │   ├── test_ingest.py    # Ingestion tests
│   │   ├── test_query.py     # Query tests
│   │   ├── test_ollama.py    # Ollama/RAG tests
│   │   └── test_chromadb.py  # ChromaDB tests
│   └── requirements.txt
├── extension/
│   ├── manifest.json         # Extension manifest
│   ├── sidepanel.html        # Chat UI
│   ├── sidepanel.js          # UI logic
│   ├── sidepanel.css         # Styles
│   ├── service-worker.js     # Background script
│   └── content.js            # Content script
└── README.md
```

## Setup

### Prerequisites

1. **Python 3.10+**
2. **Ollama** - Install from [ollama.com](https://ollama.com)
3. **Chrome Browser** (for extension)

### Backend Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/cognitive-cache.git
   cd cognitive-cache/backend
   ```

2. **Create virtual environment**

   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # or
   source .venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Start the backend server**

   ```bash
   python -m app.main
   ```

   The server will start on `http://localhost:8000`

5. **Pull the Phi-3.5 model** (done automatically on first run)

   ```bash
   ollama pull phi3.5:latest
   ```

### Extension Setup

1. **Open Chrome Extensions**
   - Navigate to `chrome://extensions`
   - Enable "Developer mode"

2. **Load the extension**
   - Click "Load unpacked"
   - Select the `extension/` directory

3. **Start using**
   - Click the Cognitive Cache icon in your browser toolbar
   - Click "Start Backend" on first use
   - Navigate to an article or YouTube video
   - Click "Save Context" to ingest content
   - Use the chat interface to query your knowledge base

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/health` | GET | Health check with service status |
| `/api/v1/ingest` | POST | Ingest article or YouTube content |
| `/api/v1/tasks/{task_id}` | GET | Get task status |
| `/api/v1/sources` | GET | List all ingested sources |
| `/api/v1/query` | POST | Query the RAG system |

### Example: Ingest an Article

```bash
curl -X POST http://localhost:8000/api/v1/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "source_type": "article",
    "url": "https://example.com/article",
    "content": "Article text content..."
  }'
```

### Example: Query

```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What were the key points about RAG?"
  }'
```

## Testing

Run the test suite:

```bash
cd backend
pytest tests/ -v
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | `phi3.5:mini` | Model to use |
| `CHROMA_PERSIST_DIR` | `./chroma_db` | ChromaDB storage path |

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Chrome Ext.    │────▶│  FastAPI        │────▶│  ChromaDB       │
│  (Content)      │     │  (localhost:8000)│     │  (Vector Store) │
└─────────────────┘     └────────┬────────┘     └─────────────────┘
                                   │
                                   ▼
                           ┌─────────────────┐
                           │  Ollama         │
                           │  (Phi-3.5-mini) │
                           └─────────────────┘
```

## Privacy & Security

- **100% Local**: No data leaves your machine
- **No Cloud Dependencies**: All processing happens locally
- **No Telemetry**: Your data stays private
- **Open Source**: Audit the code yourself

## Limitations (MVP)

- Web articles and YouTube transcripts only
- No PDF or local file ingestion
- No cross-device syncing
- Chrome browser only

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please read the contributing guidelines before submitting a pull request.

## Acknowledgments

- [LangGraph](https://github.com/langchain-ai/langgraph) for orchestration
- [ChromaDB](https://github.com/chroma-core/chroma) for vector storage
- [Ollama](https://github.com/ollama/ollama) for local LLM serving
- [HuggingFace](https://huggingface.co) for embeddings
