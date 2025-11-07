from __future__ import annotations
import os
import numpy as np
from typing import List, Tuple

from ..core.config import settings


class VectorStore:
    def __init__(self, path: str | None = None, dim: int = 768):
        self.dim = dim
        self.path = path or settings.faiss_index_path
        # internal mapping from id -> vector
        self._ids: List[str] = []
        self._vectors: np.ndarray = np.zeros((0, dim), dtype=np.float32)
        self._load()

    def _load(self) -> None:
        if os.path.exists(self.path):
            try:
                data = np.load(self.path, allow_pickle=True)
                self._ids = data["ids"].tolist()
                self._vectors = data["vectors"]
            except Exception:
                # ignore and start empty
                self._ids = []
                self._vectors = np.zeros((0, self.dim), dtype=np.float32)

    def _save(self) -> None:
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        np.savez(self.path, ids=np.array(self._ids, dtype=object), vectors=self._vectors)

    def add(self, id: str, vector: List[float]) -> None:
        v = np.asarray(vector, dtype=np.float32)
        if v.ndim != 1 or v.shape[0] != self.dim:
            raise ValueError("vector has wrong shape")
        # normalize
        norm = np.linalg.norm(v)
        if norm > 0:
            v = v / norm
        if id in self._ids:
            idx = self._ids.index(id)
            self._vectors[idx] = v
        else:
            self._ids.append(id)
            if self._vectors.shape[0] == 0:
                self._vectors = v.reshape(1, -1)
            else:
                self._vectors = np.vstack([self._vectors, v.reshape(1, -1)])
        self._save()

    def count(self) -> int:
        return len(self._ids)

    def list_ids(self, limit: int = 20) -> List[str]:
        return self._ids[:limit]

    def search(self, vector: List[float], top_k: int = 8) -> List[Tuple[str, float]]:
        if len(self._ids) == 0:
            return []
        q = np.asarray(vector, dtype=np.float32)
        norm = np.linalg.norm(q)
        if norm > 0:
            q = q / norm
        sims = (self._vectors @ q).astype(np.float32)
        # argsort descending
        idxs = np.argsort(-sims)[:top_k]
        results = [(self._ids[int(i)], float(sims[int(i)])) for i in idxs]
        return results
