# -*- coding: utf-8 -*-
"""Funciones administrativas de escritura; sin calculo de elementos finitos.
Adaptacion minima de escritura_resultados.py de Viento.
"""
import csv
import json

def escribir_csv(ruta, encabezado, filas):
    with ruta.open('w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh)
        w.writerow(encabezado)
        w.writerows(filas)

def escribir_json(ruta, datos):
    ruta.write_text(json.dumps(datos,indent=2),encoding='utf-8')
