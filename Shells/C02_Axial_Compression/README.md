# C02 — Cylindrical shell under axial compression

**Scientific lead and maintainer:** Mariano P. Ameijeiras  
**Code and documentation development:** Mariano P. Ameijeiras, with assistance from ChatGPT (OpenAI).  
**Institution:** Universidad Nacional de Córdoba, Argentina.  
**Reference environment:** Code_Aster 18.1.8, Ubuntu 22.04.5 LTS (WSL 2), Python 3.11.17.  
**Documentation:** [Installation](../../INSTALLATION.md) · [Verification status](../../VERIFICATION_CASES.md).  
**Last reviewed:** 26 November 2026.

**Status: Benchmarked; five-mesh LA/LBA comparison available; formal verification pending explicit acceptance criteria.**

## Reference problem

**Source:** Brush and Almroth, *Buckling of Bars, Plates, and Shells* (1975),
Chapter 5, §5.5b, *Axial Compression*, pp. 167–169,
Eqs. (5.49)–(5.55) and Figs. 5.8–5.9.
End conditions are discussed in §§5.5a and 5.5e.

The idealized uniform membrane prestress is

\[
N_{x0}=-\frac{P}{2\pi R}=-\sigma_{\mathrm{ref}}t,
\qquad N_{\theta0}=N_{x\theta0}=0.
\]

For the classical Donnell model, the critical axial **compressive stress
magnitude** (Brush, Eq. 5.52) is

\[
\sigma_{\mathrm{cr}}=
\frac{Et}{R\sqrt{3(1-\nu^2)}}.
\]

The initial configuration uses the same geometry and material as C01:

| Quantity | Value |
| --- | ---: |
| Diameter \(D\) | 1.016 m |
| Length \(H\) | 0.508 m |
| Thickness \(t\) | 0.00508 m |
| Young's modulus \(E\) | 68,947.57293168 MPa |
| Poisson's ratio \(\nu\) | 0.30 |
| Reference compressive stress \(\sigma_{\mathrm{ref}}\) | 1 MPa |
| **Classical critical stress (Eq. 5.52)** | **417.290 MPa** |

The more detailed wave-number formula (Eq. 5.50), using
\(k=m\pi R/H\), \(C=Et/(1-\nu^2)\) and
\(B=Et^3/[12(1-\nu^2)]\), is

\[
\sigma_{\mathrm{cr}}(m,n)=
\frac{1}{t}\left[
\frac{(k^2+n^2)^2}{k^2}\frac{B}{R^2}
+\frac{k^2}{(k^2+n^2)^2}(1-\nu^2)C
\right].
\]

For the initial dimensions, minimization over integer longitudinal
half-wave count \(m\geq1\) and circumferential wave count \(n\geq0\)
gives a predicted value of approximately **417.354 MPa** at
\(m=3,\ n=9\). Other wave combinations, including
\(m=5,\ n=6\), have very similar critical stresses. Accordingly,
the numerical buckling modes are **not assumed to be unique**.

These reference values come from Brush's idealized analytical model,
and are now compared with completed Code_Aster numerical results.

## Numerical comparison and mesh refinement

The version-controlled [verification register](../../VERIFICATION_CASES.md)
contains **all five meshes** from archived run
`C02-20261126T155920Z-9e1d93`, compared with the evaluated
Brush Eq. (5.50) minimum of **417.354 MPa**. The finest mesh
(M05, 10,455 QUAD9) gives **403.303 MPa** (difference **−3.367%**).
M04 and M05 differ by approximately 0.037 MPa.

These are comparisons of the **minimum positive numerical eigenvalue**
and the **minimum theoretical eigenvalue**, not a one-to-one match
between buckling shapes. The \(m=3,\ n=9\) pair is the theoretical
minimizer only. Closely spaced numerical eigenvalues require separate
mode identification; no numerical mode counts are inferred from CSV data.

A second archived run ID,
`C02-20261126T161313Z-6e70da`, has the same five comparison
values and is not treated here as independent validation.

The mesh-refinement trend is documented, but agreement with the
idealized analytical theory, prebuckling field, reactions, solver
termination and explicit acceptance tolerances still require their
own scientific review.

