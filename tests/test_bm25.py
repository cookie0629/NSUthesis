import math
import unittest

from nurbs_knowledge.common import tokenize
from nurbs_knowledge.index.bm25 import BM25


class BM25Tests(unittest.TestCase):
    def test_hand_computed_scores(self):
        # N=2, df(alpha)=1, avgdl=2; independent arithmetic with exact constants.
        index = BM25([{"chunk_id": "a", "text": "alpha alpha beta"},
                      {"chunk_id": "b", "text": "beta"}])
        rows = index.search("alpha")
        self.assertEqual([row["chunk_id"] for row in rows], ["a"])
        self.assertAlmostEqual(rows[0]["score"], math.log(2) * 5 / 4.0625, places=12)
        beta = index.search("beta")
        self.assertEqual([row["chunk_id"] for row in beta], ["b", "a"])
        self.assertAlmostEqual(beta[0]["score"], math.log(1.2) * 2.5 / 1.9375, places=12)
        self.assertAlmostEqual(beta[1]["score"], math.log(1.2) * 2.5 / 3.0625, places=12)

    def test_tie_break_and_repeated_query_terms(self):
        rows = [{"chunk_id": "z", "text": "surface"}, {"chunk_id": "a", "text": "surface"}]
        first = BM25(rows).search("surface")
        self.assertEqual(first, BM25(list(reversed(rows))).search("surface surface"))
        self.assertEqual([row["chunk_id"] for row in first], ["a", "z"])

    def test_unicode_and_api_identifiers(self):
        self.assertEqual(tokenize("ПОВЕРХНОСТЬ Geom_BSplineSurface ＡＢＣ"),
                         ["поверхность", "geom_bsplinesurface", "abc"])
        index = BM25([{"chunk_id": "ru", "text": "Поверхность"},
                      {"chunk_id": "api", "text": "Geom_BSplineSurface"}])
        self.assertEqual(index.search("ПОВЕРХНОСТЬ")[0]["chunk_id"], "ru")
        self.assertEqual(index.search("geom_bsplinesurface")[0]["chunk_id"], "api")

    def test_no_matching_terms_and_empty_corpus(self):
        self.assertEqual(BM25([{"chunk_id": "a", "text": "surface"}]).search("поверхность"), [])
        self.assertEqual(BM25([]).search("surface"), [])
        self.assertEqual(BM25([{"chunk_id": "a", "text": "!!!"}]).search("surface"), [])

    def test_invalid_queries_and_parameters(self):
        index = BM25([{"chunk_id": "a", "text": "surface"}])
        for query in ["", "  ", "?!"]:
            with self.subTest(query=query), self.assertRaises(ValueError):
                index.search(query)
        for top_k in [0, -1, True, 1.2]:
            with self.subTest(top_k=top_k), self.assertRaises(ValueError):
                index.search("surface", top_k)
        for k1, b in [(0, .75), (float("nan"), .75), (1.5, 2), (1.5, float("inf"))]:
            with self.subTest(k1=k1, b=b), self.assertRaises(ValueError):
                BM25([], k1, b)


if __name__ == "__main__":
    unittest.main()
