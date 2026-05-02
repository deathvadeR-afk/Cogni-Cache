import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import torch

from chromadb import Client as ChromaClient
from chromadb.config import Settings as ChromaSettings
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.retrievers import ParentDocumentRetriever
from langchain.text_splitter import TextSplitter, RecursiveCharacterTextSplitter
from langchain_experimental.text_splitter import SemanticChunker
from langchain.storage import InMemoryStore
from langchain_core.documents import Document


class SemanticChunkerWrapper(TextSplitter):
    """Wrapper to make SemanticChunker compatible with TextSplitter interface."""
    
    def __init__(self, semantic_chunker: SemanticChunker):
        super().__init__()
        self._chunker = semantic_chunker
    
    def split_documents(self, documents):
        """Split documents using the underlying SemanticChunker."""
        return self._chunker.split_documents(documents)
    
    def split_text(self, text: str) -> List[str]:
        """Split text using the underlying SemanticChunker."""
        docs = self._chunker.split_documents([Document(page_content=text)])
        return [doc.page_content for doc in docs]

logger = logging.getLogger(__name__)


class ChromaDBClient:
    """ChromaDB client with persistent storage and RAG pipeline components."""

    def __init__(self, persist_directory: str = "./chroma_db"):
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)

        self.client = None
        self.vectorstore = None
        self.embeddings = None
        self.text_splitter = None
        self.semantic_chunker = None
        self.retriever = None
        self.docstore = None
        self.status = "not_initialized"

    def initialize(self):
        """Initialize ChromaDB with embeddings and RAG components."""
        try:
            # Initialize embeddings with GPU/CPU auto-detect
            self.embeddings = self._initialize_embeddings()

            # Initialize ChromaDB client with persistent storage
            self.client = ChromaClient(
                ChromaSettings(
                    persist_directory=str(self.persist_directory),
                    is_persistent=True
                )
            )

            # Initialize vectorstore
            self.vectorstore = Chroma(
                client=self.client,
                embedding_function=self.embeddings,
                persist_directory=str(self.persist_directory)
            )

            # Initialize SemanticChunker (for text chunking)
            self.semantic_chunker = SemanticChunker(
                embeddings=self.embeddings
            )

            # Initialize InMemoryStore for ParentDocumentRetriever
            self.docstore = InMemoryStore()

            # Initialize ParentDocumentRetriever with SemanticChunker wrapper as child_splitter
            # SemanticChunker creates semantically meaningful chunks for better retrieval
            self.semantic_chunker_wrapper = SemanticChunkerWrapper(self.semantic_chunker)
            self.retriever = ParentDocumentRetriever(
                vectorstore=self.vectorstore,
                docstore=self.docstore,
                child_splitter=self.semantic_chunker_wrapper,
                parent_splitter=None  # Use default
            )

            self.status = "healthy"
            logger.info(f"ChromaDB initialized successfully at {self.persist_directory}")

        except Exception as e:
            self.status = "error"
            logger.error(f"Failed to initialize ChromaDB: {e}")
            raise

    def _initialize_embeddings(self) -> HuggingFaceEmbeddings:
        """Initialize embeddings with GPU auto-detect and CPU fallback."""
        model_name = "all-MiniLM-L6-v2"

        # Check for GPU availability
        device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {device} for embeddings")

        embeddings = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={"device": device}
        )

        return embeddings

    def get_status(self) -> Dict[str, str]:
        """Return the status of ChromaDB."""
        return {"status": self.status}

    def add_documents(self, documents: List[Any], metadata: Optional[Dict[str, Any]] = None):
        """Add documents to ChromaDB with metadata filtering support."""
        if self.status != "healthy":
            raise RuntimeError("ChromaDB not initialized")

        # Convert dictionaries to Document objects if needed
        docs_to_add = []
        for doc in documents:
            if isinstance(doc, dict):
                # Convert dict to Document
                page_content = doc.get("text", doc.get("page_content", ""))
                meta = doc.get("metadata", {})
                if metadata:
                    meta.update(metadata)
                docs_to_add.append(Document(page_content=page_content, metadata=meta))
            else:
                # Assume it's already a Document object
                if metadata:
                    doc.metadata.update(metadata)
                docs_to_add.append(doc)

        # Use retriever to add documents
        self.retriever.add_documents(docs_to_add)
        logger.info(f"Added {len(docs_to_add)} documents to ChromaDB")

    def similarity_search(self, query: str, k: int = 4, filter: Optional[Dict[str, Any]] = None):
        """Perform similarity search with metadata filtering."""
        if self.status != "healthy":
            raise RuntimeError("ChromaDB not initialized")

        return self.vectorstore.similarity_search(query, k=k, filter=filter)

    def hyde_query(self, query: str) -> str:
        """Generate hypothetical document for HyDE query enhancement."""
        hypothetical_doc = f"Hypothetical document answering: {query}"
        return hypothetical_doc

    def enhanced_search(self, query: str, k: int = 4, filter: Optional[Dict[str, Any]] = None):
        """Perform HyDE-enhanced search."""
        # Generate hypothetical document
        hyde_doc = self.hyde_query(query)

        # Search with both original query and hypothetical document
        results_original = self.similarity_search(query, k=k, filter=filter)
        results_hyde = self.similarity_search(hyde_doc, k=k, filter=filter)

        # Combine and deduplicate results
        combined = results_original + results_hyde
        return list(set(combined))
