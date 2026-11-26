# C01 — Cylindrical shell under uniform radial pressure

**Scientific lead and maintainer:** Mariano P. Ameijeiras  
**Code and documentation development:** Mariano P. Ameijeiras, with assistance from ChatGPT (OpenAI).  
**Institution:** Universidad Nacional de Córdoba, Argentina.  
**Reference environment:** Code_Aster 18.1.8, Ubuntu 22.04.5 LTS (WSL 2), Python 3.11.17.  
**Documentation:** [Installation](../INSTALLATION.md) · [Verification status](../VERIFICATION_CASES.md).  
**Last reviewed:** 26 November 2026.

**Status: benchmark comparison completed; formal verification pending a documented convergence table and acceptance criteria.**

## Purpose and reference

This independent case verifies the native LA/LBA workflow of Code_Aster against
the classical solution for a simply supported circular cylindrical shell under
uniform, non-follower external radial pressure.

**Source:** Brush and Almroth, *Buckling of Bars, Plates, and Shells* (1975),
Chapter 5, §5.5a, pp. 161–164, with boundary-condition discussion in §5.5e.

The model adopts the benchmark dimensions and material:

| Quantity | Value |
| --- | ---: |
| Diameter \(D\) | 1.016 m |
| Length \(H\) | 0.508 m |
| Thickness \(t\) | 0.00508 m |
| Young's modulus \(E\) | 68,947.57293168 MPa |
| Poisson's ratio \(\nu\) | 0.30 |
| Reference pressure \(p_{\mathrm{ref}}\) | 0.001 MPa = 1 kPa |

Brush's Donnell-theory benchmark gives an approximate critical pressure of
**730.84 kPa**, with **one axial half-wave (\(m=1\)) and eight circumferential
waves (\(n=8\))**.

## Mechanical formulation

- Full circular cylinder without circumferential symmetry constraints.
- Native **COQUE_3D / QUAD9** shell elements; nodes shared across the seam.
- **Boundary conditions:** \(w=v=0\) at both ends, imposed by \`DX=DY=0\`
  at \`BOTTOM_NODES\` and \`TOP_NODES\`; bending rotations are free.
  One bottom shell node in \`REFERENCE_NODE\` has \`DZ=0\` solely to remove
  rigid axial translation. No rigid diaphragms or master nodes.
- **Non-follower radial pressure:** fixed Cartesian load components
  \(f_X=-p_{\mathrm{ref}}X/R\) and \(f_Y=-p_{\mathrm{ref}}Y/R\),
  applied using native \`AFFE_CHAR_MECA_F/FORCE_COQUE\` and \`FORMULE\`.
  The load direction is not updated with the deformed shell.
- **LA:** \`MECA_STATIQUE\` provides the prestress state \`SIEF_ELGA\`.
- **LBA:** \`RIGI_MECA\`, \`RIGI_GEOM\`, \`INFO_MODE\`/Sturm and
  \`CALC_MODES\` provide buckling eigenvalues \(\mu\).
  The reported positive critical pressure is
  \(p_{\mathrm{cr}}=\mu p_{\mathrm{ref}}\).

The Donnell solution assumes an idealized membrane prestress field, whereas
the finite-element model can develop boundary bending effects. Follower-load
stiffness is not included; follower-pressure benchmark values are therefore
not automatically equivalent.

## First numerical comparison

The **0.08 m nominal mesh (240 QUAD9)** produced:

| Quantity | Result |
| --- | ---: |
| Brush critical pressure | 730.84 kPa |
| Code_Aster critical pressure | 734.883 kPa |
| Relative difference | +0.553% |
| Observed eigenmode in ParaView | \(m=1,\ n=8\) |

**Mesh numbering note:** this 240-element calculation was originally named
\`M01\` when the input list contained four mesh sizes. The present
seven-size configuration labels the **0.08 m** mesh \`M04\`. The numerical
value above is a previously reported result, not a new run of \`M04\`.

Mesh-refinement trends were also examined through two convergence plots.
The full numerical convergence table and explicit acceptance tolerances
remain to be documented; see
[VERIFICATION_CASES.md](../VERIFICATION_CASES.md).

## Files and configuration

| File | Role |
| --- | --- |
| \`parameters.json\` | Geometry, material, reference pressure, mesh sizes, mode count, resources |
| \`generate_mesh.py\` | Native Code_Aster ASCII mesh and boundary groups |
| \`C01_LA_LBA.comm\` | Native Code_Aster LA/LBA calculation |
| \`run.py\` | Case preparation, execution, CSV consolidation and plots |
| \`write_results.py\` | Minimal administrative CSV/JSON writer |
| \`results/\` | Locally generated outputs, excluded from Git |

The reference parameters use conventional \(D,H,t,E,\nu\) symbols and English
keys such as \`reference_pressure_MPa\`, \`num_modes\`, \`mesh_sizes_m\`,
and \`resources\`. End conditions are fixed to the benchmark and are **not**
configuration options.

The initial \`mesh_sizes_m\` list is
\`[0.64, 0.32, 0.16, 0.08, 0.06, 0.04, 0.03]\` (metres).
The actual size follows integer subdivisions of the circumference and height.
There are at least eight circumferential and two axial QUAD9 elements.

## Execution

From this directory in a WSL terminal with \`aster-mpi\` active:

\`\`\`bash
# Run the 0.08 m mesh (fourth entry in the current list).
python3 run.py --mesh-index 4

# Run every configured mesh sequentially.
python3 run.py --convergence

# Prepare all input files without executing Code_Aster.
python3 run.py --convergence --prepare-only

# Recreate SVG figures from existing convergence.csv; no solver.
python3 run.py --plots-only
\`\`\`

**Output cleanup:** preparation and execution delete and recreate
\`results/\`. \`--plots-only\` is non-destructive: it reads only
\`results/convergence.csv\` and replaces the two SVG files. It does not
read \`parameters.json\`, generate meshes, or execute Code_Aster.

Each mesh directory contains \`cylinder.mail\`, \`case.json\`, \`mesh.json\`,
\`C01_LA_LBA.comm\`, \`C01_LA_LBA.export\`, \`C01_LA_LBA.mess\`,
\`C01_LA.med\`, \`C01_LBA.med\`, \`C01_LA_results.csv\`,
\`C01_LBA_results.csv\`, and \`C01_metadata.json\`, as available.

The convergence report writes \`results/convergence.csv\` with the first
positive eigenvalue, critical pressure and actual element size. Matplotlib
generates:

- \`results/convergence.svg\`: pressure vs. maximum actual element size;
- \`results/convergence_by_elements.svg\`: pressure vs. QUAD9 element count.

Figures use Latin Modern Roman when installed, with editable SVG text.
See [INSTALLATION.md](../INSTALLATION.md) for WSL, Code_Aster, Matplotlib
and font setup.

## Verification checks

1. Inspect the solver \`.mess\` file, the LA reactions and the
   pre-buckling shell stress field.
2. Compare the smallest positive LBA eigenvalue with the Brush pressure.
3. Inspect the buckling eigenmodes in ParaView and count axial and
   circumferential waves.
4. Compare critical pressures for successive meshes using the numerical
   \`convergence.csv\` table and both SVG plots.
5. Specify numerical acceptance tolerances and the scope of agreement
   between Donnell theory and COQUE_3D.

**Status:** benchmark agreement is encouraging; no blanket verification
claim is made for Code_Aster or other boundary/loading formulations.
