from typing import List

from fastapi import APIRouter, UploadFile, File, Body
from pydantic import BaseModel

from ..core.config import settings
from ..ingestion.worker import worker, write_status, read_status, process_doc_sync

import os
import uuid


router = APIRouter()


@router.post("/upload")
async def upload(files: List[UploadFile] = File(...)):
    doc_ids = []
    for f in files:
        doc_id = str(uuid.uuid4())
        target_dir = os.path.join(settings.uploads_dir, doc_id, "raw")
        os.makedirs(target_dir, exist_ok=True)
        target_path = os.path.join(target_dir, f.filename)
        with open(target_path, "wb") as out:
            out.write(await f.read())
        doc_ids.append(doc_id)
        write_status(doc_id, "uploaded", {"files": 1, "chunks": 0})
    return {"doc_ids": doc_ids}


class IndexRequest(BaseModel):
    doc_ids: List[str] | None = None


@router.post("/index")
async def start_indexing(req: IndexRequest | None = Body(default=None)):
    try:
        doc_ids: List[str] | None = None
        if req and req.doc_ids:
            doc_ids = req.doc_ids
        # If no ids provided, try to infer from uploads dir
        if not doc_ids:
            if os.path.isdir(settings.uploads_dir):
                doc_ids = [
                    d
                    for d in os.listdir(settings.uploads_dir)
                    if os.path.isdir(os.path.join(settings.uploads_dir, d))
                ]
            else:
                doc_ids = []
        enq = worker.enqueue(doc_ids)
        return {"status": "started", "queued": enq, "doc_ids": doc_ids}
    except Exception as e:
        return {"status": "error", "message": f"failed to start indexing: {e}"}


@router.get("/status")
def status(doc_id: str):
    return read_status(doc_id)


@router.post("/force_process/{doc_id}")
def force_process(doc_id: str):
    """Force processing of a doc_id synchronously (debug only)."""
    try:
        res = process_doc_sync(doc_id)
        return {"ok": True, "status": res}
    except Exception as e:
        return {"ok": False, "error": str(e)}


