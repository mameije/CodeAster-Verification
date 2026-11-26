# -*- coding: utf-8 -*-
"""Generate a complete cylindrical QUAD9 Code_Aster mesh.

The circumferential seam shares nodes; no duplicate nodes are created.
Units: metres. This module only generates mesh geometry and groups.
"""
from __future__ import annotations

import math
from pathlib import Path


def divisions(length: float, element_size: float, minimum: int) -> int:
    """Round to an integer element count, subject to a minimum."""
    return max(minimum, int(math.floor(length / element_size + 0.5)))


def generate_mesh(destination: Path, D: float, H: float, element_size: float) -> dict:
    """Write the native Code_Aster ASCII mesh and return its mesh statistics."""
    if not all(math.isfinite(v) and v > 0 for v in (D, H, element_size)):
        raise ValueError("D, H and element_size must be positive and finite")

    R = D / 2
    circumferential_count = divisions(2 * math.pi * R, element_size, 8)
    axial_count = divisions(H, element_size, 2)
    nodes_per_ring = 2 * circumferential_count  # Quadratic QUAD9 edge nodes
    axial_intervals = 2 * axial_count

    # Wrap circumferential numbering to form a single closed surface.
    def node(i: int, j: int) -> str:
        return f"N{j * nodes_per_ring + i % nodes_per_ring + 1}"

    def write_group(file, names) -> None:
        for k in range(0, len(names), 8):
            file.write(" " + " ".join(names[k:k + 8]) + "\n")
        file.write("FINSF\n")

    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="ascii", newline="\n") as file:
        # TITRE, COOR_3D and QUAD9 are native Code_Aster mesh keywords.
        file.write("TITRE\n CYLINDER C02 QUAD9\nFINSF\nCOOR_3D\n")
        for j in range(axial_intervals + 1):
            z = H * j / axial_intervals
            for i in range(nodes_per_ring):
                theta = 2 * math.pi * i / nodes_per_ring
                file.write(
                    f"{node(i,j)} {R * math.cos(theta):.15g} "
                    f"{R * math.sin(theta):.15g} {z:.15g}\n"
                )

        file.write("FINSF\nQUAD9\n")
        for j in range(axial_count):
            b = 2 * j
            for i in range(circumferential_count):
                a = 2 * i
                connectivity = [
                    node(a,b), node(a+2,b), node(a+2,b+2), node(a,b+2),
                    node(a+1,b), node(a+2,b+1), node(a+1,b+2),
                    node(a,b+1), node(a+1,b+1),
                ]
                # Preserve the QUAD9 connectivity convention of C01.
                file.write(
                    f"Q{j*circumferential_count+i+1} "
                    + " ".join(connectivity[:4]) + "\n "
                    + " ".join(connectivity[4:]) + "\n"
                )

        # Quadratic SEG3 edges carry the two opposing axial line loads.
        file.write("FINSF\nSEG3\n")
        for prefix, j in (("BE", 0), ("TE", axial_intervals)):
            for i in range(circumferential_count):
                a = 2 * i
                file.write(
                    f"{prefix}{i+1} {node(a,j)} "
                    f"{node(a+2,j)} {node(a+1,j)}\n"
                )

        file.write("FINSF\nGROUP_MA NOM=SHELL\n")
        write_group(file, [f"Q{k}" for k in range(1, circumferential_count*axial_count+1)])
        for name, prefix in (("BOTTOM_EDGE", "BE"), ("TOP_EDGE", "TE")):
            file.write(f"GROUP_MA NOM={name}\n")
            write_group(file, [f"{prefix}{i+1}" for i in range(circumferential_count)])

        for name, j in (("BOTTOM_NODES", 0), ("TOP_NODES", axial_intervals)):
            file.write(f"GROUP_NO NOM={name}\n")
            write_group(file, [node(i,j) for i in range(nodes_per_ring)])

        # One actual shell node prevents rigid-body translation along Z.
        file.write("GROUP_NO NOM=REFERENCE_NODE\n")
        write_group(file, [node(0,0)])
        file.write("FIN\n")

    return {
        "num_elements": circumferential_count * axial_count,
        "num_nodes": nodes_per_ring * (axial_intervals + 1),
        "circumferential_elements": circumferential_count,
        "axial_elements": axial_count,
        "circumferential_size_m": 2 * math.pi * R / circumferential_count,
        "axial_size_m": H / axial_count,
        "num_edge_segments": 2 * circumferential_count,
        "orientation": "circumferential tangent x axial tangent = outward normal",
        "topology": "closed circumference with shared seam nodes",
    }
