import logging
from typing import Optional
from langchain_core.documents import Document
from app.task_storage import TaskStorage
from app.youtube_transcript import fetch_youtube_transcript
from app.chromadb_client import ChromaDBClient

logger = logging.getLogger(__name__)


def process_ingest_task(
    task_id: str,
    source_type: str,
    url: str,
    content: Optional[str],
    task_storage: TaskStorage,
    chromadb_client: ChromaDBClient,
) -> None:
    """
    Process an ingestion task in the background.

    Args:
        task_id: Task ID
        source_type: Type of source (article/youtube)
        url: Source URL
        content: Content for articles (None for YouTube)
        task_storage: Task storage instance
        chromadb_client: ChromaDB client instance
    """
    try:
        # Update status to processing
        task_storage.update_task(task_id, status="processing")

        # Get the text content
        if source_type == "youtube":
            text_content = fetch_youtube_transcript(url)
        else:
            if not content:
                raise ValueError("Content is required for article source type")
            text_content = content

        # Chunk and store in ChromaDB
        logger.info(f"Processing {len(text_content)} characters for task {task_id}")

        # Use the ChromaDB client to add documents
        # The client handles chunking via ParentDocumentRetriever
        doc = Document(
            page_content=text_content,
            metadata={
                "source_type": source_type,
                "url": url,
            }
        )
        chromadb_client.add_documents([doc])

        # Update task as completed
        task_storage.update_task(
            task_id,
            status="completed",
            result={
                "chunks_added": 1,
                "source_type": source_type,
                "url": url,
            }
        )
        logger.info(f"Task {task_id} completed successfully")

    except Exception as e:
        logger.error(f"Task {task_id} failed: {e}")
        task_storage.update_task(
            task_id,
            status="failed",
            error=str(e)
        )