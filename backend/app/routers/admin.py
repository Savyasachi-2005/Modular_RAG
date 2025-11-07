from fastapi import APIRouter


router = APIRouter()


@router.get("/health")
def health():
    return {"ok": True}


@router.get("/docs")
def list_docs():
    from ..core import db as core_db

    docs = core_db.get_all_documents()
    return {"documents": docs}


@router.get("/index_stats")
def index_stats():
    # expose lightweight vector store stats for debugging
    from ..core.di import get_vector_store

    vs = get_vector_store()
    return {"count": vs.count(), "sample_ids": vs.list_ids(20)}


@router.get("/trace/{trace_id}")
def trace(trace_id: str):
    from ..core import db as core_db

    t = core_db.get_trace(trace_id)
    if not t:
        return {"error": "trace not found"}
    return t


