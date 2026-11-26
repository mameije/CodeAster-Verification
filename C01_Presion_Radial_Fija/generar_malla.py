# -*- coding: utf-8 -*-
"""Genera malla ASCII Aster QUAD9 de cilindro completo (sin costura duplicada).

Adaptacion de generar_mallas.py del proyecto Viento; sin imports del mismo.
Unidades: m. Esta rutina genera geometria, no calcula la mecanica.
"""
from __future__ import annotations
import math
from pathlib import Path


def divisiones(longitud: float, h: float, minimo: int) -> int:
    return max(minimo, int(math.floor(longitud / h + 0.5)))


def generar_malla(destino: Path, D: float, H: float, h: float) -> dict:
    if not all(math.isfinite(v) and v > 0.0 for v in (D, H, h)):
        raise ValueError("D, H y h deben ser positivos y finitos")
    R = D / 2
    nc = divisiones(2 * math.pi * R, h, 8)  # elementos circunferenciales
    nz = divisiones(H, h, 2)                # elementos longitudinales
    nt = 2 * nc                             # divisiones nodales circunferenciales QUAD9
    nh = 2 * nz

    # Una sola columna de nodos en la costura: topologia del cilindro cerrado.
    def nodo(i: int, j: int) -> str:
        return f"N{j * nt + (i % nt) + 1}"

    def grupo(f, nombres):
        for k in range(0, len(nombres), 8):
            f.write(' ' + ' '.join(nombres[k:k + 8]) + '\n')
        f.write('FINSF\n')

    destino.parent.mkdir(parents=True, exist_ok=True)
    with destino.open('w', encoding='ascii', newline='\n') as f:
        f.write('TITRE\n CILINDRO COMPLETO C01 QUAD9\nFINSF\nCOOR_3D\n')
        for j in range(nh + 1):
            z = H * j / nh
            for i in range(nt):
                phi = 2 * math.pi * i / nt
                f.write(f'{nodo(i,j)} {R * math.cos(phi):.15g} '
                        f'{R * math.sin(phi):.15g} {z:.15g}\n')
        f.write('FINSF\nQUAD9\n')
        for j in range(nz):
            b = 2 * j
            for i in range(nc):
                a = 2 * i
                nn = [nodo(a,b), nodo(a+2,b), nodo(a+2,b+2), nodo(a,b+2),
                      nodo(a+1,b), nodo(a+2,b+1), nodo(a+1,b+2),
                      nodo(a,b+1), nodo(a+1,b+1)]
                # Se conserva exactamente el orden QUAD9 de Viento.
                f.write(f'Q{j*nc+i+1} ' + ' '.join(nn[:4]) + '\n ' + ' '.join(nn[4:]) + '\n')
        f.write('FINSF\nGROUP_MA NOM=PAROI\n')
        grupo(f, [f'Q{k}' for k in range(1, nc*nz + 1)])
        for nombre, jj in [('BORDE_INF', 0), ('BORDE_SUP', nh)]:
            f.write(f'GROUP_NO NOM={nombre}\n')
            grupo(f, [nodo(i,jj) for i in range(nt)])
        # Un nodo real del perimetro inferior: elimina traslacion rigida axial.
        f.write('GROUP_NO NOM=NODO_REF\n')
        grupo(f, [nodo(0, 0)])
        f.write('FIN\n')
    return {
        'n_elementos': nc * nz, 'n_nodos': nt * (nh + 1),
        'n_circunferencia': nc, 'n_altura': nz,
        'h_circunferencia_m': 2 * math.pi * R / nc,
        'h_altura_m': H / nz,
        'orientacion': 'tangente theta x tangente z = normal radial exterior',
        'topologia': 'cerrado sin duplicar nodos de costura',
    }
