import logging
from typing import List, Dict, Any, TypedDict, AsyncGenerator
from langchain_core.documents import Document
from langgraph.graph import StateGraph, END

logger = logging.getLogger(__name__)


class RAGState(TypedDict):
    """State for the RAG pipeline."""
    query: str
    context: List[Document]
    response: str
    filter: Dict[str, Any]
    history: List[Dict[str, str]]
    citations: List[Dict[str, str]]


def create_rag_graph(chromadb_client, ollama_client):
    """
    Create a LangGraph RAG pipeline.

    Args:
        chromadb_client: Initialized ChromaDB client
        ollama_client: Initialized Ollama client

    Returns:
        Compiled LangGraph state graph
    """

    # Define the retrieval node
    def retrieve(state: RAGState) -> RAGState:
        """Retrieve relevant documents from ChromaDB."""
        query = state["query"]
        filter = state.get("filter")

        logger.info(f"Retrieving documents for query: {query}")
        try:
            docs = chromadb_client.similarity_search(
                query=query,
                k=4,
                filter=filter
            )
            state["context"] = docs
            logger.info(f"Retrieved {len(docs)} documents")
        except Exception as e:
            logger.error(f"Error retrieving documents: {e}")
            state["context"] = []

        return state

    # Define the generation node
    def generate(state: RAGState) -> RAGState:
        """Generate response using Ollama with retrieved context."""
        query = state["query"]
        context_docs = state.get("context", [])
        history = state.get("history", [])

        # Build context string from retrieved documents
        context_text = "\n\n".join([
            f"Document {i+1}:\n{doc.page_content}"
            for i, doc in enumerate(context_docs)
        ])

        # Build citations from context documents
        citations = []
        for doc in context_docs:
            metadata = doc.metadata
            url = metadata.get("url", "")
            title = metadata.get("title", "")
            if url:
                citations.append({"url": url, "title": title})

        # Build prompt with context
        system_prompt = """You are a helpful assistant that answers questions based on the provided context.
If the context doesn't contain relevant information, say so honestly.
Always cite the specific documents you use in your answer using inline citations like [1], [2], etc.
The citations should reference the document numbers from the context."""

        # Build conversation history
        history_text = ""
        if history:
            for msg in history:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                history_text += f"{role.capitalize()}: {content}\n"

        user_prompt = f"""Context:
{context_text}

Conversation History:
{history_text}

Question: {query}

Answer:"""

        logger.info("Generating response with Ollama")
        try:
            response = ollama_client.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.7
            )
            state["response"] = response
            state["citations"] = citations
            logger.info("Response generated successfully")
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            state["response"] = f"Error generating response: {str(e)}"
            state["citations"] = []

        return state

    # Create the graph
    workflow = StateGraph(RAGState)

    # Add nodes
    workflow.add_node("retrieve", retrieve)
    workflow.add_node("generate", generate)

    # Add edges
    workflow.set_entry_point("retrieve")
    workflow.add_edge("retrieve", "generate")
    workflow.add_edge("generate", END)

    # Compile the graph
    return workflow.compile()


class RAGPipeline:
    """RAG pipeline using LangGraph orchestration."""

    def __init__(self, chromadb_client, ollama_client):
        self.chromadb_client = chromadb_client
        self.ollama_client = ollama_client
        self.graph = create_rag_graph(chromadb_client, ollama_client)

    def query(self, query: str, filter: Dict[str, Any] = None, history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Run a query through the RAG pipeline.

        Args:
            query: The user query
            filter: Optional metadata filter for ChromaDB
            history: Optional conversation history

        Returns:
            Dictionary with response and citations
        """
        if self.chromadb_client.status != "healthy":
            raise RuntimeError("ChromaDB client not healthy")
        if self.ollama_client.status != "healthy":
            raise RuntimeError("Ollama client not healthy")

        initial_state: RAGState = {
            "query": query,
            "context": [],
            "response": "",
            "filter": filter or {},
            "history": history or [],
            "citations": []
        }

        logger.info(f"Running RAG pipeline for query: {query}")
        result = self.graph.invoke(initial_state)

        return {
            "response": result["response"],
            "citations": result.get("citations", [])
        }

    async def query_stream(self, query: str, filter: Dict[str, Any] = None, history: List[Dict[str, str]] = None) -> AsyncGenerator[str, None]:
        """
        Run a query through the RAG pipeline with streaming response.

        Args:
            query: The user query
            filter: Optional metadata filter for ChromaDB
            history: Optional conversation history

        Yields:
            Response chunks as they are generated
        """
        if self.chromadb_client.status != "healthy":
            raise RuntimeError("ChromaDB client not healthy")
        if self.ollama_client.status != "healthy":
            raise RuntimeError("Ollama client not healthy")

        # Run the pipeline synchronously but yield response in chunks
        result = self.query(query, filter, history)
        response = result["response"]
        
        # Yield response in chunks for streaming effect
        words = response.split()
        for i, word in enumerate(words):
            yield word + (" " if i < len(words) - 1 else "")

    def query_with_hyde(self, query: str, filter: Dict[str, Any] = None) -> str:
        """
        Run a query through the RAG pipeline with HyDE enhancement.

        Args:
            query: The user query
            filter: Optional metadata filter for ChromaDB

        Returns:
            Generated response using HyDE-enhanced search
        """
        if self.chromadb_client.status != "healthy":
            raise RuntimeError("ChromaDB client not healthy")

        # Get HyDE-enhanced search results
        hyde_results = self.chromadb_client.enhanced_search(query, k=4, filter=filter)

        # Build context from HyDE results
        context_text = "\n\n".join([
            f"Document {i+1}:\n{doc.page_content}"
            for i, doc in enumerate(hyde_results)
        ])

        system_prompt = """You are a helpful assistant that answers questions based on the provided context.
If the context doesn't contain relevant information, say so honestly.
Always cite the specific documents you use in your answer."""

        user_prompt = f"""Context:
{context_text}

Question: {query}

Answer:"""

        logger.info(f"Generating HyDE-enhanced response for query: {query}")
        response = self.ollama_client.generate(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.7
        )

        return response
