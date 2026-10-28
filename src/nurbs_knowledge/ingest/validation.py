"""Validate corpus provenance before any retrieval."""
from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

from src.nurbs_knowledge.common import comment_text, local_path, read_jsonl, sha256_file, text_hash

SOURCE_FIELDS = (
    "source_id", "title", "publisher", "canonical_url", "retrieved_at", "language",
    "product_version", "license_name", "license_url", "permission_status", "permitted_use",
    "local_path", "content_sha256", "notes",
)
CHUNK_FIELDS = (
    "chunk_id", "source_id", "section_title", "locator", "text", "language",
    "product_version", "content_sha256",
)


def _strings(row: dict, fields: tuple[str, ...], prefix: str, errors: list[str]) -> bool:
    ok = True
    for key in fields:
        if not isinstance(row.get(key), str) or not row[key].strip():
            errors.append(f"{prefix}: {key} must be a nonempty string")
            ok = False
    return ok


def _file_hash(root: Path, path_value: str, expected: str) -> Path:
    path = local_path(root, path_value)
    if not re.fullmatch(r"[a-f0-9]{64}", expected) or sha256_file(path) != expected:
        raise ValueError(f"SHA-256 mismatch: {path_value}")
    return path


def validate_corpus(root: Path) -> tuple[dict[str, dict], list[dict], list[str]]:
    source_path = root / "data/sources/registry.jsonl"
    chunk_path = root / "data/processed/chunks.jsonl"
    source_rows, errors = read_jsonl(source_path)
    chunk_rows, chunk_errors = read_jsonl(chunk_path)
    errors.extend(chunk_errors)
    sources, chunks, seen_ids, seen_hashes = {}, [], set(), set()
    for number, row in source_rows:
        prefix = f"{source_path}:{number}"
        if not _strings(row, ("source_id", "title", "permission_status"), prefix, errors):
            continue
        source_id = row["source_id"]
        if source_id in sources:
            errors.append(f"{prefix}: duplicate source_id {source_id}")
            continue
        sources[source_id] = row
        if row["permission_status"] not in {"pending", "approved", "excluded"}:
            errors.append(f"{prefix}: invalid permission_status")
        missing = [field for field in SOURCE_FIELDS if field not in row]
        if missing:
            errors.append(f"{prefix}: missing fields: {', '.join(missing)}")
        # Pending/excluded candidates can have unknown/null fields, but can never supply chunks.
        if row["permission_status"] != "approved":
            continue
        if not _strings(row, SOURCE_FIELDS + ("license_local_path", "license_sha256", "permission_evidence"), prefix, errors):
            continue
        try:
            for key in ("canonical_url", "license_url"):
                parsed = urlparse(row[key])
                if parsed.scheme not in {"https", "http"} or not parsed.netloc:
                    raise ValueError(f"invalid {key}")
            date = datetime.fromisoformat(row["retrieved_at"])
            if date.tzinfo is None:
                raise ValueError("retrieved_at must include timezone")
            _file_hash(root, row["local_path"], row["content_sha256"])
            _file_hash(root, row["license_local_path"], row["license_sha256"])
            if "exception_local_path" in row or "exception_sha256" in row:
                if not _strings(row, ("exception_local_path", "exception_sha256"), prefix, errors):
                    continue
                _file_hash(root, row["exception_local_path"], row["exception_sha256"])
        except (OSError, ValueError, TypeError) as exc:
            errors.append(f"{prefix}: {exc}")
    for number, row in chunk_rows:
        prefix = f"{chunk_path}:{number}"
        if not _strings(row, CHUNK_FIELDS, prefix, errors):
            continue
        if row["chunk_id"] in seen_ids:
            errors.append(f"{prefix}: duplicate chunk_id {row['chunk_id']}")
        seen_ids.add(row["chunk_id"])
        digest = text_hash(row["text"])
        if digest != row["content_sha256"]:
            errors.append(f"{prefix}: text SHA-256 mismatch")
        if digest in seen_hashes:
            errors.append(f"{prefix}: duplicate normalized chunk text")
        seen_hashes.add(digest)
        source = sources.get(row["source_id"])
        if source is None:
            errors.append(f"{prefix}: unknown source_id {row['source_id']}")
            continue
        if source["permission_status"] != "approved":
            errors.append(f"{prefix}: source is not approved")
            continue
        if any(row[key] != source.get(key) for key in ("language", "product_version")):
            errors.append(f"{prefix}: language/version differs from source")
        # v1 corpus uses line-anchored, verbatim OCCT Doxygen comments.
        match = re.fullmatch(re.escape(source.get("canonical_url", "")) + r"#L(\d+)-L(\d+)", row["locator"])
        try:
            if not match:
                raise ValueError("locator must be source URL plus #Lstart-Lend")
            start, end = map(int, match.groups())
            lines = local_path(root, source["local_path"]).read_text(encoding="utf-8").splitlines()
            if not (1 <= start <= end <= len(lines)):
                raise ValueError("locator is outside source line range")
            if comment_text(lines[start - 1:end]) != row["text"]:
                raise ValueError("chunk text differs from source lines")
        except (OSError, ValueError, TypeError, KeyError) as exc:
            errors.append(f"{prefix}: {exc}")
        chunks.append(row)
    if not chunks:
        errors.append(f"{chunk_path}: no usable chunks; corpus is not ready")
    return sources, chunks, errors


def validate_questions(path: Path) -> tuple[list[dict], list[str]]:
    rows, errors = read_jsonl(path)
    ids = set()
    categories = {"definition_api", "representation", "fitting", "boundary_continuity", "tolerance_validity"}
    questions = []
    for number, row in rows:
        prefix = f"{path}:{number}"
        if not _strings(row, ("query_id", "family_id", "language", "category", "question", "evidence_need", "origin", "source_note", "review_status"), prefix, errors):
            continue
        if row["query_id"] in ids:
            errors.append(f"{prefix}: duplicate query_id")
        ids.add(row["query_id"])
        if row["category"] not in categories or row["origin"] not in {"synthetic", "real_task"}:
            errors.append(f"{prefix}: invalid category/origin")
        questions.append(row)
    if not questions:
        errors.append(f"{path}: no development questions")
    return questions, errors
