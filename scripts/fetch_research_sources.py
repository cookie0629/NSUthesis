"""Download pinned OCCT header documentation and research metadata (stdlib only)."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
HEADERS = {
    "occt_geom_bspline_surface": "src/Geom/Geom_BSplineSurface.hxx",
    "occt_geom_surface": "src/Geom/Geom_Surface.hxx",
    "occt_points_to_bspline_surface": "src/GeomAPI/GeomAPI_PointsToBSplineSurface.hxx",
    "occt_geomabs_shape": "src/GeomAbs/GeomAbs_Shape.hxx",
    "occt_brep_tool": "src/BRep/BRep_Tool.hxx",
    "occt_brepcheck_analyzer": "src/BRepCheck/BRepCheck_Analyzer.hxx",
}


def fetch(url: str) -> bytes:
    request = Request(url, headers={"User-Agent": "nurbs-knowledge-research/0.1"})
    with urlopen(request, timeout=60) as response:
        return response.read()


def main() -> None:
    raw = ROOT / "data/raw/occt-7.9.0"
    raw.mkdir(parents=True, exist_ok=True)
    evidence = ROOT / "references/literature/verification"
    evidence.mkdir(parents=True, exist_ok=True)
    ref_url = "https://api.github.com/repos/Open-Cascade-SAS/OCCT/git/ref/tags/V7_9_0"
    ref_data = fetch(ref_url)
    (evidence / "occt_tag_ref.json").write_bytes(ref_data)
    obj = json.loads(ref_data)["object"]
    while obj["type"] == "tag":
        tag_data = fetch(obj["url"])
        (evidence / "occt_tag.json").write_bytes(tag_data)
        obj = json.loads(tag_data)["object"]
    if obj["type"] != "commit":
        raise ValueError("Tag did not resolve to a commit")
    commit = obj["sha"]
    base = f"https://raw.githubusercontent.com/Open-Cascade-SAS/OCCT/{commit}/"
    records = []
    paths = {**HEADERS, "license": "LICENSE_LGPL_21.txt", "exception": "OCCT_LGPL_EXCEPTION.txt"}
    for source_id, upstream in paths.items():
        url = base + upstream
        target = raw / Path(upstream).name
        record = {"source_id": source_id, "upstream_path": upstream, "url": url,
                  "commit": commit, "product_version": "OCCT 7.9.0 (V7_9_0)",
                  "retrieved_at": datetime.now(timezone.utc).isoformat()}
        try:
            payload = fetch(url)
            target.write_bytes(payload)
            record.update(local_path=target.relative_to(ROOT).as_posix(),
                          content_sha256=hashlib.sha256(payload).hexdigest(), status="downloaded")
            if source_id in {"license", "exception"}:
                (evidence / target.name).write_bytes(payload)
        except Exception as exc:
            record.update(status="failed", error=str(exc))
        records.append(record)
        print(source_id, record["status"])
    manifest = {"tag": "V7_9_0", "commit": commit, "files": records}
    (evidence / "occt_download_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    papers = {
        "bm25_crossref": "https://api.crossref.org/works/10.1561/1500000019",
        "sbert_acl": "https://aclanthology.org/D19-1410/",
        "sbert_bib": "https://aclanthology.org/D19-1410.bib",
        "rag_arxiv": "https://arxiv.org/abs/2005.11401",
        "rag_neurips": "https://papers.nips.cc/paper/2020/hash/6b493230205f780e1bc26945df7481e5-Abstract.html",
    }
    checks = []
    for name, url in papers.items():
        try:
            payload = fetch(url)
            suffix = ".json" if "crossref" in name else ".bib" if name.endswith("bib") else ".html"
            target = evidence / (name + suffix)
            target.write_bytes(payload)
            checks.append({"name": name, "url": url, "status": "downloaded",
                           "retrieved_at": datetime.now(timezone.utc).isoformat(),
                           "local_path": target.relative_to(ROOT).as_posix(),
                           "sha256": hashlib.sha256(payload).hexdigest()})
            print(name, "downloaded", len(payload))
        except Exception as exc:
            checks.append({"name": name, "url": url, "status": "failed", "error": str(exc)})
            print(name, "failed", exc)
    (evidence / "bibliography_verification.json").write_text(
        json.dumps(checks, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
