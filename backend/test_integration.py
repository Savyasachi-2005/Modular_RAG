import os
import uuid
import json
from app.core import db as core_db
from app.ingestion.worker import process_doc_sync
from app.core.di import get_vector_store

# create a test doc id
DOC_ID = "integration-test-" + str(uuid.uuid4())
raw_dir = os.path.join("data", "uploads", DOC_ID, "raw")
os.makedirs(raw_dir, exist_ok=True)

# write a sample raw file
with open(os.path.join(raw_dir, "sample.txt"), "w", encoding="utf-8") as f:
    f.write("This is a small test document about testing the ingestion pipeline. It contains several sentences to create multiple chunks. " * 30)

# ensure DB exists
core_db.init_db()

print("Processing doc:", DOC_ID)
status = process_doc_sync(DOC_ID)
print("Status:", json.dumps(status, indent=2))

# inspect DB counts
chunks = core_db.get_all_chunks(limit=20)
print("Sample chunks (up to 20):", len(chunks))
for c in chunks[:3]:
    print("-", c.get("chunk_id"), "(len=", len(c.get("text", "")), ")")

# vector store count
vs = get_vector_store()
print("VectorStore count:", vs.count())
print("VectorStore sample ids:", vs.list_ids(10))

# Clean up note
print("Done. If vectors==0, ensure GEMINI_API_KEY is set in .env and server restarted, or inspect data/uploads/<doc_id>/status.json")
