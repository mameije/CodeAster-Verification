# -*- coding: utf-8 -*-
"""Prepare and run C01 meshes locally, or regenerate convergence plots.

Commands:
  python3 run.py --mesh-index 4
  python3 run.py --convergence
  python3 run.py --plots-only
  python3 run.py --convergence --prepare-only

Only preparation and solver execution clear results/. --plots-only never does.
"""
from __future__ import annotations
import argparse
import csv
import json
import math
from pathlib import Path
import shutil
import subprocess
from generate_mesh import generate_mesh

ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
CASE_ID = "C01"
REFERENCE_KEY = "reference_pressure_MPa"
CRITICAL_KEY = "critical_pressure_MPa"
PLOT_KEY = "critical_pressure_kPa"


def read_parameters():
    """Validate physical inputs, mesh sizes and Code_Aster resources."""
    p = json.loads((ROOT / "parameters.json").read_text(encoding="utf-8"))
    for key in ("D", "H", "t", "E", REFERENCE_KEY):
        value = p[key]
        if not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
            raise ValueError(f"{key} must be positive and finite")
    if not -1 < p["nu"] < 0.5:
        raise ValueError("nu is outside the elastic range")
    if p["t"] >= p["D"]/2:
        raise ValueError("Shell thickness must be smaller than the radius")
    if not isinstance(p["num_modes"], int) or not 1 <= p["num_modes"] <= 12:
        raise ValueError("num_modes must be between 1 and 12")
    sizes = p["mesh_sizes_m"]
    if not isinstance(sizes, list) or not sizes:
        raise ValueError("mesh_sizes_m must contain at least one value")
    if any(not isinstance(h, (int, float)) or not math.isfinite(h) or h <= 0 for h in sizes):
        raise ValueError("Mesh sizes must be positive and finite")
    if len(set(sizes)) != len(sizes):
        raise ValueError("Mesh sizes must be distinct")
    if any(not isinstance(p["resources"][key], int) or p["resources"][key] < 1
           for key in ("ncpus", "mpi_nbcpu", "memory_limit_MB", "time_limit_s")):
        raise ValueError("Invalid Code_Aster resource limits")
    return p


def find_aster(command):
    """Check solver availability before removing any previous results."""
    executable = shutil.which(command) or (command if Path(command).is_file() else None)
    if executable is None:
        raise FileNotFoundError(f"{command} was not found; activate aster-mpi")
    return executable


def clear_results():
    """Restart with a clean local output directory; reject symlinks."""
    if RESULTS.is_symlink():
        raise RuntimeError("results/ must not be a symbolic link")
    if RESULTS.exists():
        if not RESULTS.is_dir():
            raise RuntimeError("results/ exists but is not a directory")
        shutil.rmtree(RESULTS)
        print(f"CLEANUP: deleted old results in {RESULTS}", flush=True)
    RESULTS.mkdir(parents=True, exist_ok=True)


def prepare(index, p):
    """Generate one native mesh, .comm, .export and JSON input."""
    h = p["mesh_sizes_m"][index - 1]
    folder = RESULTS / f"M{index:02d}"
    folder.mkdir(parents=True, exist_ok=True)
    mesh_info = generate_mesh(folder / "cylinder.mail", p["D"], p["H"], h)
    case = {key: p[key] for key in ("D", "H", "t", "E", "nu", REFERENCE_KEY, "num_modes")}
    case["id"] = f"{CASE_ID}_M{index:02d}"
    case["nominal_size_m"] = h
    (folder / "case.json").write_text(json.dumps(case, indent=2), encoding="utf-8")
    (folder / "mesh.json").write_text(json.dumps(mesh_info, indent=2), encoding="utf-8")
    for filename in (f"{CASE_ID}_LA_LBA.comm", "write_results.py"):
        shutil.copy2(ROOT / filename, folder / filename)
    resources = p["resources"]
    export = (
        f"P time_limit {resources['time_limit_s']}\n"
        f"P memory_limit {resources['memory_limit_MB']}\n"
        f"P ncpus {resources['ncpus']}\n"
        f"P mpi_nbcpu {resources['mpi_nbcpu']}\n"
        f"F comm {CASE_ID}_LA_LBA.comm D 1\n"
        f"F mess {CASE_ID}_LA_LBA.mess R 6\n"
        f"F rmed {CASE_ID}_LA.med R 80\n"
        f"F rmed {CASE_ID}_LBA.med R 81\n"
    )
    (folder / f"{CASE_ID}_LA_LBA.export").write_text(export, encoding="utf-8")
    print(f"M{index:02d} | h={h:g} m | {mesh_info['num_elements']} QUAD9 | "
          f"{mesh_info['num_nodes']} nodes | {folder}", flush=True)
    return folder


