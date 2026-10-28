"""Shared, versioned normalization and provenance helpers."""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from pathlib import Path


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalized_text(text: str) -> str:
    return unicodedata.normalize("NFC", text.replace("\r\n", "\n").replace("\r", "\n")).strip()


def text_hash(text: str) -> str:
    return hashlib.sha256(normalized_text(text).encode("utf-8")).hexdigest()


def tokenize(text: str) -> list[str]:
    return re.findall(r"\w+", unicodedata.normalize("NFKC", text).casefold(), flags=re.UNICODE)


def comment_text(lines: list[str]) -> str:
    """Remove only Doxygen line markers; keep paragraph structure and wording."""
    if not lines or any(not line.lstrip().startswith("//!") for line in lines):
        raise ValueError("Selected lines must be a contiguous Doxygen //! block")
    return normalized_text("\n".join(re.sub(r"^\s*//! ?", "", line) for line in lines))


def local_path(root: Path, value: str) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("local path must be a nonempty string")
    path = (root / value).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError("path must stay inside the project")
    return path


def read_jsonl(path: Path) -> tuple[list[tuple[int, dict]], list[str]]:
    rows, errors = [], []
    try:
        lines = path.read_text(encoding="utf-8-sig").splitlines()
    except (OSError, UnicodeError) as exc:
        return [], [f"{path}: {exc}"]
    for number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
            if not isinstance(row, dict):
                raise ValueError("record must be a JSON object")
            rows.append((number, row))
        except (ValueError, TypeError) as exc:
            errors.append(f"{path}:{number}: {exc}")
    return rows, errors


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write("\n")
