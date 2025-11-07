import uuid
from typing import List, Tuple, Optional


def _words(text: str) -> List[str]:
    return text.split()


def _join(words: List[str]) -> str:
    return " ".join(words)


def chunk_text(text: str, chunk_size_words: int = 600, overlap_words: int = 150, parent_span_id: Optional[str] = None) -> List[Tuple[str, str, Optional[str]]]:
    """
    Simple word-based chunker.

    Returns list of tuples: (chunk_id, chunk_text, parent_span_id)
    """
    words = _words(text)
    if not words:
        return []
    chunks = []
    i = 0
    while i < len(words):
        start = max(0, i)
        end = min(len(words), i + chunk_size_words)
        piece = _join(words[start:end])
        chunk_id = str(uuid.uuid4())
        chunks.append((chunk_id, piece, parent_span_id))
        if end == len(words):
            break
        i = end - overlap_words
    return chunks
