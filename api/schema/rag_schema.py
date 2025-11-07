from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class DocumentPayload(BaseModel):
    """Schema for a document to be indexed."""
    content: str = Field(..., description="The main text content of the document.")
    title: Optional[str] = Field(None, description="The title of the document.")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata for the document.")

class QueryRequest(BaseModel):
    """Schema for a user's query."""
    query: str = Field(..., description="The user's question.")
    top_k: int = Field(5, gt=0, le=10, description="The number of source documents to return.")

class SourceDocument(BaseModel):
    """Schema representing a source document chunk used for the answer."""
    id: str
    content: str
    title: Optional[str] = None
    score: Optional[float] = None

class QueryResponse(BaseModel):
    """Schema for the final RAG response."""
    answer: str = Field(..., description="The generated answer to the query.")
    sources: List[SourceDocument] = Field(..., description="A list of source documents that informed the answer.")
