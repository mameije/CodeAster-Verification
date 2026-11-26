# Brush and Almroth (1975): theoretical references

Independent, read-only Python implementations of the integer-wave Donnell expressions for circular cylindrical shells. The code does not call or modify Code_Aster.

| Case | Reference | Printed page | Output | Mode scan |
| --- | --- | ---: | --- | --- |
| C01, non-follower radial pressure | Eq. (5.44) | 163 | kPa | m >= 1, n >= 1 |
| C02, axial compression | Eq. (5.50) | 168 | MPa | m >= 1, n >= 0 |

Definitions used in the code: a = D/2, L = H, h = t, k = m*pi*a/L, C = E*h/(1-nu^2) and B = E*h^3/[12*(1-nu^2)]. Inputs follow the existing MN-m-MPa convention. Search limits are configured centrally in `models.json`; the reported result is a **bounded discrete minimum** and the selected integers m,n are recorded.

For the default benchmark input D = 1.016 m, H = 0.508 m, t = 0.00508 m, E = 68947.57293168 MPa and nu = 0.3, the numerical implementation evaluates:

- C01 Eq. (5.44): 730.641426552 kPa, m=1, n=8. The historical 730.84 kPa in the case index is a rounded 106 psi value reported in the book; do not conflate it with the unrounded discrete formula evaluation.
- C02 Eq. (5.50): 417.354315528 MPa, m=3, n=9.

The source text is `buckling of bars plates and shells brush 1975 a4.pdf` available separately in the project. The PDF is **not** copied into this repository.

Compare archived runs via `python3 registry/compare.py --case C02`, `--case C01`, `--all` or `--run <run-id>`. The report records the equation used, bounds, theoretical wave numbers and numerical differences. Results are generated under `archive/comparisons/` and are **not committed**.

**Limits:** These are independently programmed reference expressions. The automated report is not a scientific acceptance certificate; reviewing analytical assumptions and finite-element eigenmodes remains a separate step.
