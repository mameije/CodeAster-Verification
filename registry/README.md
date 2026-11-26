# Verification registry and numerical-run archive (v1)

This **administrative** module is separate from the student benchmarks. It does not import or edit any of the `run.py`, `.comm`, `generate_mesh.py` or `parameters.json` files under `Shells/`. It uses Python's standard library and does not invoke Code_Aster.

## Sources of truth

- `registry/cases.json` (tracked in Git): scientific references and the **current scientific review state** of C01 and C02. Only reviewed changes to case status and `approved_run_ids` should be committed.
- `archive/<case>/<run_id>/manifest.json` (local, not tracked): immutable snapshot metadata and numerical results for a specific, *completed* local execution.
- `archive/<case>/<run_id>/snapshot/inputs/` and `snapshot/results/` (local, not tracked): inputs and the original solver output directory, including `.mess`, `.med`, mesh files and CSVs when produced.
- `registry/runs.csv` (local, not tracked): **rebuildable** index, one row per mesh found in each archived execution. It records case, run, critical value, reference value, signed percentage difference, unit, and mesh details.

The C01 historical value (734.883 kPa for 240 QUAD9) is listed as **historical evidence only** in `cases.json`: it is *not* presented as a run that can be restored. C02 has an analytical benchmark but no recorded Code_Aster calculation. Neither case has any approved archived runs yet.

## Commands

Run from the `Verification` repository root (no solver environment required):

```bash
python3 registry/manage.py cases
python3 registry/manage.py list
```

After a benchmark has finished running successfully, **before its next execution clears its `results/`**, archive all available mesh results, inputs and metadata:

```bash
python3 registry/manage.py capture --case C01 --note "Mesh-convergence run"
python3 registry/manage.py capture --case C02 --note "First axial-compression trial"
```

To list a subset or restore an archived run, using the run ID printed by `capture` or displayed in the index:

```bash
python3 registry/manage.py list --case C01
python3 registry/manage.py restore --run C01-YYYYMMDDTHHMMSSZ-abcdef
```

The last line is a **format example**: use a real run ID. Recovery copies the archived inputs and outputs to `archive/recovered/<run_id>/`. It **never overwrites** either the original archive or the active `Shells/C0x_.../results/` directory. If the recovery directory already exists, it stops rather than replacing it. It verifies SHA-256 hashes first and checks the recovered copy again.

Only finite, positive numerical LBA values from `C01_LBA_results.csv` or `C02_LBA_results.csv` are indexed. The script does not independently establish successful solver termination; review the archived `.mess` and execution log. The `capture` tool refuses a case with no numerical LBA CSVs (for example, a `--prepare-only` run). Each archived result is a **record**, not an automatically approved verification. Percentage differences compare the calculated critical value with the primary Brush reference; they are **not acceptance decisions** or error bounds.

## Retention, reproducibility and review

`archive/` and `registry/runs.csv` are ignored by Git. **They are not backed up or synchronized by GitHub.** Preserve a copy of `archive/` on another volume or an approved storage location before deleting, moving or re-running calculations. `runs.csv` can be rebuilt from preserved manifests by `list`; it cannot rebuild lost `.med` or `.mess` files.

The manifest records the Git revision, whether tracked files were modified at capture, the Python/platform version, input and output SHA-256 hashes, reference comparisons and a user note. The installed Code_Aster version is **not automatically detected** in this first version; its `.mess` output is retained so it can be reviewed independently. If inputs were edited without a commit, their exact contents are still archived.

For scientific review, validate the mechanical assumptions, prestress state, eigenmodes and convergence, then explicitly update the `approved_run_ids` and status in `cases.json` through a reviewed PR. `VERIFICATION_CASES.md` remains a **human-written scientific overview**, while the registry stores structured data. There is no automatic elevation to `Verified`.

### Limitations of v1

- Local, manual, post-run capture only; no background monitoring or automatic job submissions.
- Stores each completed calculation's whole `results/`, which may consume substantial disk space.
- Does not infer mode counts from `.med` and does not compute numerical acceptance tolerances.
- The index stores one summary row per mesh and uses the smallest positive critical value from the mesh's LBA CSV; all other modes remain in the archived original CSV.
- A separate backup strategy is necessary to make archived runs recoverable after disk loss.
