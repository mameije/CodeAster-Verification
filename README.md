# CodeAster-Verification

**Scientific lead and maintainer:** Mariano P. Ameijeiras  
**Code and documentation development:** Mariano P. Ameijeiras, with assistance from ChatGPT (OpenAI).  
**Institution:** Universidad Nacional de Córdoba, Argentina.

This repository contains self-contained **Code_Aster verification benchmarks**
for structural stability problems involving columns, plates and shells.
The examples are suitable for graduate-level study and independent numerical
comparison by researchers.

The repository is designed around native Code_Aster commands, transparent
mechanical assumptions, and small, readable Python scripts for mesh
generation and execution. No external simulation campaigns or cluster
administrators are required.

**Repository:** [github.com/mameije/CodeAster-Verification](https://github.com/mameije/CodeAster-Verification)  
**Reference environment:** Code_Aster 18.1.8 · Ubuntu 22.04.5 LTS (WSL 2) · Python 3.11.17.

## For students and researchers

After the repository has been renamed and made public, it can be cloned using:

```bash
git clone https://github.com/mameije/CodeAster-Verification.git
cd CodeAster-Verification
code .
```

Each benchmark contains a reference publication, an explicitly defined
finite-element model, editable configuration in `parameters.json`, native
Code_Aster input (`.comm`), and reproducible execution instructions.

## Documentation

- [INSTALLATION.md](INSTALLATION.md): Windows 11, WSL 2, Ubuntu, VS Code,
  Micromamba and the Code_Aster MPI environment, with reference versions.
- [VERIFICATION_CASES.md](VERIFICATION_CASES.md): independent references,
  numerical comparisons, evidence and verification status.
- [Registry and archive](registry/README.md): separate administrative catalogue,
  local run index, snapshot capture and recovery (not used by student cases).

## Structural families

- [Columns](Columns/README.md): reserved for future column buckling verification cases.
- [Plates](Plates/README.md): reserved for future plate buckling verification cases.
- [Shells](Shells/README.md): cylindrical-shell verification cases, currently C01 and C02.

## Verification cases

| Case | Problem | Analysis | Status |
| --- | --- | --- | --- |
| [C01 — Radial pressure](Shells/C01_Radial_Pressure/README.md) | Circular cylindrical shell under uniform non-follower radial pressure | LA/LBA and mesh convergence | Benchmarked; formal closure pending |
| [C02 — Axial compression](Shells/C02_Axial_Compression/README.md) | Circular cylindrical shell under uniformly distributed axial compression | LA/LBA and mesh convergence | Benchmarked; formal closure pending |

Both cases use the native **COQUE_3D** shell formulation with **QUAD9**
elements. Mesh refinement is controlled by an arbitrary list of element
sizes in each case configuration.

## Organization and conventions

- All source code, file names, comments, terminal messages, CSV columns
  and documentation are written in English.
- Standard scientific symbols (\(D,H,t,E,\nu\)) and Code_Aster's native
  command syntax are retained.
- Mechanical assumptions and shell boundary conditions are fixed by the
  selected benchmark, rather than exposed as arbitrary configuration
  alternatives.
- Each case has its own `run.py`, `generate_mesh.py`, `write_results.py`,
  `parameters.json`, and native `.comm` file.
- Generated `results/` directories are excluded from Git.
- A case is marked **verified** only when the reference, boundary conditions,
  numerical evidence, convergence and acceptance criteria are documented.

**Publication note:** A software license must be selected before the
repository is released for reuse. Public visibility alone does not grant
permission to redistribute or modify the code.

**Documentation updated:** 26 November 2026.
