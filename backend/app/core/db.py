import os
import sqlite3
import json
import pickle
from typing import Optional

from ..core.config import settings


def _db_path() -> str:
    # settings.sqlite_url is expected like sqlite:///data/meta.db
    url = settings.sqlite_url
    if url.startswith("sqlite:///"):
        return url.replace("sqlite:///", "")
    return url


def get_connection() -> sqlite3.Connection:
    path = _db_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    conn = get_connection()
    cur = conn.cursor()

    # Documents
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS documents (
            doc_id TEXT PRIMARY KEY,
            filename TEXT,
            metadata TEXT
        )
        """
    )

    # Chunks
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS chunks (
            chunk_id TEXT PRIMARY KEY,
            doc_id TEXT,
            text TEXT,
            parent_span_id TEXT,
            metadata TEXT,
            FOREIGN KEY(doc_id) REFERENCES documents(doc_id) ON DELETE CASCADE
        )
        """
    )

    # Embeddings: store pickled vector to keep simple
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS embeddings (
            chunk_id TEXT PRIMARY KEY,
            vector BLOB,
            FOREIGN KEY(chunk_id) REFERENCES chunks(chunk_id) ON DELETE CASCADE
        )
        """
    )

    # Traces & feedback
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS traces (
            trace_id TEXT PRIMARY KEY,
            payload TEXT
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trace_id TEXT,
            thumb TEXT,
            comment TEXT
        )
        """
    )

    conn.commit()
    conn.close()


def insert_document(doc_id: str, filename: str, metadata: dict | None = None) -> None:
    metadata = metadata or {}
    conn = get_connection()
    conn.execute(
        "INSERT OR REPLACE INTO documents (doc_id, filename, metadata) VALUES (?, ?, ?)",
        (doc_id, filename, json.dumps(metadata)),
    )
    conn.commit()
    conn.close()


def insert_chunk(chunk_id: str, doc_id: str, text: str, parent_span_id: Optional[str] = None, metadata: dict | None = None) -> None:
    metadata = metadata or {}
    conn = get_connection()
    conn.execute(
        "INSERT OR REPLACE INTO chunks (chunk_id, doc_id, text, parent_span_id, metadata) VALUES (?, ?, ?, ?, ?)",
        (chunk_id, doc_id, text, parent_span_id, json.dumps(metadata)),
    )
    conn.commit()
    conn.close()


def upsert_embedding(chunk_id: str, vector: list[float]) -> None:
    conn = get_connection()
    blob = pickle.dumps(vector)
    conn.execute(
        "INSERT OR REPLACE INTO embeddings (chunk_id, vector) VALUES (?, ?)",
        (chunk_id, sqlite3.Binary(blob)),
    )
    conn.commit()
    conn.close()


def get_chunk(chunk_id: str) -> dict | None:
    conn = get_connection()
    cur = conn.execute("SELECT * FROM chunks WHERE chunk_id = ?", (chunk_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    return dict(row)


def get_all_chunks(limit: int | None = None) -> list[dict]:
    conn = get_connection()
    q = "SELECT * FROM chunks"
    if limit:
        q += f" LIMIT {int(limit)}"
    cur = conn.execute(q)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def get_embedding(chunk_id: str) -> list[float] | None:
    conn = get_connection()
    cur = conn.execute("SELECT vector FROM embeddings WHERE chunk_id = ?", (chunk_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    return pickle.loads(row[0])


def save_trace(trace_id: str, payload: dict) -> None:
    conn = get_connection()
    conn.execute(
        "INSERT OR REPLACE INTO traces (trace_id, payload) VALUES (?, ?)",
        (trace_id, json.dumps(payload)),
    )
    conn.commit()
    conn.close()


def get_trace(trace_id: str) -> dict | None:
    conn = get_connection()
    cur = conn.execute("SELECT payload FROM traces WHERE trace_id = ?", (trace_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    return json.loads(row[0])


def insert_feedback(trace_id: str, thumb: str | None, comment: str | None) -> None:
    conn = get_connection()
    conn.execute(
        "INSERT INTO feedback (trace_id, thumb, comment) VALUES (?, ?, ?)",
        (trace_id, thumb, comment),
    )
    conn.commit()
    conn.close()


def get_all_documents() -> list[dict]:
    conn = get_connection()
    cur = conn.execute("SELECT * FROM documents")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    # parse metadata JSON
    for r in rows:
        if r.get("metadata"):
            try:
                r["metadata"] = json.loads(r["metadata"]) if isinstance(r["metadata"], str) else r["metadata"]
            except Exception:
                r["metadata"] = {}
    return rows


def get_document(doc_id: str) -> dict | None:
    conn = get_connection()
    cur = conn.execute("SELECT * FROM documents WHERE doc_id = ?", (doc_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    r = dict(row)
    try:
        r["metadata"] = json.loads(r["metadata"]) if isinstance(r["metadata"], str) else r["metadata"]
    except Exception:
        r["metadata"] = {}
    return r
