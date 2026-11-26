# CodeAster-Verification

**Reproducible structural-stability benchmarks with Code_Aster**

**Scientific lead and maintainer:** Mariano P. Ameijeiras  
**Code and documentation development:** Mariano P. Ameijeiras, with assistance from ChatGPT (OpenAI).  
**Institution:** Universidad Nacional de Córdoba, Argentina.

CodeAster-Verification is a collection of **self-contained numerical benchmarks**
for the study and verification of structural stability using
[Code_Aster](https://code-aster.org/). Its purpose is to make mechanical
assumptions, finite-element models, independent reference solutions,
numerical evidence and limitations **explicit and reproducible**.

The project is intended for researchers, instructors and graduate students.
It currently provides two **linear analysis / linear buckling analysis
(LA/LBA)** benchmarks for circular cylindrical shells. Columns, plates
and additional shell problems are planned; they are not yet implemented.

## Available benchmarks

Both cases use native Code_Aster `COQUE_3D` shell modeling with
`QUAD9` elements. The comparison values below are from the **finest
mesh (M05)** in a five-mesh refinement study. The reference is the
evaluated discrete analytical prediction from Brush and Almroth (1975).

| Case | Loading | Code_Aster, M05 | Analytical reference | Difference | Review status |
| --- | --- | ---: | ---: | ---: | --- |
| [C01 — Radial pressure](Shells/C01_Radial_Pressure/README.md) | Uniform **non-follower** external radial pressure | 729.098 kPa | 730.641 kPa | −0.211% | **Benchmarked** |
| [C02 — Axial compression](Shells/C02_Axial_Compression/README.md) | Uniform axial compression | 403.303 MPa | 417.354 MPa | −3.367% | **Benchmarked** |

The full **M01–M05 convergence tables**, reference equations, run IDs
and scientific qualifications appear in
[VERIFICATION_CASES.md](VERIFICATION_CASES.md). The underlying
numerical/theoretical comparison records are included in the tracked
[registry/comparisons.csv](registry/comparisons.csv).

**Benchmarked does not mean Verified.** The numerical values show
comparisons and mesh-refinement trends, but do not establish formal
acceptance tolerances or certify Code_Aster for general use. In
particular, the theoretical minimum and the smallest positive
finite-element eigenvalue are compared without automatically asserting
that their buckling mode shapes coincide.

## Getting started

**Reference environment:** Code_Aster 18.1.8, Ubuntu 22.04.5 LTS
(WSL 2), Python 3.11.17, with Code_Aster available through a
Micromamba environment named `aster-mpi`.

For installation and environment checks, follow
[INSTALLATION.md](INSTALLATION.md). Other environments may work, but
have not been established as equivalent by this project.

Once the repository is publicly accessible, download it as a ZIP
from GitHub or clone it:

```bash
git clone https://github.com/mameije/CodeAster-Verification.git
cd CodeAster-Verification
```

With a compatible Code_Aster environment already installed, an
example run is:

```bash
micromamba activate aster-mpi
cd Shells/C01_Radial_Pressure
python3 run.py --convergence
```

For axial compression, start from the repository root and use
`cd Shells/C02_Axial_Compression` instead. Each benchmark's README
describes its loads, restraints, configuration and execution options.

**Important:** a new calculation or input preparation **clears that
case's local `results/` directory**. Preserve results before
rerunning. The `--plots-only` option regenerates figures from
existing results without invoking the solver.

## Repository structure

| Location | Content |
| --- | --- |
| [Shells/](Shells/README.md) | Available cylindrical-shell benchmarks, C01 and C02 |
| [Columns/](Columns/README.md) | Reserved for future column stability benchmarks |
| [Plates/](Plates/README.md) | Reserved for future plate stability benchmarks |
| [VERIFICATION_CASES.md](VERIFICATION_CASES.md) | Scientific references, five-mesh comparisons, evidence and review status |
| [INSTALLATION.md](INSTALLATION.md) | Installation and reference software environment |
| [registry/](registry/README.md) | Separate administrative registry, comparison tools and local run archiving |

Each implemented case retains the native Code_Aster `.comm` input
and its `parameters.json` configuration together with small Python
scripts for mesh generation, execution and output organization.
Scientific calculations use **native Code_Aster commands**; the
administrative registry does not replace the finite-element solver.

Mechanical boundary conditions and loading assumptions follow each
reference problem and are documented within the corresponding case.

## Results and reproducibility

The repository tracks **source files, scientific documentation and
the compact comparison index**. Full solver outputs, meshes,
`.med` files and archived run snapshots are generated locally and
are **not included** in GitHub. To inspect the complete numerical
output, run the cases locally. The
[verification register](VERIFICATION_CASES.md) identifies the
reference equations, individual refinement meshes and archived run IDs.

The current analytical references are from W. O. Brush and B. O.
Almroth, *Buckling of Bars, Plates, and Shells* (1975), Chapter 5.
The referenced book and third-party software are **not distributed**
as part of this repository.

## License and project stewardship

The original project code and documentation are offered under the
[MIT License](LICENSE). You may download, run, adapt and redistribute
your own copies under its terms, including retaining the required
copyright and permission notices. Code_Aster and other third-party
dependencies retain their own licenses.

The **official repository is curated by its maintainer**. External
change proposals are not being solicited at this stage; users are
welcome to maintain independent forks. Permission to modify a copy
does **not** grant write access to the official repository.

**Scientific use:** these are research and teaching benchmarks,
provided without a warranty of accuracy or fitness for a particular
engineering design. Users must independently assess model
assumptions, numerical convergence and applicable design standards.

**Documentation updated:** 26 November 2026.
