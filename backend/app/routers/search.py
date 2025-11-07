from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..rag.base import RAG
from ..core import db as core_db


router = APIRouter()


class QueryRequest(BaseModel):
    query: str
    plugin_config: dict | None = None
    preview_only: bool | None = None


@router.post("/query")
async def query_rag(req: QueryRequest):
    if not req.query:
        raise HTTPException(status_code=400, detail="query is required")
    rag = RAG()
    gen = rag.generate(req.query, plugin_config=req.plugin_config or {}, preview_only=bool(req.preview_only))
    # conversion to plain dict (pydantic models are JSON serializable)
    return gen.dict()


class ApproveRequest(BaseModel):
    trace_id: str
    chunk_ids: list[str]


@router.post("/approve")
async def approve(req: ApproveRequest):
    # When user approves chunk_ids, run final generation using approved chunks
    from ..core import db as core_db
    from ..core.di import get_generator
    from ..rag.context_assembly import assemble_context

    # fetch chunks
    texts = []
    for cid in req.chunk_ids:
        c = core_db.get_chunk(cid)
        if not c:
            continue
        texts.append(c.get("text", ""))

    if not texts:
        return {"ok": False, "error": "no chunks found for provided chunk_ids"}

    context = "\n\n---\n\n".join(texts)
    prompt = f"Context:\n{context}\n\nQuestion: (from trace {req.trace_id})\nAnswer:"
    gen_client = get_generator()
    answer = gen_client.generate(prompt)

    # save a new trace for the approved generation
    new_trace_id = req.trace_id + "-approved"
    core_db.save_trace(new_trace_id, {"from_trace": req.trace_id, "chunk_ids": req.chunk_ids, "prompt": prompt, "answer": answer})

    return {"ok": True, "trace_id": new_trace_id, "answer": answer}


class RegenerateRequest(BaseModel):
    trace_id: str
    format: str | None = None
    tone: str | None = None
    length: str | None = None


@router.post("/regenerate")
async def regenerate(req: RegenerateRequest):
    trace = core_db.get_trace(req.trace_id)
    if not trace:
        raise HTTPException(status_code=404, detail="trace not found")
    # For MVP, regenerate by reusing the saved prompt if present
    prompt = trace.get("prompt")
    if not prompt:
        raise HTTPException(status_code=400, detail="no prompt available for trace")
    from ..core.di import get_generator

    gen_client = get_generator()
    answer = gen_client.generate(prompt)
    # save new trace
    new_trace_id = req.trace_id + "-regen"
    core_db.save_trace(new_trace_id, {"prompt": prompt, "answer": answer})
    return {"answer": answer, "trace_id": new_trace_id}


@router.get("/trace/{trace_id}")
async def get_trace(trace_id: str):
    t = core_db.get_trace(trace_id)
    if not t:
        raise HTTPException(status_code=404, detail="trace not found")
    return t


