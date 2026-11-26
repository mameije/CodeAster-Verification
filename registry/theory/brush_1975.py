"""Brush & Almroth (1975), cylindrical-shell Donnell equations (5.44, 5.50).

Independent reference calculations in MN-m-MPa; no Code_Aster imports.
An integer-mode search is *bounded*: results are not certified global minima.
"""
from __future__ import annotations

import math


def _parameters(data):
    values = [float(data[key]) for key in ("D", "H", "t", "E", "nu")]
    diameter, length, thickness, young, poisson = values
    if not all(math.isfinite(v) for v in values):
        raise ValueError("Non-finite material or geometric parameter")
    if min(diameter, length, thickness, young) <= 0 or not -1 < poisson < 0.5:
        raise ValueError("Invalid material or geometric parameter")
    if thickness >= diameter / 2:
        raise ValueError("Shell thickness must be smaller than its radius")
    return diameter / 2, length, thickness, young, poisson


def critical_value(case_id: str, params: dict, m: int, n: int) -> float:
    """Evaluate one integer wave pair; C01 in kPa, C02 in MPa.

    C01: Brush Eq. (5.44), p*a = ...; C02: Eq. (5.50), P/(2*pi*a) = ...
    The pre-buckling field and simple supports are those assumed in the book.
    """
    radius, length, thickness, young, nu = _parameters(params)
    if not isinstance(m, int) or not isinstance(n, int) or m < 1 or n < 0:
        raise ValueError("Wave counts m and n must be integers, m >= 1 and n >= 0")
    if case_id == "C01" and n < 1:
        raise ValueError("C01 radial pressure requires circumferential n >= 1")
    if case_id not in ("C01", "C02"):
        raise ValueError("Unsupported Brush reference case")
    wave = m * math.pi * radius / length
    wave_sq = wave * wave
    total = wave_sq + n * n
    membrane = young * thickness / (1 - nu * nu)
    flexural = young * thickness**3 / (12 * (1 - nu * nu))
    if case_id == "C01":
        pressure_mpa = (
            total**2 / n**2 * flexural / radius**2
            + wave_sq**2 / (n**2 * total**2) * (1 - nu**2) * membrane
        ) / radius
        return pressure_mpa * 1000  # kPa
    axial_mpa = (
        total**2 / wave_sq * flexural / radius**2
        + wave_sq / total**2 * (1 - nu**2) * membrane
    ) / thickness
    return axial_mpa


def discrete_minimum(case_id: str, params: dict, limits: dict, keep: int = 10) -> dict:
    """Bounded integer-mode scan; report bounds and close competing wave pairs."""
    mn = (int(limits["m_min"]), int(limits["m_max"]))
    nn = (int(limits["n_min"]), int(limits["n_max"]))
    if mn[0] < 1 or nn[0] < (1 if case_id == "C01" else 0):
        raise ValueError("Lower mode bound is not admissible")
    if mn[1] < mn[0] or nn[1] < nn[0] or mn[1] > 200 or nn[1] > 400:
        raise ValueError("Invalid or excessive mode search bounds")
    if not 1 <= keep <= 100:
        raise ValueError("keep must be between 1 and 100")
    modes = sorted(
        ((critical_value(case_id, params, m, n), m, n)
         for m in range(mn[0], mn[1] + 1)
         for n in range(nn[0], nn[1] + 1)),
        key=lambda item: (item[0], item[1], item[2]),
    )
    value, m, n = modes[0]
    if m == mn[1] or n == nn[1]:
        raise ValueError("Best mode is at the upper search boundary; increase limits")
    return {
        "value": value,
        "unit": "kPa" if case_id == "C01" else "MPa",
        "m": m,
        "n": n,
        "bounds": {"m_min": mn[0], "m_max": mn[1],
                   "n_min": nn[0], "n_max": nn[1]},
        "candidates": [{"value": x, "m": i, "n": j} for x, i, j in modes[:keep]],
    }
