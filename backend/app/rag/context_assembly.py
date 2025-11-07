from typing import List, Dict


def assemble_context(chunks: List[Dict], budget_tokens: int = 6000) -> str:
    """
    Very small context assembler: concatenates chunk texts until budget (approx words) is reached.
    Each chunk dict is expected to have at least 'chunk_id' and 'text'.
    """
    out = []
    count = 0
    for c in chunks:
        text = c.get("text", "")
        words = text.split()
        if count + len(words) > budget_tokens:
            # include partial if nothing added yet
            if count == 0:
                out.append(" ".join(words[:max(1, budget_tokens)]))
            break
        out.append(text)
        count += len(words)
    return "\n\n---\n\n".join(out)


def mmr_select(candidates: List[Dict], k: int = 8, lambda_mul: float = 0.7) -> List[Dict]:
    """
    Simple selection that picks top-k by score and attempts to reduce redundancy by skipping exact duplicates.
    Each candidate should be a dict with 'chunk_id' and 'score'.
    """
    seen_texts = set()
    out = []
    for c in sorted(candidates, key=lambda x: x.get("score", 0), reverse=True):
        txt = c.get("text", "")
        if txt in seen_texts:
            continue
        seen_texts.add(txt)
        out.append(c)
        if len(out) >= k:
            break
    return out
