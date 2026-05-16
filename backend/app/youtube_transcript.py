import logging
import re
from typing import Optional

logger = logging.getLogger(__name__)

try:
    from youtube_transcript_api import YouTubeTranscriptApi
    YOUTUBE_TRANSCRIPT_AVAILABLE = True
except ImportError:
    YOUTUBE_TRANSCRIPT_AVAILABLE = False
    logger.warning("youtube_transcript_api not installed")


def extract_video_id(url_or_id: str) -> Optional[str]:
    """
    Extract YouTube video ID from URL or return the ID if already provided.

    Args:
        url_or_id: YouTube URL or video ID

    Returns:
        Video ID or None if invalid
    """
    # If it's already a video ID (11 characters, no special chars)
    if re.match(r'^[a-zA-Z0-9_-]{11}$', url_or_id):
        return url_or_id

    # Extract from various URL formats
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
        r'youtube\.com\/watch\?.*v=([^&\n?#]+)',
    ]

    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)

    return None


def fetch_youtube_transcript(url_or_id: str) -> str:
    """
    Fetch transcript from YouTube video.

    Args:
        url_or_id: YouTube URL or video ID

    Returns:
        Transcript text

    Raises:
        ValueError: If transcript cannot be fetched
    """
    if not YOUTUBE_TRANSCRIPT_AVAILABLE:
        raise ValueError("youtube_transcript_api not installed")

    video_id = extract_video_id(url_or_id)
    if not video_id:
        raise ValueError(f"Invalid YouTube URL or ID: {url_or_id}")

    try:
        logger.info(f"Fetching transcript for video: {video_id}")
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)

        # Combine all text segments
        transcript_text = " ".join([
            segment["text"] for segment in transcript_list
        ])

        logger.info(f"Successfully fetched transcript with {len(transcript_text)} characters")
        return transcript_text

    except Exception as e:
        logger.error(f"Failed to fetch transcript for {video_id}: {e}")
        raise ValueError(f"Could not fetch transcript: {str(e)}")