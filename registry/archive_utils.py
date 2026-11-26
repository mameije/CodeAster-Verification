"""Pure administrative utilities for archival runs (no Code_Aster calls)."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

# Interpreter bytecode and editor preview caches are unrelated to the solver run.
EXCLUDED_DIRS = frozenset({"__pycache__", ".vs-code-aster"})
EXCLUDED_SUFFIXES = frozenset({".pyc", ".pyo"})
SUMMARY_COLUMNS = (
    "run_id", "case_id", "captured_utc", "note", "case_status",
    "mesh_count", "finest_mesh", "finest_nominal_size_m", "finest_elements",
    "critical_value", "unit", "reference_value", "difference_pct",
)


def is_scientific_file(relative_path: str) -> bool:
    """Select authored inputs and numerical solver results, excluding cache files."""
    parts = Path(relative_path).parts
    return not (any(part in EXCLUDED_DIRS for part in parts)
                or Path(relative_path).suffix.lower() in EXCLUDED_SUFFIXES)


def relevant_hashes(hashes: dict) -> dict:
    """Canonicalize hashes for old and new manifests without modifying them."""
    return {str(path): str(digest) for path, digest in hashes.items()
            if is_scientific_file(str(path))}


def content_fingerprint(hashes: dict) -> str:
    """Deterministic fingerprint of archived *file contents and paths*, not metadata."""
    digest = hashlib.sha256()
    for path, file_hash in sorted(relevant_hashes(hashes).items()):
        digest.update(path.encode("utf-8"))
        digest.update(b"\0")
        digest.update(file_hash.encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def matching_archive(case_archive: Path, current_hashes: dict, file_hashes) -> str | None:
    """Find an existing *intact* identical snapshot (supports legacy manifests)."""
    expected = content_fingerprint(current_hashes)
    if not case_archive.is_dir():
        return None
    for folder in sorted(case_archive.iterdir()):
        if not folder.is_dir() or folder.is_symlink() or folder.name.startswith("."):
            continue
        manifest_file = folder / "manifest.json"
        if not manifest_file.is_file() or manifest_file.is_symlink():
            continue
        manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
        if manifest.get("run_id") != folder.name:
            raise ValueError(f"Archive identity mismatch: {folder}")
        hashes = manifest.get("sha256", {})
        if content_fingerprint(hashes) != expected:
            continue
        snapshot = folder / "snapshot"
        # Integrity check before declaring an existing archive safely reusable.
        if not snapshot.is_dir() or snapshot.is_symlink():
            raise RuntimeError(f"Matching archive snapshot is missing: {folder}")
        existing = relevant_hashes(file_hashes(snapshot))
        if existing != relevant_hashes(hashes):
            raise RuntimeError(f"Matching archive fails integrity check: {folder}")
        return folder.name
    return None


def finest_result(results: list[dict]) -> dict:
    """Choose finest *available* mesh, never claim a mathematical limit."""
    if not results:
        raise ValueError("Archived run contains no numerical mesh results")

    def size(record):
        # Older manifests have only nominal_size_m; preserve compatibility.
        actual = record.get("max_actual_size_m")
        nominal = record.get("nominal_size_m")
        value = actual if actual not in (None, "") else nominal
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            numeric = math.inf
        if not math.isfinite(numeric) or numeric <= 0:
            numeric = math.inf
        return (numeric, -int(record.get("elements") or 0), str(record.get("mesh", "")))

    return min(results, key=size)


def summary_rows(archive: Path, cases: dict) -> list[dict]:
    """One entry per captured run, with the finest available mesh for navigation."""
    summaries = []
    for case_id in sorted(cases):
        parent = archive / case_id
        if not parent.is_dir():
            continue
        for folder in sorted(parent.iterdir()):
            if not folder.is_dir() or folder.is_symlink() or folder.name.startswith("."):
                continue
            manifest_file = folder / "manifest.json"
            if not manifest_file.is_file():
                continue
            manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
            if manifest.get("run_id") != folder.name or manifest.get("case_id") != case_id:
                raise ValueError(f"Archive identity mismatch: {folder}")
            results = manifest["results"]
            finest = finest_result(results)
            summaries.append({
                "run_id": folder.name,
                "case_id": case_id,
                "captured_utc": manifest.get("captured_utc", ""),
                "note": manifest.get("note", ""),
                "case_status": manifest.get("case_status_at_capture", ""),
                "mesh_count": len(results),
                "finest_mesh": finest["mesh"],
                "finest_nominal_size_m": finest.get("nominal_size_m", ""),
                "finest_elements": finest.get("elements", ""),
                "critical_value": finest["critical_value"],
                "unit": finest["unit"],
                "reference_value": finest["reference_value"],
                "difference_pct": finest["difference_pct"],
            })
    return sorted(summaries, key=lambda row: (row["captured_utc"], row["run_id"]))
