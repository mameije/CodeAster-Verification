#!/usr/bin/env python3
"""Compare archived Code_Aster runs with independent Brush analytical equations.

Never changes archived source snapshots or the self-contained student cases.
Outputs generated comparisons under archive/comparisons and registry/comparisons.csv.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import re
import sys

from theory.brush_1975 import discrete_minimum

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "registry"
ARCHIVE = ROOT / "archive"
MODEL_FILE = REGISTRY / "theory" / "models.json"
COMPARISONS = ARCHIVE / "comparisons"
INDEX = REGISTRY / "comparisons.csv"
ID_PATTERN = re.compile(r"^C\d{2}-\d{8}T\d{6}Z-[0-9a-f]{6}$")
FIELDS = (
    "run_id", "case_id", "mesh", "nominal_size_m", "elements", "nodes",
    "numerical_value", "theoretical_value", "unit", "difference_pct",
    "m", "n", "reference_model", "equation",
)


def load_config():
    cases_data = json.loads((REGISTRY / "cases.json").read_text(encoding="utf-8"))
    models_data = json.loads(MODEL_FILE.read_text(encoding="utf-8"))
    if cases_data.get("schema_version") != 1 or models_data.get("schema_version") != 1:
        raise ValueError("Unsupported catalogue/theory schema version")
    return {c["id"]: c for c in cases_data["cases"]}, models_data["models"]


def file_sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verified_read(snapshot, manifest, relative):
    if relative not in manifest["sha256"]:
        raise ValueError(f"Archived manifest lacks integrity hash for {relative}")
    path = snapshot / relative
    if path.is_symlink() or not path.is_file() or file_sha256(path) != manifest["sha256"][relative]:
        raise ValueError(f"Missing, linked or altered archived file: {path}")
    return path


def parameters_for_mesh(snapshot, manifest, mesh):
    relative = f"results/{mesh}/case.json"
    if relative not in manifest["sha256"]:
        relative = "inputs/parameters.json"
    data = json.loads(verified_read(snapshot, manifest, relative).read_text(encoding="utf-8"))
    return {k: data[k] for k in ("D", "H", "t", "E", "nu")}


def numerical_from_csv(snapshot, manifest, case, mesh):
    relative = f"results/{mesh}/{case['id']}_LBA_results.csv"
    path = verified_read(snapshot, manifest, relative)
    with path.open(newline="", encoding="utf-8-sig") as stream:
        records = list(csv.DictReader(stream))
    key = case["result_column"]
    if not records or key not in records[0]:
        raise ValueError(f"Missing or empty LBA result column {key} in {path}")
    values = [float(record[key]) for record in records]
    if any(not math.isfinite(value) or value <= 0 for value in values):
        raise ValueError(f"Invalid positive critical values in {path}")
    return min(values) * float(case["output_to_reference_factor"])


def analyse_run(run_folder, cases, models):
    manifest_file = run_folder / "manifest.json"
    if run_folder.is_symlink() or not manifest_file.is_file():
        raise ValueError(f"Missing or linked archived manifest: {run_folder}")
    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    run_id, case_id = manifest["run_id"], manifest["case_id"]
    if not ID_PATTERN.fullmatch(run_id) or run_id != run_folder.name or case_id != run_folder.parent.name:
        raise ValueError(f"Invalid archived run identity: {run_folder}")
    if case_id not in cases or case_id not in models:
        raise ValueError(f"Unconfigured theory for case: {case_id}")
    case, model = cases[case_id], models[case_id]
    if model["unit"] != case["primary_reference"]["unit"]:
        raise ValueError("Model output unit does not match registry unit")
    snapshot = run_folder / "snapshot"
    if snapshot.is_symlink() or not snapshot.is_dir():
        raise ValueError(f"Missing or linked archived snapshot: {run_folder}")
    rows = []
    for numerical in manifest["results"]:
        mesh = numerical["mesh"]
        if not re.fullmatch(r"M\d{2}", mesh):
            raise ValueError(f"Invalid mesh identifier: {mesh}")
        params = parameters_for_mesh(snapshot, manifest, mesh)
        theory = discrete_minimum(case_id, params, model["search_limits"])
        critical = numerical_from_csv(snapshot, manifest, case, mesh)
        expected = float(numerical["critical_value"])
        if not math.isclose(critical, expected, rel_tol=1e-9, abs_tol=1e-9):
            raise ValueError(f"Archived manifest and LBA CSV disagree for {mesh}")
        if numerical["unit"] != model["unit"]:
            raise ValueError(f"Numerical unit mismatch for {mesh}")
        rows.append({
            "run_id": run_id, "case_id": case_id, "mesh": mesh,
            "nominal_size_m": numerical.get("nominal_size_m", ""),
            "elements": numerical.get("elements", ""),
            "nodes": numerical.get("nodes", ""),
            "numerical_value": critical, "theoretical_value": theory["value"],
            "unit": theory["unit"],
            "difference_pct": 100 * (critical - theory["value"]) / theory["value"],
            "m": theory["m"], "n": theory["n"],
            "reference_model": model["id"], "equation": model["equation"],
        })
    if not rows:
        raise ValueError(f"Archived run has no numerical meshes: {run_id}")
    return manifest, model, rows


def save_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(".csv.tmp")
    with temp.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    temp.replace(path)


def report_markdown(manifest, model, rows):
    line = [f"# Archived comparison — {manifest['run_id']}", "",
            f"Case: **{manifest['case_id']}** · Model: **{model['id']}** · "
            f"Brush & Almroth (1975), Eq. {model['equation']} (p. {model['printed_page']}).",
            "", f"Captured: {manifest.get('captured_utc', '')}  ",
            f"Run note: {manifest.get('note', '')}  ",
            "Reference: bounded discrete minimization over integer wave numbers "
            f"{model['search_limits']}.", "",
            "| Mesh | Elements | Code_Aster | Theory | Difference (%) | m | n |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for r in rows:
        line.append(f"| {r['mesh']} | {r['elements']} | {r['numerical_value']:.9g} "
                    f"{r['unit']} | {r['theoretical_value']:.9g} {r['unit']} | "
                    f"{r['difference_pct']:+.5f} | {r['m']} | {r['n']} |")
    line += ["", "Comparison is computational, not an automatic scientific approval.",
             "Finite mode search bounds are recorded; review mode/boundary assumptions separately.",
             "Archived inputs and solver outputs were not modified.", ""]
    return "\n".join(line)


def maybe_plot(out, rows, manifest):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("Plot skipped: Matplotlib is not installed (CSV and Markdown were saved)")
        return
    xs = list(range(1, len(rows) + 1))
    fig, ax = plt.subplots()
    ax.plot(xs, [float(r["numerical_value"]) for r in rows], "o-", label="Code_Aster")
    ax.plot(xs, [float(r["theoretical_value"]) for r in rows], "s--", label="Brush Eq. " + rows[0]["equation"])
    ax.set_xticks(xs, [r["mesh"] for r in rows])
    ax.set_ylabel(f"Critical value ({rows[0]['unit']})")
    ax.set_xlabel("Mesh")
    ax.set_title(f"{manifest['case_id']} — archived run comparison")
    ax.grid(True)
    ax.legend()
    fig.tight_layout()
    plt.rcParams["svg.fonttype"] = "none"
    fig.savefig(out / "comparison.svg")
    plt.close(fig)


def refresh_index():
    gathered = []
    if COMPARISONS.is_dir():
        for folder in sorted(COMPARISONS.iterdir()):
            if folder.is_symlink() or not folder.is_dir() or not ID_PATTERN.fullmatch(folder.name):
                continue
            source = folder / "comparison.csv"
            if not source.is_file():
                continue
            with source.open(newline="", encoding="utf-8") as stream:
                for row in csv.DictReader(stream):
                    if row["run_id"] != folder.name:
                        raise ValueError(f"Invalid comparison index identity: {source}")
                    gathered.append(row)
    save_csv(INDEX, gathered)
    return len(gathered)


def main():
    cases, models = load_config()
    parser = argparse.ArgumentParser(description=__doc__)
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument("--run", help="One archived run identifier")
    selection.add_argument("--case", choices=sorted(models), help="All archived runs for one case")
    selection.add_argument("--all", action="store_true", help="All archived runs")
    args = parser.parse_args()
    folders = []
    if args.run:
        if not ID_PATTERN.fullmatch(args.run):
            parser.error("Invalid archived run identifier")
        folders = [ARCHIVE / args.run.split("-")[0] / args.run]
    else:
        case_ids = [args.case] if args.case else sorted(models)
        for case_id in case_ids:
            case_archive = ARCHIVE / case_id
            if case_archive.is_dir():
                folders += [p for p in sorted(case_archive.iterdir())
                            if p.is_dir() and not p.is_symlink()
                            and ID_PATTERN.fullmatch(p.name)]
    for folder in folders:
        manifest, model, rows = analyse_run(folder, cases, models)
        output = COMPARISONS / manifest["run_id"]
        output.mkdir(parents=True, exist_ok=True)
        save_csv(output / "comparison.csv", rows)
        (output / "report.md").write_text(report_markdown(manifest, model, rows), encoding="utf-8")
        maybe_plot(output, rows, manifest)
        print(f"COMPARED {manifest['run_id']}: {len(rows)} meshes; {output}")
    count = refresh_index()
    print(f"Global comparison index: {INDEX} ({count} mesh rows)")
    if not folders:
        print("No archived runs selected; no comparisons were generated")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, RuntimeError, json.JSONDecodeError) as exc:
        sys.exit(f"ERROR: {exc}")
