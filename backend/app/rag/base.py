import uuid
from typing import List, Dict, Any
from ..core import db as core_db
from ..core.di import get_vector_store, get_generator, get_encoder
from ..domain.models import RetrievalResult, GenerationResult
from ..rag.context_assembly import assemble_context, mmr_select
from ..core.config import settings


class RAG:
    def __init__(self):
        self.vs = get_vector_store()
        self.gen = get_generator()

    def retrieve(self, query: str, top_k: int = 8) -> List[Dict[str, Any]]:
        # Embed the query using the same encoder used for chunks so retrieval is consistent.
        encoder = get_encoder()
        try:
            q_vectors = encoder.encode_batch([query], batch_size=1)
            qv = q_vectors[0]
        except Exception:
            # Fallback to a very small deterministic vector if encoding fails
            qv = [0.0] * 768

        hits = self.vs.search(qv, top_k=top_k)
        results = []
        for chunk_id, score in hits:
            chunk = core_db.get_chunk(chunk_id)
            if not chunk:
                continue
            results.append({"chunk_id": chunk_id, "doc_id": chunk.get("doc_id"), "score": score, "text": chunk.get("text")})
        return results

    def generate(self, query: str, plugin_config: dict | None = None, preview_only: bool = False) -> GenerationResult:
        # Determine top_k (respect plugin config, otherwise use settings)
        top_k = plugin_config.get("top_k") if plugin_config and "top_k" in plugin_config else settings.retrieval_top_k

        # Retrieve and select using MMR-like selection
        retrieved = self.retrieve(query, top_k=top_k)
        selected = mmr_select(retrieved, k=top_k, lambda_mul=settings.mmr_lambda)

        # Assemble context using configured budget
        context = assemble_context(selected, budget_tokens=settings.context_budget_tokens)
        prompt = f"Context:\n{context}\n\nQuestion: {query}\nAnswer:"

        # If preview_only, don't call the generator; return a preview of the prompt
        if preview_only:
            answer = "[preview] " + (prompt[:1000] if len(prompt) > 1000 else prompt)
        else:
            # call generator (stub or real client depending on DI)
            answer = self.gen.generate(prompt)

        # Compute a bounded confidence score. Vector similarities are cosine in [-1,1].
        scores = [r.get("score", 0.0) for r in selected]
        if scores:
            avg = float(sum(scores) / len(scores))
            # map from [-1,1] to [0,1]
            confidence = max(0.0, min(1.0, (avg + 1.0) / 2.0))
        else:
            confidence = 0.0

        # persist trace (include a preview flag)
        trace_id = str(uuid.uuid4())
        trace_payload = {
            "query": query,
            "retrieved": selected,
            "prompt": prompt,
            "answer": answer,
            "confidence": confidence,
            "preview": bool(preview_only),
        }
        core_db.save_trace(trace_id, trace_payload)

        # Build pydantic sources list
        sources = [RetrievalResult(chunk_id=r["chunk_id"], doc_id=r.get("doc_id"), score=r.get("score", 0.0)) for r in selected]
        gen = GenerationResult(answer=answer, sources=sources, confidence=confidence, trace_id=trace_id)
        return gen