def execute(folder, solver):
    """Run the native Code_Aster export; require a fresh numerical CSV."""
    executable = find_aster(solver)
    logfile = folder / f"{CASE_ID}_LA_LBA.log"
    with logfile.open("w", encoding="utf-8") as stream:
        status = subprocess.run([executable, f"{CASE_ID}_LA_LBA.export"],
                                cwd=folder, stdout=stream,
                                stderr=subprocess.STDOUT, check=False).returncode
    if status:
        raise RuntimeError(f"run_aster returned {status}; inspect {logfile} and .mess")
    if not (folder / f"{CASE_ID}_LBA_results.csv").is_file():
        raise RuntimeError(f"Missing numerical LBA results in {folder}")
    print(f"OK: {folder}", flush=True)


def summary(indices, p):
    """Consolidate the first positive mode from each completed mesh."""
    rows = []
    for index in indices:
        folder = RESULTS / f"M{index:02d}"
        source = folder / f"{CASE_ID}_LBA_results.csv"
        if not source.is_file():
            continue
        with source.open(newline="", encoding="utf-8") as stream:
            modes = list(csv.DictReader(stream))
        if not modes:
            continue
        mesh = json.loads((folder / "mesh.json").read_text(encoding="utf-8"))
        critical = float(modes[0][CRITICAL_KEY])
        row = {
            "mesh": f"M{index:02d}",
            "nominal_size_m": p["mesh_sizes_m"][index - 1],
            "max_actual_size_m": max(mesh["circumferential_size_m"], mesh["axial_size_m"]),
            "elements": mesh["num_elements"], "nodes": mesh["num_nodes"],
            "load_factor": float(modes[0]["load_factor"]),
            CRITICAL_KEY: critical,
            "critical_pressure_kPa": 1000 * critical,
            "change_from_previous_pct": "",
        }
        rows.append(row)
    # Percentage changes follow the configured order; they are not error bounds.
    for i in range(1, len(rows)):
        previous, current = rows[i-1], rows[i]
        current["change_from_previous_pct"] = (
            100 * abs(current[PLOT_KEY] - previous[PLOT_KEY]) / abs(current[PLOT_KEY])
        )
    if rows:
        output = RESULTS / "convergence.csv"
        with output.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        print(f"Summary: {output}", flush=True)
        plot(rows)
    return rows


def plot(rows, required=False):
    """Save two SVG plots, keeping Latin Modern Roman text editable."""
    if len(rows) < 2:
        if required:
            raise ValueError("At least two meshes are required for convergence plots")
        return
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib import font_manager
    except ImportError as exc:
        if required:
            raise RuntimeError("Matplotlib is not installed in the active Python") from exc
        print("Matplotlib unavailable; convergence.csv was preserved", flush=True)
        return
    plt.rcParams["font.family"] = "serif"
    plt.rcParams["font.serif"] = ["Latin Modern Roman", "DejaVu Serif"]
    plt.rcParams["svg.fonttype"] = "none"
    if not any(f.name == "Latin Modern Roman" for f in font_manager.fontManager.ttflist):
        print("NOTE: Latin Modern Roman unavailable; using a fallback", flush=True)

    critical = [float(r[PLOT_KEY]) for r in rows]
    ylabel = "First critical pressure (kPa)"
    # Same data and plotting style; only the horizontal axis changes.
    for xvalues, xlabel, title, filename in (
        ([float(r["max_actual_size_m"]) for r in rows],
         "Maximum actual element size (m)", "Mesh-size convergence", "convergence.svg"),
        ([int(r["elements"]) for r in rows],
         "Number of QUAD9 elements", "Convergence by element count",
         "convergence_by_elements.svg"),
    ):
        fig, ax = plt.subplots()
        ax.plot(xvalues, critical, "o-")
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(f"{CASE_ID} - {title}")
        ax.grid(True)
        fig.tight_layout()
        fig.savefig(RESULTS / filename)
        plt.close(fig)
    print("Plots: convergence.svg and convergence_by_elements.svg", flush=True)


def plots_only():
    """Read existing convergence.csv without touching solver results."""
    source = RESULTS / "convergence.csv"
    if not source.is_file():
        raise FileNotFoundError(f"Missing {source}; run --convergence first")
    with source.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    plot(rows, required=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    options = parser.add_mutually_exclusive_group()
    options.add_argument("--mesh-index", type=int, default=None)
    options.add_argument("--convergence", action="store_true")
    options.add_argument("--plots-only", action="store_true")
    parser.add_argument("--prepare-only", action="store_true")
    parser.add_argument("--aster", default="run_aster")
    args = parser.parse_args()
    if args.plots_only:
        if args.prepare_only:
            parser.error("--plots-only is incompatible with --prepare-only")
        plots_only()
        return

    p = read_parameters()
    count = len(p["mesh_sizes_m"])
    indices = list(range(1, count+1)) if args.convergence else [args.mesh_index or 1]
    if any(i < 1 or i > count for i in indices):
        parser.error(f"Mesh index must be between 1 and {count}")
    if not args.prepare_only:
        find_aster(args.aster)
    clear_results()
    for index in indices:
        folder = prepare(index, p)
        if not args.prepare_only:
            execute(folder, args.aster)
    if args.prepare_only:
        print("Preparation only: Code_Aster was not executed", flush=True)
    else:
        summary(indices, p)


if __name__ == "__main__":
    main()
