"""Validate, search, and record development demos from the project root."""
from __future__ import annotations

import argparse
import json
import math
import platform
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

from src.nurbs_knowledge.common import sha256_file, write_json
from src.nurbs_knowledge.index.bm25 import BM25
from src.nurbs_knowledge.ingest.validation import validate_corpus, validate_questions

ROOT = Path(__file__).resolve().parents[2]


def load_config(root: Path) -> dict:
    config = json.loads((root / "configs/bm25.json").read_text(encoding="utf-8"))
    for key in ("k1", "b"):
        if type(config.get(key)) not in (int, float) or not math.isfinite(config[key]):
            raise ValueError(f"config {key} must be a finite number")
    if config["k1"] <= 0 or not 0 <= config["b"] <= 1:
        raise ValueError("config requires k1 > 0 and 0 <= b <= 1")
    expected = {"method": "bm25", "tokenizer": "unicode_nfkc_casefold_word_v1",
                "idf": "log(1 + (N - df + 0.5) / (df + 0.5))", "query_terms": "unique"}
    if any(config.get(key) != value for key, value in expected.items()):
        raise ValueError("unsupported method, tokenizer, IDF or query term policy")
    if type(config.get("default_top_k")) is not int or config["default_top_k"] <= 0:
        raise ValueError("config default_top_k must be a positive integer")
    return config


def manifest(root: Path, config: dict, sources: dict, chunks: list[dict]) -> dict:
    paths = [root / name for name in ("configs/bm25.json", "data/sources/registry.jsonl", "data/processed/chunks.jsonl")]
    paths += sorted((root / "src/nurbs_knowledge").rglob("*.py"))
    paths += sorted((root / "scripts").glob("*.py"))
    selection = root / "configs/occt_excerpt_selection.json"
    if selection.exists():
        paths.append(selection)
    question_path = root / "data/evaluation/dev_questions.jsonl"
    if question_path.exists():
        paths.append(question_path)
    return {"created_at": datetime.now(timezone.utc).isoformat(), "stage": "development_demo",
            "python": sys.version, "executable": sys.executable, "platform": platform.platform(),
            "processor": platform.processor(), "dependencies": "Python standard library only",
            "config": config, "source_count": len(sources), "chunk_count": len(chunks),
            "file_sha256": {path.relative_to(root).as_posix(): sha256_file(path) for path in paths},
            "source_content_sha256": {key: value.get("content_sha256") for key, value in sources.items()},
            "random_seed": None, "randomness": "none; deterministic ranking",
            "api_cost_cny": 0, "limitation": "Development queries, no human relevance labels or test metrics"}


def retrieve(index: BM25, sources: dict, query: str, top_k: int) -> dict:
    start = time.perf_counter()
    results = index.search(query, top_k)
    elapsed = time.perf_counter() - start
    for item in results:
        source = sources[item["source_id"]]
        item.update(source_title=source["title"], source_url=source["canonical_url"])
    return {"query": query, "top_k": top_k, "results": results,
            "status": "matched" if results else "no_match", "search_seconds": elapsed,
            "timing_scope": "query tokenization and scoring; excludes corpus validation and index build"}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Traceable NURBS BM25 development prototype")
    parser.add_argument("--root", type=Path, default=ROOT, help="project root, default: source checkout")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("validate")
    search = commands.add_parser("search")
    search.add_argument("--query", required=True)
    search.add_argument("--top-k", type=int)
    search.add_argument("--output", type=Path, help="save JSON without overwriting an existing file")
    demo = commands.add_parser("demo")
    demo.add_argument("--top-k", type=int)
    args = parser.parse_args(argv)
    root = args.root.resolve()
    try:
        started = time.perf_counter()
        sources, chunks, errors = validate_corpus(root)
        if errors:
            for error in errors:
                print(error, file=sys.stderr)
            return 1
        if args.command == "validate":
            print(json.dumps({"status": "valid", "sources": len(sources), "chunks": len(chunks)}, indent=2))
            return 0
        config = load_config(root)
        top_k = args.top_k if args.top_k is not None else config["default_top_k"]
        if top_k <= 0:
            raise ValueError("top_k must be positive")
        index = BM25(chunks, config["k1"], config["b"])
        setup_seconds = time.perf_counter() - started
        metadata = manifest(root, config, sources, chunks)
        metadata.update(setup_seconds=setup_seconds, effective_top_k=top_k)
        if args.command == "search":
            result = retrieve(index, sources, args.query, top_k)
            result["manifest"] = metadata
            if args.output:
                write_json(args.output, result)
            print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
            return 0
        questions, errors = validate_questions(root / "data/evaluation/dev_questions.jsonl")
        if errors:
            for error in errors:
                print(error, file=sys.stderr)
            return 1
        records = [{"query_id": q["query_id"], "family_id": q["family_id"], "category": q["category"],
                    "language": q["language"], **retrieve(index, sources, q["question"], top_k)} for q in questions]
        run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "_bm25_" + uuid.uuid4().hex[:8]
        directory = root / "reports/demos" / run_id
        directory.mkdir(parents=True, exist_ok=False)
        metadata.update(run_id=run_id, query_count=len(records),
                        question_languages=sorted({q["language"] for q in questions}))
        write_json(directory / "manifest.json", metadata)
        with (directory / "retrieval.jsonl").open("x", encoding="utf-8") as output:
            for record in records:
                output.write(json.dumps(record, ensure_ascii=False, allow_nan=False) + "\n")
        write_json(directory / "summary.json", {
            "query_count": len(records), "queries_with_lexical_matches": sum(bool(r["results"]) for r in records),
            "note": "Lexical matches are NOT relevance judgments or evaluation metrics."})
        print(directory)
        return 0
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    raise SystemExit(main())