## Finite-element model

- Complete cylindrical shell, native `COQUE_3D` with `QUAD9` elements.
- Radial and circumferential displacements are zero at both end rings:
  `DX=DY=0` on `BOTTOM_NODES` and `TOP_NODES`.
- Shell rotations and the remaining axial displacements are free.
  Only one bottom shell node (`REFERENCE_NODE`) has `DZ=0` to
  suppress rigid axial translation. No rigid diaphragm is introduced.
- Uniform axial compression is applied by native
  `AFFE_CHAR_MECA/FORCE_ARETE` to auxiliary quadratic `SEG3` end
  boundaries grouped as `BOTTOM_EDGE` and `TOP_EDGE`.
  The bottom force intensity is \(+\sigma_{\mathrm{ref}}t\) along Z;
  the top intensity is \(-\sigma_{\mathrm{ref}}t\), in MN/m.
- The two applied end forces balance globally. There is no concentrated
  nodal load at the reference node and no prescribed axial shortening.
- LA (`MECA_STATIQUE`) supplies `SIEF_ELGA`. Native
  `RIGI_MECA`, `RIGI_GEOM`, `INFO_MODE` and `CALC_MODES`
  determine positive buckling load factors \(\mu\).

The positive critical stress **magnitude** is
\(\sigma_{\mathrm{cr}}=\mu\sigma_{\mathrm{ref}}\).
The signed membrane stress is compressive, i.e.
\(\sigma_x=-\sigma_{\mathrm{cr}}\).

## Files, configuration and execution

The case is independent of C01, but uses the same file organization:

| File | Role |
| --- | --- |
| `parameters.json` | Geometry, elastic material, reference axial stress, mesh sizes and resources |
| `generate_mesh.py` | QUAD9 mesh and two SEG3 end-edge groups |
| `C02_LA_LBA.comm` | Code_Aster model, balanced line loads and native LA/LBA |
| `run.py` | Input preparation, sequential execution, convergence summary and plots |
| `write_results.py` | Administrative CSV/JSON writer |
| `results/` | Local outputs, excluded from version control |

The initial reference stress is `reference_stress_MPa=1`.
The five current nominal sizes are
`[0.15, 0.1, 0.05, 0.025, 0.0125]` m.
Shell boundary conditions are fixed in the `.comm`, not parameterized.

From this directory with `aster-mpi` active:

```bash
# Example: 0.025 m nominal mesh (fourth entry).
python3 run.py --mesh-index 4

# All meshes for convergence.
python3 run.py --convergence

# Input files only, without the solver.
python3 run.py --convergence --prepare-only

# Regenerate both figures without clearing results or running Code_Aster.
python3 run.py --plots-only
```

Preparation and analysis **clear `results/` before execution**.
The exception is `--plots-only`, which reads the existing
`results/convergence.csv` and replaces only the two SVG plots.

Numerical output includes `C02_LA_results.csv` (reference-node reaction
and nominal total axial load), `C02_LBA_results.csv` (eigenvalue and
`critical_stress_MPa`), `C02_LA.med`, `C02_LBA.med`,
`C02_metadata.json`, and the mesh-specific `.mess` file.

The consolidated `results/convergence.csv` contains the first positive
critical stress for each completed mesh. Matplotlib writes
`convergence.svg` (stress vs. actual size) and
`convergence_by_elements.svg` (stress vs. QUAD9 count) with
Latin Modern Roman typography when available.

## Further verification checks

1. Verify the QUAD9 surface and the two loaded SEG3 end boundaries.
2. Review the archived Code_Aster `.mess` files and termination messages.
3. Check equilibrium and the LA prestress field, expecting
   \(N_x\approx-\sigma_{\mathrm{ref}}t\) away from end effects.
4. Compare the positive critical stress with **417.290 MPa**
   (classical formula) and the discrete-mode prediction of
   approximately **417.354 MPa**.
5. Inspect several nearby eigenmodes and refine the mesh. Axial shell
   buckling can exhibit closely spaced eigenvalues.
6. Document acceptance tolerances and differences due to the Donnell
   approximation and boundary effects.

**Verification state: Benchmarked; five-mesh comparison completed, with formal verification closure pending.**
