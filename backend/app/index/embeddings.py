from typing import List
import numpy as np


class EmbeddingEncoder:
    def __init__(self, model_name: str, dim: int = 768):
        self.model_name = model_name
        self.dim = dim

    def _deterministic_vector(self, text: str) -> np.ndarray:
        # Create a deterministic pseudo-random vector for the text
        h = hash(text) & 0xFFFFFFFF
        rng = np.random.RandomState(h)
        v = rng.normal(size=(self.dim,)).astype(np.float32)
        # L2 normalize
        norm = np.linalg.norm(v)
        if norm > 0:
            v = v / norm
        return v

    def encode(self, texts: List[str]) -> List[List[float]]:
        vectors = [self._deterministic_vector(t).tolist() for t in texts]
        return vectors

    def encode_batch(self, texts: List[str], batch_size: int = 64) -> List[List[float]]:
        out = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            out.extend(self.encode(batch))
        return out
