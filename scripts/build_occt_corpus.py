"""Rebuild the curated development corpus from pinned local source files."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from src.nurbs_knowledge.common import comment_text, sha256_file, text_hash  # noqa: E402


def main() -> None:
    evidence = ROOT / "references/literature/verification"
    manifest = json.loads((evidence / "occt_download_manifest.json").read_text(encoding="utf-8"))
    selection = json.loads((ROOT / "configs/occt_excerpt_selection.json").read_text(encoding="utf-8"))
    if selection["commit"] != manifest["commit"]:
        raise ValueError("Selected line ranges belong to another commit")
    files = {record["source_id"]: record for record in manifest["files"]}
    license_file = evidence / "LICENSE_LGPL_21.txt"
    exception_file = evidence / "OCCT_LGPL_EXCEPTION.txt"
    if sha256_file(license_file) != files["license"]["content_sha256"] or sha256_file(exception_file) != files["exception"]["content_sha256"]:
        raise ValueError("License evidence hash mismatch")
    sources, chunks = [], []
    for source_id, ranges in selection["selections"].items():
        record = files[source_id]
        path = ROOT / record["local_path"]
        if record["status"] != "downloaded" or sha256_file(path) != record["content_sha256"]:
            raise ValueError(f"Missing or changed source: {source_id}")
        lines = path.read_text(encoding="utf-8").splitlines()
        if not all(phrase in "\n".join(lines[:16]) for phrase in ("Lesser General Public License version 2.1", "OCCT_LGPL_EXCEPTION.txt")):
            raise ValueError(f"Missing explicit license notice: {source_id}")
        url = f"https://github.com/Open-Cascade-SAS/OCCT/blob/{manifest['commit']}/{record['upstream_path']}"
        sources.append({
            "source_id": source_id, "title": path.stem + " API documentation (source comments)",
            "publisher": "Open CASCADE SAS / Open-Cascade-SAS/OCCT", "canonical_url": url,
            "retrieved_at": record["retrieved_at"], "language": "en", "product_version": record["product_version"],
            "license_name": "LGPL-2.1 with OCCT exception 1.0", "license_url": files["license"]["url"],
            "permission_status": "approved", "permitted_use": "Local research, verbatim comment extraction, local indexing; retain notices and license; no public distribution prepared",
            "local_path": record["local_path"], "content_sha256": record["content_sha256"],
            "license_local_path": license_file.relative_to(ROOT).as_posix(), "license_sha256": sha256_file(license_file),
            "exception_local_path": exception_file.relative_to(ROOT).as_posix(), "exception_sha256": sha256_file(exception_file),
            "permission_evidence": f"Explicit library license notice in {path.name}, lines 1-16; license and exception archived locally",
            "copyright_notice": "\n".join(lines[:16]),
            "notes": "Approval is for this local workflow based on explicit file notices; assistant checked, no independent human license review. Not website-documentation licensing."
        })
        for start, end, title in ranges:
            text = comment_text(lines[start - 1:end])
            chunks.append({"chunk_id": f"{source_id}_L{start:04d}_L{end:04d}", "source_id": source_id,
                           "section_title": title, "locator": f"{url}#L{start}-L{end}", "text": text,
                           "language": "en", "product_version": record["product_version"], "content_sha256": text_hash(text)})
    if len({item["content_sha256"] for item in chunks}) != len(chunks):
        raise ValueError("Duplicate selected text; update the curated selection")
    for relative, records in (("data/sources/registry.jsonl", sources), ("data/processed/chunks.jsonl", chunks)):
        (ROOT / relative).write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in records), encoding="utf-8")
    print(f"Built {len(sources)} sources and {len(chunks)} verbatim comment chunks")


if __name__ == "__main__":
    main()
