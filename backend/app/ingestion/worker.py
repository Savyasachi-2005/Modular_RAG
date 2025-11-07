import json
import os
import queue
import threading
import time
from typing import List
import traceback

from ..core.config import settings
from ..core import db as core_db
from ..core.di import get_encoder, get_vector_store
from .chunker import chunk_text

import logging

log = logging.getLogger(__name__)


STATUS_FILENAME = "status.json"


def _status_path(doc_id: str) -> str:
    return os.path.join(settings.uploads_dir, doc_id, STATUS_FILENAME)


def write_status(doc_id: str, status: str, counts: dict | None = None, errors: list | None = None) -> None:
    path = _status_path(doc_id)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    data = {"doc_id": doc_id, "status": status, "counts": counts or {}}
    if errors:
        # keep only last 10 errors to avoid huge blobs
        data["errors"] = errors[-10:]
    with open(path, "w") as f:
        json.dump(data, f)


def read_status(doc_id: str) -> dict:
    path = _status_path(doc_id)
    if not os.path.exists(path):
        return {"doc_id": doc_id, "status": "unknown", "counts": {}}
    with open(path, "r") as f:
        return json.load(f)


class IngestionWorker:
    def __init__(self) -> None:
        self._q: queue.Queue[str] = queue.Queue()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._started = False

    def start(self) -> None:
        if not self._started:
            # initialize DB
            try:
                core_db.init_db()
            except Exception:
                log.exception("failed to init db")
            self._thread.start()
            self._started = True

    def enqueue(self, doc_ids: List[str]) -> int:
        for d in doc_ids:
            self._q.put(d)
        return len(doc_ids)

    def _run(self) -> None:
        while True:
            doc_id = self._q.get()
            try:
                log.info("ingestion: picked doc_id=%s for processing", doc_id)
                self._process_doc(doc_id)
            except Exception:
                # mark failed and capture traceback
                tb = traceback.format_exc()
                log.exception("ingestion: fatal error processing doc %s", doc_id)
                write_status(doc_id, "failed", counts={"files": 0, "chunks": 0}, errors=[tb])
            finally:
                self._q.task_done()

    def _process_doc(self, doc_id: str) -> None:
        # mark processing
        errors: list = []
        write_status(doc_id, "processing", {"files": 0, "chunks": 0}, errors=None)
        raw_dir = os.path.join(settings.uploads_dir, doc_id, "raw")
        file_count = 0
        chunk_count = 0
        encoder = get_encoder()
        vs = get_vector_store()
        try:
            before_vectors = vs.count()
        except Exception:
            before_vectors = 0

        log.info("ingestion: vector count before processing doc %s = %s", doc_id, before_vectors)

        if not os.path.isdir(raw_dir):
            msg = f"raw dir not found: {raw_dir}"
            log.error(msg)
            errors.append(msg)
            write_status(doc_id, "failed", {"files": 0, "chunks": 0}, errors=errors)
            return

        # iterate files, parse text, chunk, embed, persist
        for name in os.listdir(raw_dir):
            p = os.path.join(raw_dir, name)
            if not os.path.isfile(p):
                continue
            file_count += 1
            log.info("ingestion: processing file %s for doc %s", name, doc_id)
            try:
                with open(p, "r", encoding="utf-8", errors="replace") as f:
                    text = f.read()
            except Exception:
                # fallback to binary read
                try:
                    with open(p, "rb") as f:
                        text = f.read().decode("utf-8", errors="replace")
                except Exception as e:
                    tb = traceback.format_exc()
                    log.exception("ingestion: failed to read file %s for doc %s", name, doc_id)
                    errors.append(tb)
                    continue

            # insert document record (minimal metadata)
            try:
                core_db.insert_document(doc_id, name, {"source_filename": name})
            except Exception:
                log.exception("failed to insert document record")

            chunks = chunk_text(text)
            chunk_count += len(chunks)
            log.info("ingestion: created %d chunks for file %s (doc=%s)", len(chunks), name, doc_id)

            # persist chunks and compute embeddings in batches
            texts = []
            chunk_ids = []
            for chunk_id, chunk_text_content, parent in chunks:
                try:
                    core_db.insert_chunk(chunk_id, doc_id, chunk_text_content, parent_span_id=parent, metadata={})
                except Exception:
                    tb = traceback.format_exc()
                    log.exception("failed to insert chunk %s", chunk_id)
                    errors.append(tb)
                texts.append(chunk_text_content)
                chunk_ids.append(chunk_id)

            # compute embeddings
            if texts:
                vectors = encoder.encode_batch(texts, batch_size=settings.embedding_batch_size)
                for cid, vec in zip(chunk_ids, vectors):
                    try:
                        core_db.upsert_embedding(cid, vec)
                        vs.add(cid, vec)
                        log.debug("ingestion: persisted embedding for chunk %s", cid)
                    except Exception:
                        tb = traceback.format_exc()
                        log.exception("failed to upsert embedding for %s", cid)
                        errors.append(tb)

            # slight delay to avoid busy loop
            time.sleep(0.01)

        # mark completed
        try:
            after_vectors = vs.count()
        except Exception:
            after_vectors = 0
        counts = {"files": file_count, "chunks": chunk_count, "vectors_before": before_vectors, "vectors_after": after_vectors, "vectors_added": max(0, after_vectors - before_vectors)}
        status = "completed" if not errors else "completed_with_errors"
        write_status(doc_id, status, counts, errors=errors if errors else None)
        log.info("ingestion: vector count after processing doc %s = %s (added=%s); errors=%d", doc_id, after_vectors, max(0, after_vectors - before_vectors), len(errors))


worker = IngestionWorker()


def process_doc_sync(doc_id: str) -> dict:
    """Process a document synchronously (for debugging).

    Returns the status dict written to status.json after processing.
    """
    try:
        # ensure DB initialized
        core_db.init_db()
    except Exception:
        log.exception("failed to init db (sync)")
    try:
        worker._process_doc(doc_id)
    except Exception:
        tb = traceback.format_exc()
        write_status(doc_id, "failed", {"files": 0, "chunks": 0}, errors=[tb])
    return read_status(doc_id)


