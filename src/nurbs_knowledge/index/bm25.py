"""Small, deterministic BM25 index; no query expansion or external dependencies."""
from __future__ import annotations

import math
from collections import Counter

from nurbs_knowledge.common import tokenize


class BM25:
    def __init__(self, chunks: list[dict], k1: float = 1.5, b: float = 0.75):
        if not math.isfinite(k1) or k1 <= 0 or not math.isfinite(b) or not 0 <= b <= 1:
            raise ValueError("BM25 requires finite k1 > 0 and 0 <= b <= 1")
        self.chunks = sorted(chunks, key=lambda item: item["chunk_id"])
        self.k1, self.b = k1, b
        self.frequencies = [Counter(tokenize(item["text"])) for item in self.chunks]
        self.lengths = [sum(freq.values()) for freq in self.frequencies]
        self.average_length = sum(self.lengths) / len(self.lengths) if self.lengths else 0
        self.df = Counter(term for freq in self.frequencies for term in freq)

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        terms = sorted(set(tokenize(query)))
        if not terms:
            raise ValueError("query must contain at least one word or API identifier")
        if isinstance(top_k, bool) or not isinstance(top_k, int) or top_k <= 0:
            raise ValueError("top_k must be a positive integer")
        if not self.average_length:
            return []
        count = len(self.chunks)
        results = []
        for chunk, freq, length in zip(self.chunks, self.frequencies, self.lengths):
            score = 0.0
            for term in terms:
                tf = freq.get(term, 0)
                if not tf:
                    continue
                idf = math.log1p((count - self.df[term] + 0.5) / (self.df[term] + 0.5))
                score += idf * tf * (self.k1 + 1) / (tf + self.k1 * (1 - self.b + self.b * length / self.average_length))
            if score > 0:
                results.append({**chunk, "score": score})
        results.sort(key=lambda item: (-item["score"], item["chunk_id"]))
        return [{**item, "rank": rank} for rank, item in enumerate(results[:top_k], 1)]
