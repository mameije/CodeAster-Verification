# Structural stability verification register

**Scientific lead and maintainer:** Mariano P. Ameijeiras  
**Code and documentation development:** Mariano P. Ameijeiras, with assistance from ChatGPT (OpenAI).  
**Institution:** Universidad Nacional de Córdoba, Argentina.  
**Last reviewed:** 26 November 2026.

This register identifies reference problems, independent analytical
benchmarks, available numerical evidence and the scope of verification.
Code_Aster results are generated locally and are not committed to Git.
The detailed mechanical assumptions of each case are recorded in its README.

## Verification status definitions

- **Prepared:** the reference and model are defined, but no solver result
  has yet been confirmed for that case.
- **Benchmarked:** one or more numerical results have been compared with an
  independent analytical, numerical or experimental reference. Further
  documentation or acceptance tests may be required.
- **Verified:** the reference solution, boundary conditions, numerical
  results, convergence and explicit acceptance criteria are documented.

The label **Verified** applies only to the stated model and conditions.
It is not a certification of Code_Aster for arbitrary structural problems.

## Case index

| Case | Mechanical problem | Independent reference | Available evidence | Status |
| --- | --- | --- | --- | --- |
| [C01](Shells/C01_Radial_Pressure/README.md) | Cylindrical shell, uniform non-follower radial pressure, LA/LBA, COQUE_3D/QUAD9 | Brush and Almroth (1975), §5.5a | Critical pressure, mode shape, mesh-refinement plots | **Benchmarked** |
| [C02](Shells/C02_Axial_Compression/README.md) | Cylindrical shell, uniform axial compression, LA/LBA, COQUE_3D/QUAD9 | Brush and Almroth (1975), §5.5b | Analytical predictions documented; numerical run pending | **Prepared** |

## C01 — Uniform non-follower radial pressure

**Source:** Brush and Almroth, *Buckling of Bars, Plates, and Shells*
(1975), Chapter 5, §5.5a.

The benchmark cylinder uses \(D=1.016\) m, \(H=0.508\) m,
\(t=0.00508\) m, \(E=68,947.57293168\) MPa and \(\nu=0.3\).

| Check | Value |
| --- | ---: |
| Brush critical pressure (approximate) | 730.84 kPa |
| Previously reported Code_Aster result, 240 QUAD9 | 734.883 kPa |
| Relative difference from Brush | +0.553% |
| Analytical circumferential wave count | \(n=8\) |
| Observed circumferential wave count | \(n=8\) |
| Analytical and observed longitudinal half-waves | \(m=1\) |

**Mesh numbering:** the 240-element mesh was designated `M01` under the
original four-mesh configuration. It corresponds to the current **0.08 m**
nominal size, designated `M04` in the seven-mesh configuration. The value
above is a historical reported result, not a new run under the new name.

Mesh-refinement plots were produced for critical pressure versus actual
element size and total QUAD9 count. The complete numerical convergence
table and quantitative acceptance thresholds still need to be included
in a reviewed verification report.

**State:** **Benchmarked**; favorable agreement in eigenvalue and mode
shape. Formal verification closure remains pending.

## C02 — Uniform axial compression

**Source:** Brush and Almroth (1975), Chapter 5, §5.5b, Eqs. (5.50) and
(5.52), Figs. 5.8 and 5.9.

For the same initial dimensions and material:

| Analytical reference | Predicted positive critical stress |
| --- | ---: |
| Classical Donnell expression (Eq. 5.52) | 417.290 MPa |
| Minimum of discrete axial and circumferential wave modes (Eq. 5.50) | Approximately 417.354 MPa, \(m=3,\ n=9\) |

Closely spaced axial-shell buckling eigenvalues are expected. The case
applies balanced non-follower line forces at both ends using the native
`FORCE_ARETE` operator and uses a single axial reference-node restraint
to eliminate rigid translation.

**State:** **Prepared**. The C02 `.comm`, Python scripts and reference
calculations have not yet been verified through an actual solver run.
Prebuckling stresses, reactions, eigenvalues, eigenmodes and mesh
convergence remain to be checked.

---

New cases should be included only with a precise independent reference
and an explicit description of their verification status. A documented
numerical agreement for one loading or support configuration does not
extend automatically to other mechanical formulations.
