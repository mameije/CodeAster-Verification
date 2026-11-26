# Structural stability verification register

**Scientific lead and maintainer:** Mariano P. Ameijeiras  
**Code and documentation development:** Mariano P. Ameijeiras, with assistance from ChatGPT (OpenAI).  
**Institution:** Universidad Nacional de Córdoba, Argentina.  
**Last reviewed:** 26 November 2026.

This register identifies reference problems, independent analytical
benchmarks, available numerical evidence and the scope of verification.
Full Code_Aster solver outputs are generated and archived locally, not committed to Git.
The reviewed numerical/theoretical comparison index is tracked in
`registry/comparisons.csv`. The detailed mechanical assumptions of each
case are recorded in its README.

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
| [C01](Shells/C01_Radial_Pressure/README.md) | Cylindrical shell, uniform non-follower radial pressure, LA/LBA, COQUE_3D/QUAD9 | Brush and Almroth (1975), §5.5a | Five-mesh critical-pressure comparison and historical mode observation | **Benchmarked** |
| [C02](Shells/C02_Axial_Compression/README.md) | Cylindrical shell, uniform axial compression, LA/LBA, COQUE_3D/QUAD9 | Brush and Almroth (1975), §5.5b | Five-mesh critical-stress comparison; closely spaced eigenmodes | **Benchmarked** |

## C01 — Uniform non-follower radial pressure

**Source:** Brush and Almroth, *Buckling of Bars, Plates, and Shells*
(1975), Chapter 5, §5.5a, Eq. (5.44).

The benchmark cylinder has \(D=1.016\) m, \(H=0.508\) m,
\(t=0.00508\) m, \(E=68,947.57293168\) MPa and \(\nu=0.3\).
The discrete Brush equation, evaluated for the configured geometry and
searched wave numbers, gives **730.6414266 kPa** at \(m=1,\ n=8\).
The older rounded reference of approximately 730.84 kPa is kept distinct.

**Archived comparison:** \`C01-20261126T164332Z-b9740e\`.
Each numerical value is the **smallest positive LBA eigenvalue** for
that mesh, converted to critical pressure. Differences are calculated
relative to the evaluated Brush Eq. (5.44), not the historical rounded value.

| Mesh | Nominal size (m) | QUAD9 | Code_Aster (kPa) | Brush (kPa) | Difference |
| --- | ---: | ---: | ---: | ---: | ---: |
| M01 | 0.1500 | 63 | 815.424 | 730.641 | +11.604% |
| M02 | 0.1000 | 160 | 744.616 | 730.641 | +1.913% |
| M03 | 0.0500 | 640 | 729.941 | 730.641 | −0.096% |
| M04 | 0.0250 | 2560 | 729.153 | 730.641 | −0.204% |
| M05 | 0.0125 | 10455 | 729.098 | 730.641 | −0.211% |

The finest two meshes differ by approximately 0.055 kPa in critical
pressure. This supports a mesh-refinement trend for the **numerical
critical value**; it does not establish an acceptance tolerance.

**Historical mode check:** a different, earlier 240-QUAD9 mesh with
0.08 m nominal size gave 734.883 kPa versus the approximately
730.84 kPa rounded Brush reference (+0.553%). For that earlier run,
the observed buckling mode was \(m=1,\ n=8\). It is *not* one of
the five meshes in the table, and its mode identification must not
be attributed automatically to M05.

**State:** **Benchmarked**. Numerical/analytical comparison and
mesh-refinement values are available; formal acceptance criteria and
full review of archived prestress, reactions and solver records remain
outside the scope of this summary.

## C02 — Uniform axial compression

**Source:** Brush and Almroth (1975), Chapter 5, §5.5b,
Eqs. (5.50) and (5.52), Figs. 5.8 and 5.9.

The same geometry and material are used. The classical Donnell critical
compressive-stress magnitude from Eq. (5.52) is approximately
**417.290 MPa**. Discrete minimization of Eq. (5.50) gives
**417.3543155 MPa** at theoretical wave counts \(m=3,\ n=9\).

**Archived comparison:** \`C02-20261126T155920Z-9e1d93\`.
The table compares the **smallest positive numerical LBA eigenvalue**
for each mesh with the **minimum theoretical stress** from Eq. (5.50).

| Mesh | Nominal size (m) | QUAD9 | Code_Aster (MPa) | Brush (MPa) | Difference |
| --- | ---: | ---: | ---: | ---: | ---: |
| M01 | 0.1500 | 63 | 419.913 | 417.354 | +0.613% |
| M02 | 0.1000 | 160 | 412.283 | 417.354 | −1.215% |
| M03 | 0.0500 | 640 | 403.953 | 417.354 | −3.211% |
| M04 | 0.0250 | 2560 | 403.340 | 417.354 | −3.358% |
| M05 | 0.0125 | 10455 | 403.303 | 417.354 | −3.367% |

The finest two meshes differ by approximately 0.037 MPa in critical
stress. The numerical result approaches 403.3 MPa over the last
refinements, while remaining about 3.37% below the idealized Brush
minimum. Agreement between successive meshes and agreement with an
analytical theory are **different checks**.

The \(m=3,\ n=9\) values identify the **theoretical minimizer**;
they are *not* an automatic identification of the numerical first
eigenmode. Several axial-compression buckling eigenvalues are closely
spaced. Another C02 archive, \`C02-20261126T161313Z-6e70da\`,
contains the same five numerical comparison values; it is not counted
as a second independent convergence series here.

The finite-element model uses balanced non-follower end line forces
through native \`FORCE_ARETE\` and one reference-node axial restraint
to remove rigid translation. See the [C02 model description](Shells/C02_Axial_Compression/README.md).

**State:** **Benchmarked**. Numerical results now exist, with a
five-mesh comparison. Formal acceptance criteria, complete inspection
of archived prestress/reactions and full mode classification remain
separate review tasks.

## Evidence scope and traceability

The numerical and evaluated theoretical values above come from the
version-controlled [comparison index](registry/comparisons.csv).
The full solver artifacts and manifests remain under the **local**
\`archive/\` directory, excluded from Git; a comparison row is not by
itself proof of solver termination or verification approval. Both
tables report nominal target mesh size, not measured maximum element
size. For reproducibility and detailed checks, use the associated run
IDs to locate the original archived \`.mess\`, \`.med\`, mesh and CSV files.

---

New cases should be included only with a precise independent reference
and an explicit description of their verification status. A documented
numerical agreement for one loading or support configuration does not
extend automatically to other mechanical formulations.
