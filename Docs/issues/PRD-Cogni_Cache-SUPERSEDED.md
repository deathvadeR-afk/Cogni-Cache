> ⚠️ **SUPERSEDED** — This is the original high-level PRD sketch. It has been replaced by the Grill Me-refined document at `/issues/PRD-Cognitive-Cache.md`. Do not treat this file as current specification. It is retained for historical reference only.

---

Here is a high-level Product Requirements Document (PRD) for the MVP of your local, personalized "Second Brain" AI.

To keep this completely free to build and run, the architecture relies heavily on open-source, locally hosted tools, orchestrated through a Python-based backend.

---

# MVP Product Requirements Document (PRD): "Cognitive Cache"

## 1. Product Vision & Objective

**Vision:** To provide users with a hyper-personalized, fully private AI companion that acts as an extension of their memory by silently ingesting, cataloging, and recalling their web consumption.
**MVP Objective:** Build an end-to-end pipeline that captures text from web articles and YouTube transcripts, stores them in a local vector database, and allows the user to query this knowledge base using a locally hosted Small Language Model (SLM) via a chat interface.

## 2. Scope & Constraints

| Category | In Scope (MVP) | Out of Scope (MVP) |
| :--- | :--- | :--- |
| **Data Sources** | Text-heavy web articles/blogs, YouTube Auto-Transcripts. | PDFs, local desktop files, real-time audio/video processing, emails. |
| **User Interface** | A simple browser extension to trigger ingestion and open a chat side-panel. | Standalone desktop application, mobile app. |
| **Infrastructure** | 100% local execution (CPU/GPU dependent). Zero cloud API costs. | Cloud backups, cross-device syncing. |

## 3. Core Features (MVP)

* **One-Click Ingestion:** A browser extension button that scrapes the currently active tab (extracting article text or YouTube transcripts) and sends it to the local backend.
* **Local RAG Pipeline:** A background service that chunks the scraped text, generates embeddings, and stores them in a vector database.
* **Conversational Recall Interface:** A simple chat UI (accessible via the browser extension) where the user can query their consumed content.
* **Source Attribution:** The AI must cite the specific URL or video title it used to generate its answer.

## 4. Tech Stack (100% Free & Open-Source)

This stack leverages standard open-source Python libraries and local inference engines to guarantee zero operational costs.

### A. The Browser Extension (Frontend)

* **Languages:** Vanilla JavaScript, HTML, CSS.
* **Capabilities:** Uses standard Chrome/Firefox extension APIs to read DOM elements. Uses libraries like `Readability.js` to strip HTML down to pure text.

### B. The Brain & Backend Service (Python)

* **API Framework:** **FastAPI**. A lightweight, asynchronous web server running locally on `localhost` to receive data from the extension.
* **Orchestration:** **LangChain** or **LangGraph**. Ideal for managing the RAG workflow, routing user queries, and structuring the agentic logic between the database and the LLM.
* **Embedding Model:** **`all-MiniLM-L6-v2`** via HuggingFace (runs locally, extremely fast, and completely free).
* **Vector Database:** **ChromaDB**. Runs entirely locally as a Python library, requiring no external server setup.

### C. Local Inference Engine

* **Execution Provider:** **Ollama**. Free, open-source, and manages local model weights with excellent hardware optimization.
* **The SLM:** **Llama 3 (8B - 4-bit quantized)** or **Phi-3 Mini**. Hosted inside Ollama.

## 5. User Flow

1. **Consume:** User watches a video on multi-agent AI frameworks.
2. **Ingest:** User clicks the "Cognitive Cache" extension icon and hits "Save Context."
3. **Process (Invisible):** The extension grabs the YouTube transcript and POSTs it to the local FastAPI server. The Python backend chunks the text, creates embeddings using `MiniLM`, and saves it to ChromaDB.
4. **Query:** A week later, the user opens the extension chat and asks, "What were the core concepts of that agentic framework video I watched?"
5. **Retrieve & Generate:** LangGraph intercepts the query, retrieves the relevant transcript chunks from ChromaDB, and passes them to the local Llama 3 model in Ollama to generate the final, sourced answer.

---

This PRD sets a strict, achievable boundary for an MVP. Since the backend heavily relies on Python and standard RAG workflows, building out the FastAPI and vector database integration is usually the quickest win.
