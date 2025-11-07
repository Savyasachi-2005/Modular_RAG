from pydantic import BaseModel
from typing import List, Optional


class Document(BaseModel):
    doc_id: str
    filename: str
    metadata: dict


class Chunk(BaseModel):
    chunk_id: str
    doc_id: str
    text: str
    parent_span_id: Optional[str] = None
    metadata: dict = {}


class Query(BaseModel):
    text: str


class RetrievalResult(BaseModel):
    chunk_id: str
    doc_id: str
    score: float


class GenerationResult(BaseModel):
    answer: str
    sources: List[RetrievalResult]
    confidence: float
    trace_id: str


