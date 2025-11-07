from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..core import db as core_db


router = APIRouter()


class FeedbackRequest(BaseModel):
    trace_id: str
    thumb: str | None = None
    comment: str | None = None


@router.post("/feedback")
async def post_feedback(req: FeedbackRequest):
    # validate trace exists
    trace = core_db.get_trace(req.trace_id)
    if not trace:
        raise HTTPException(status_code=404, detail="trace not found")
    core_db.insert_feedback(req.trace_id, req.thumb, req.comment)
    return {"ok": True}
