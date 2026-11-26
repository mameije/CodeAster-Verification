#!/usr/bin/env python3
"""Read-only-to-benchmarks administration of archived Code_Aster verification runs.

Only writes under repository-level archive/ and registry/runs.csv.
Standard-library Python; independent of the classroom benchmark runners.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import uuid

from archive_utils import (
    SUMMARY_COLUMNS, content_fingerprint, is_scientific_file, matching_archive,
    summary_rows,
)

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "registry"
ARCHIVE = ROOT / "archive"
INDEX = REGISTRY / "runs.csv"
SUMMARY_INDEX = REGISTRY / "run_summary.csv"
COLUMNS = (
    "run_id", "case_id", "captured_utc", "mesh", "nominal_size_m",
    "max_actual_size_m", "elements", "nodes", "load_factor", "critical_value", "unit",
    "reference_value", "difference_pct", "case_status", "note",
)
RUN_PATTERN = re.compile(r"^C\d{2}-\d{8}T\d{6}Z-[0-9a-f]{6}$")


def catalog():
    data = json.loads((REGISTRY / "cases.json").read_text(encoding="utf-8"))
    if data.get("schema_version") != 1:
        raise ValueError("Unsupported cases.json schema version")
    return {row["id"]: row for row in data["cases"]}


def case_entry(case_id):
    cases = catalog()
    if case_id not in cases:
        raise ValueError(f"Unknown case {case_id}; available: {', '.join(sorted(cases))}")
    return cases[case_id]


def safe_relative(path):
    value = Path(path)
    if value.is_absolute() or ".." in value.parts or not value.parts:
        raise ValueError(f"Unsafe relative path: {path}")
    return value


def check_tree_no_symlinks(path):
    if path.is_symlink():
        raise ValueError(f"Symlinks are not supported in snapshots: {path}")
    if path.is_dir():
        for child in path.iterdir():
            check_tree_no_symlinks(child)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_revision():
    try:
        rev = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                             capture_output=True, text=True, check=True).stdout.strip()
        dirty = bool(subprocess.run(["git", "status", "--porcelain", "--untracked-files=no"],
                                    cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip())
        return {"commit": rev, "tracked_files_modified": dirty}
    except (OSError, subprocess.CalledProcessError):
        return {"commit": None, "tracked_files_modified": None}


def numerical_rows(case, results):
    case_id = case["id"]
    expected = case["result_column"]
    rows = []
    for mesh_dir in sorted(results.glob("M[0-9][0-9]")):
        if not mesh_dir.is_dir():
            continue
        source = mesh_dir / f"{case_id}_LBA_results.csv"
        if not source.is_file():
            continue
        with source.open(newline="", encoding="utf-8-sig") as stream:
            data = list(csv.DictReader(stream))
        if not data or expected not in data[0] or "load_factor" not in data[0]:
            raise ValueError(f"Missing LBA columns or rows in {source}")
        candidates = []
        for record in data:
            value = float(record[expected]); mu = float(record["load_factor"])
            if not (math.isfinite(value) and math.isfinite(mu) and value > 0 and mu > 0):
                raise ValueError(f"Invalid LBA data in {source}")
            candidates.append((value, mu))
        critical, factor = min(candidates)
        mesh_info_path = mesh_dir / "mesh.json"
        mesh_info = json.loads(mesh_info_path.read_text(encoding="utf-8")) if mesh_info_path.is_file() else {}
        case_info_path = mesh_dir / "case.json"
        case_info = json.loads(case_info_path.read_text(encoding="utf-8")) if case_info_path.is_file() else {}
        reference = case["primary_reference"]["value"]
        rows.append({
            "mesh": mesh_dir.name,
            "nominal_size_m": case_info.get("nominal_size_m", ""),
            "max_actual_size_m": max(mesh_info["circumferential_size_m"],
                                     mesh_info["axial_size_m"]) if all(
                                         k in mesh_info for k in
                                         ("circumferential_size_m", "axial_size_m")) else "",
            "elements": mesh_info.get("num_elements", ""),
            "nodes": mesh_info.get("num_nodes", ""),
            "load_factor": factor,
            "critical_value": critical * case["output_to_reference_factor"],
            "unit": case["primary_reference"]["unit"],
            "reference_value": reference,
            "difference_pct": 100 * (critical * case["output_to_reference_factor"] - reference) / reference,
        })
    if not rows:
        raise ValueError(f"No numerical LBA CSV files found in {results}; nothing to capture")
    return rows


def file_hashes(directory):
    return {p.relative_to(directory).as_posix(): sha256(p)
            for p in sorted(directory.rglob("*")) if p.is_file()}


def index_rows():
    cases = catalog()
    rows = []
    for case_id in sorted(cases):
        folder = ARCHIVE / case_id
        if not folder.is_dir():
            continue
        for run_folder in sorted(folder.iterdir()):
            if not run_folder.is_dir() or run_folder.name.startswith("."):
                continue
            manifest_path = run_folder / "manifest.json"
            if not manifest_path.is_file():
                continue
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            if manifest["run_id"] != run_folder.name or manifest["case_id"] != case_id:
                raise ValueError(f"Archive identity mismatch in {run_folder}")
            for item in manifest["results"]:
                rows.append({**item, "run_id": manifest["run_id"],
                             "case_id": case_id, "captured_utc": manifest["captured_utc"],
                             "case_status": manifest["case_status_at_capture"],
                             "note": manifest.get("note", "")})
    return sorted(rows, key=lambda r: (r["captured_utc"], r["run_id"], r["mesh"]))


def write_index(rows):
    REGISTRY.mkdir(exist_ok=True)
    temporary = INDEX.with_suffix(".csv.tmp")
    with temporary.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(INDEX)
    # Regenerate the independent, one-row-per-run navigation index.
    summaries = summary_rows(ARCHIVE, catalog())
    summary_temp = SUMMARY_INDEX.with_suffix(".csv.tmp")
    with summary_temp.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=SUMMARY_COLUMNS)
        writer.writeheader()
        writer.writerows(summaries)
    summary_temp.replace(SUMMARY_INDEX)


def capture(case_id, note):
    case = case_entry(case_id)
    source = ROOT / safe_relative(case["path"])
    results = source / "results"
    if not source.is_dir() or not results.is_dir():
        raise FileNotFoundError(f"Expected completed case results in {results}")
    check_tree_no_symlinks(source / "results")
    inputs = ["parameters.json", "run.py", "generate_mesh.py", "write_results.py", f"{case_id}_LA_LBA.comm"]
    for name in inputs:
        if not (source / name).is_file() or (source / name).is_symlink():
            raise FileNotFoundError(f"Missing or linked case input: {source / name}")
    rows = numerical_rows(case, results)
    # Hash relevant contents, not UI caches: allows duplicate detection across v1/v2.
    source_hashes = {f"inputs/{n}": sha256(source / n) for n in inputs}
    source_hashes.update({f"results/{p.relative_to(results).as_posix()}": sha256(p)
                          for p in sorted(results.rglob("*"))
                          if p.is_file() and is_scientific_file(p.relative_to(results).as_posix())})
    parent = ARCHIVE / case_id
    parent.mkdir(parents=True, exist_ok=True)
    duplicate_id = matching_archive(parent, source_hashes, file_hashes)
    if duplicate_id:
        write_index(index_rows())
        print(f"ALREADY_ARCHIVED {duplicate_id}: same inputs and numerical files; no copy made")
        return
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_id = f"{case_id}-{timestamp}-{uuid.uuid4().hex[:6]}"
    staging = parent / f".tmp-{run_id}"
    final = parent / run_id
    if staging.exists() or final.exists():
        raise FileExistsError(f"Run destination already exists: {run_id}")
    try:
        (staging / "snapshot" / "inputs").mkdir(parents=True)
        for name in inputs:
            shutil.copy2(source / name, staging / "snapshot" / "inputs" / name)
        shutil.copytree(results, staging / "snapshot" / "results",
                        ignore=shutil.ignore_patterns("__pycache__", ".vs-code-aster", "*.pyc", "*.pyo"))
        copied_hashes = file_hashes(staging / "snapshot")
        if copied_hashes != source_hashes:
            raise RuntimeError("Inputs or outputs changed during snapshot; archive rejected")
        manifest = {
            "schema_version": 1, "run_id": run_id, "case_id": case_id,
            "captured_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "case_status_at_capture": case["status"],
            "status_note": "Captured numerical output; not automatically verified",
            "note": note, "source_case_path": case["path"],
            "git": git_revision(), "platform": platform.platform(),
            "python_version": platform.python_version(),
            "code_aster_version": "Not automatically determined",
            "results": rows, "sha256": copied_hashes,
            "content_fingerprint": content_fingerprint(copied_hashes),
        }
        (staging / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        staging.rename(final)
    except BaseException:
        if staging.exists():
            shutil.rmtree(staging)
        raise
    write_index(index_rows())
    print(f"CAPTURED {run_id}: {len(rows)} numerical mesh(es); stored at {final}")
    print(f"Index: {INDEX}")


def restore(run_id):
    if not RUN_PATTERN.fullmatch(run_id):
        raise ValueError("Invalid run ID")
    # Rebuild from the archived manifest files if necessary, then look up the run in the CSV.
    write_index(index_rows())
    with INDEX.open(newline="", encoding="utf-8") as stream:
        found = [row for row in csv.DictReader(stream) if row["run_id"] == run_id]
    if not found:
        raise FileNotFoundError(f"Run not present in registry: {run_id}")
    case_id = found[0]["case_id"]
    original = ARCHIVE / case_id / run_id
    manifest = json.loads((original / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("run_id") != run_id or manifest.get("case_id") != case_id:
        raise ValueError("Archive manifest identity mismatch")
    snapshot = original / "snapshot"
    check_tree_no_symlinks(snapshot)
    if file_hashes(snapshot) != manifest["sha256"]:
        raise RuntimeError("Archive integrity verification failed; recovery refused")
    destination = ARCHIVE / "recovered" / run_id
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() or destination.is_symlink():
        raise FileExistsError(f"Recovery destination already exists: {destination}")
    shutil.copytree(snapshot, destination)
    if file_hashes(destination) != manifest["sha256"]:
        shutil.rmtree(destination)
        raise RuntimeError("Recovered copy integrity verification failed")
    print(f"RESTORED {run_id} to {destination}")
    print("The original benchmark directories and their results were not modified.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("cases", help="List catalogued Brush benchmarks")
    p = sub.add_parser("capture", help="Archive completed case results without changing the case")
    p.add_argument("--case", required=True, choices=sorted(catalog()))
    p.add_argument("--note", default="")
    p = sub.add_parser("list", help="Rebuild and display the local run index")
    p.add_argument("--case", choices=sorted(catalog()))
    p.add_argument("--details", action="store_true", help="Show all mesh rows instead of one row per run")
    p = sub.add_parser("duplicates", help="Report identical archived runs; never deletes archives")
    p.add_argument("--case", choices=sorted(catalog()))
    p = sub.add_parser("restore", help="Recover a checked run outside the benchmark directories")
    p.add_argument("--run", required=True)
    args = parser.parse_args()
    if args.command == "cases":
        for case_id, c in sorted(catalog().items()):
            ref = c["primary_reference"]
            print(f"{case_id} | {c['status']} | {ref['value']} {ref['unit']} | {c['path']}")
    elif args.command == "capture":
        capture(args.case, args.note)
    elif args.command == "list":
        rows = index_rows(); write_index(rows)
        if args.details:
            selected = [r for r in rows if not args.case or r["case_id"] == args.case]
            for r in selected:
                print(f"{r['run_id']} | {r['mesh']} | {r['critical_value']:.9g} {r['unit']} | "
                      f"difference={r['difference_pct']:+.4f}% | {r['note']}")
        else:
            selected = [r for r in summary_rows(ARCHIVE, catalog())
                        if not args.case or r["case_id"] == args.case]
            for r in selected:
                print(f"{r['run_id']} | {r['mesh_count']} meshes | finest={r['finest_mesh']} | "
                      f"{r['critical_value']:.9g} {r['unit']} | {r['note']}")
        if not selected:
            print("No archived numerical runs yet")
        print(f"Indices refreshed: {INDEX} and {SUMMARY_INDEX}")
    elif args.command == "duplicates":
        found = False
        for case_id in sorted(catalog()):
            if args.case and args.case != case_id:
                continue
            folder = ARCHIVE / case_id
            if not folder.is_dir():
                continue
            groups = {}
            for run_folder in sorted(folder.iterdir()):
                manifest_file = run_folder / "manifest.json"
                if run_folder.is_symlink() or not run_folder.is_dir() or not manifest_file.is_file():
                    continue
                manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
                fingerprint = content_fingerprint(manifest["sha256"])
                groups.setdefault(fingerprint, []).append(run_folder.name)
            for run_ids in groups.values():
                if len(run_ids) > 1:
                    found = True
                    print(f"{case_id} | identical snapshots: {', '.join(run_ids)}")
        if not found:
            print("No duplicate snapshot fingerprints found")
        print("No archives were deleted")
    elif args.command == "restore":
        restore(args.run)


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, RuntimeError) as exc:
        sys.exit(f"ERROR: {exc}")
