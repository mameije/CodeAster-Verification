# Verification registry and numerical-run archive (v2)

This **administrative** module is separate from the student benchmarks. It does not import or edit any of the `run.py`, `.comm`, `generate_mesh.py` or `parameters.json` files under `Shells/`. It uses Python's standard library and does not invoke Code_Aster.

## Sources of truth

- `registry/cases.json` (tracked in Git): scientific references and the **current scientific review state** of C01 and C02. Only reviewed changes to case status and `approved_run_ids` should be committed.
- `archive/<case>/<run_id>/manifest.json` (local, not tracked): immutable snapshot metadata and numerical results for a specific, *completed* local execution.
- `archive/<case>/<run_id>/snapshot/inputs/` and `snapshot/results/` (local, not tracked): inputs and the original solver output directory, including `.mess`, `.med`, mesh files and CSVs when produced.
- `registry/runs.csv` (local, not tracked): **rebuildable detailed index**, one row per mesh found in each archived execution. Includes the run note, numerical values, comparison columns and mesh details.
- `registry/run_summary.csv` (local, not tracked): **rebuildable navigation index**, one row per archived run, including its note, mesh count and the finest available mesh. This is a navigation convenience, **not a proof of convergence**.

The C01 historical value (734.883 kPa for 240 QUAD9) remains **historical evidence only** in `cases.json`: it is *not* presented as a restorable run. Both C01 and C02 now have five-mesh numerical/theoretical comparison rows in the tracked `registry/comparisons.csv`. Original solver artifacts remain in the local archives, not Git. Neither case has any `approved_run_ids` yet.

## Commands

Run from the `Verification` repository root (no solver environment required):

```bash
python3 registry/manage.py cases
python3 registry/manage.py list
python3 registry/manage.py list --case C02 --details
python3 registry/manage.py duplicates --case C02
```

After a benchmark has finished running successfully, **before its next execution clears its `results/`**, archive all available numerical mesh results, inputs and metadata (excluding interpreter and editor cache directories):

```bash
python3 registry/manage.py capture --case C01 --note "Mesh-convergence run"
python3 registry/manage.py capture --case C02 --note "First axial-compression trial"
```

To list a subset or restore an archived run, using the run ID printed by `capture` or displayed in the index:

```bash
python3 registry/manage.py list --case C01
python3 registry/manage.py restore --run C01-YYYYMMDDTHHMMSSZ-abcdef
```

The last line is a **format example**: use a real run ID. By default `list` displays **one row per archived run**, while `list --details` displays every mesh. The `duplicates` command reports identical snapshots but **never deletes anything**. Repeating `capture` with identical inputs and scientific outputs prints `ALREADY_ARCHIVED` and does not create a duplicate, even for a snapshot captured with v1.

Recovery copies the archived inputs and outputs to `archive/recovered/<run_id>/`. It **never overwrites** either the original archive or the active `Shells/C0x_.../results/` directory. If the recovery directory already exists, it stops rather than replacing it. It verifies SHA-256 hashes first and checks the recovered copy again.

Only finite, positive numerical LBA values from `C01_LBA_results.csv` or `C02_LBA_results.csv` are indexed. The script does not independently establish successful solver termination; review the archived `.mess` and execution log. The `capture` tool refuses a case with no numerical LBA CSVs (for example, a `--prepare-only` run). Each archived result is a **record**, not an automatically approved verification. Percentage differences compare the calculated critical value with the primary Brush reference; they are **not acceptance decisions** or error bounds.

## Retention, reproducibility and review

`archive/`, `registry/runs.csv` and `registry/run_summary.csv` are ignored by Git; `registry/comparisons.csv` is tracked. **They are not backed up or synchronized by GitHub.** Preserve a copy of `archive/` on another volume or an approved storage location before deleting, moving or re-running calculations. Both CSV indices can be rebuilt from preserved manifests by `list`; it cannot rebuild lost `.med` or `.mess` files.

The manifest records the Git revision, whether tracked files were modified at capture, the Python/platform version, input and output SHA-256 hashes, reference comparisons and a user note. The capture additionally stores a deterministic fingerprint of the relevant file contents, ignoring `__pycache__`, `.vs-code-aster`, `*.pyc` and `*.pyo`. Existing v1 archives are not rewritten. The installed Code_Aster version is **not automatically detected** in this first version; its `.mess` output is retained so it can be reviewed independently. If inputs were edited without a commit, their exact contents are still archived.

For scientific review, validate the mechanical assumptions, prestress state, eigenmodes and convergence, then explicitly update the `approved_run_ids` and status in `cases.json` through a reviewed PR. `VERIFICATION_CASES.md` remains a **human-written scientific overview**, while the registry stores structured data. There is no automatic elevation to `Verified`.

### Limitations of v1

- Local, manual, post-run capture only; no background monitoring or automatic job submissions.
- Stores the numerical `results/` content (but not editor/interpreter caches), which may consume substantial disk space.
- Does not infer mode counts from `.med` and does not compute numerical acceptance tolerances.
- The detailed index stores one row per mesh, using the smallest positive critical value from each mesh's LBA CSV; all other modes remain in the archived original CSV.
- The run-summary index displays the *finest available mesh* by actual mesh size when recorded, and otherwise by nominal size for historical archives. It is only a quick navigation view.
- To run the administrative regression tests: `python3 -m unittest discover -s registry -p 'test_*.py'`.
- A separate backup strategy is necessary to make archived runs recoverable after disk loss.

## Numerical/theoretical comparisons (Brush and Almroth 1975)

This optional, separate administrative script compares **already archived** C01/C02 runs with the discrete analytical equations from [theory/README.md](theory/README.md). It does **not** execute Code_Aster, alter student examples, or change the archived solver results.

From the `Verification` repository root:

```bash
python3 registry/compare.py --case C02   # All archived C02 runs
python3 registry/compare.py --case C01   # All archived C01 runs
python3 registry/compare.py --all        # All archived C01/C02 runs
python3 registry/compare.py --run C02-YYYYMMDDTHHMMSSZ-abcdef
```

The final line illustrates the identifier format: replace it with an existing run ID. The calculation reads the **archived per-mesh `case.json`** when available (otherwise the archived `parameters.json`), and the original LBA result CSV. It checks their SHA-256 fingerprints against the archive manifest before using their contents. No current-case parameter files are consulted.

`registry/comparisons.csv` is generated by `compare.py` but **tracked by Git as a compact, reviewed summary**. Re-running comparisons may modify this file locally; inspect its diff and commit intended updates only after review. Per-run `archive/comparisons/<run_id>/comparison.csv`, `report.md`, and `comparison.svg` (SVG only when Matplotlib is available) remain local and ignored by Git. Reports can be regenerated after changes to theoretical equations or search limits. Existing snapshots are never overwritten.

The relative differences use the **evaluated theoretical equation**, not the historical rounded constant in `cases.json`. Wave numbers refer to the theoretical search only; FE eigenmodes are not classified automatically. The finite integer bounds are configurable in `registry/theory/models.json`. None of these outputs changes the scientific review status or constitutes automatic acceptance.

Run the standard-library test suite with `python3 -m unittest discover -s registry -p 'test_*.py'`.
