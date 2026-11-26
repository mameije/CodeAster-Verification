# -*- coding: utf-8 -*-
"""Preparador y ejecutor local. Sin campanas ni integraciones con Viento.

python3 ejecutar.py --solo-preparar
python3 ejecutar.py --indice 1
python3 ejecutar.py --convergencia

Cada malla se procesa secuencialmente en una carpeta independiente.
"""
from __future__ import annotations
import argparse
import csv
import json
import math
from pathlib import Path
import shutil
import subprocess

from generar_malla import generar_malla

RAIZ = Path(__file__).resolve().parent


def configuracion():
    p = json.loads((RAIZ/'parametros.json').read_text(encoding='utf-8'))
    for k in ('D','H','t','E','q_ref'):
        if not isinstance(p[k],(int,float)) or not math.isfinite(p[k]) or p[k]<=0:
            raise ValueError(f'{k} debe ser positivo y finito')
    if not -1 < p['nu'] < .5: raise ValueError('nu fuera del rango elastico admisible')
    if p['t']>=p['D']/2: raise ValueError('C01 requiere t < R')
    if p['apoyo']!='BASE_ARTICULADA_SUP_LIBRE':
        raise ValueError('Solo se implemento BASE_ARTICULADA_SUP_LIBRE')
    if not isinstance(p['n_modos'],int) or not 1<=p['n_modos']<=12:
        raise ValueError('n_modos debe estar entre 1 y 12')
    hs = p['tamano_mallas_m']
    if not isinstance(hs,list) or not hs:
        raise ValueError('tamano_mallas_m debe ser una lista de longitud N>=1')
    for h in hs:
        if not isinstance(h,(float,int)) or not math.isfinite(h) or h<=0:
            raise ValueError('Todos los tamanos de malla deben ser positivos y finitos')
    if len(set(hs))!=len(hs):
        raise ValueError('Los tamanos de malla deben ser distintos')
    rec=p['recursos']
    if any(not isinstance(rec[k],int) or rec[k]<1 for k in
           ('ncpus','mpi_nbcpu','memory_limit_MB','time_limit_s')):
        raise ValueError('Recursos invalidos')
    return p


def preparar(i, p):
    h=p['tamano_mallas_m'][i-1]
    directorio=RAIZ/'resultados'/f'M{i:02d}'
    directorio.mkdir(parents=True,exist_ok=True)
    meta=generar_malla(directorio/'cilindro.mail',p['D'],p['H'],h)
    datos={k:p[k] for k in ('D','H','t','E','nu','q_ref','n_modos','apoyo')}
    datos['id']=f'C01_M{i:02d}'
    datos['h_nominal_m']=h
    (directorio/'caso.json').write_text(json.dumps(datos,indent=2),encoding='utf-8')
    (directorio/'malla.json').write_text(json.dumps(meta,indent=2),encoding='utf-8')
    for nombre in ('C01_LA_LBA.comm','escritura_resultados.py'):
        shutil.copy2(RAIZ/nombre,directorio/nombre)
    rec=p['recursos']
    export=(f"P time_limit {rec['time_limit_s']}\n"
            f"P memory_limit {rec['memory_limit_MB']}\n"
            f"P ncpus {rec['ncpus']}\n"
            f"P mpi_nbcpu {rec['mpi_nbcpu']}\n"
            "F comm C01_LA_LBA.comm D 1\n"
            "F mess C01_LA_LBA.mess R 6\n"
            "F rmed C01_LA.med R 80\n"
            "F rmed C01_LBA.med R 81\n")
    (directorio/'C01_LA_LBA.export').write_text(export,encoding='utf-8')
    print(f'M{i:02d} | h_nominal={h:g} m | {meta["n_elementos"]} QUAD9 | '
          f'{meta["n_nodos"]} nodos | {directorio}',flush=True)
    return directorio


def ejecutar(directorio, aster):
    exe=shutil.which(aster) or (aster if Path(aster).is_file() else None)
    if exe is None: raise FileNotFoundError(f'No se encontro {aster}. Activar entorno aster-mpi')
    log=directorio/'C01_LA_LBA.log'
    with log.open('w',encoding='utf-8') as fh:
        ret=subprocess.run([exe,'C01_LA_LBA.export'],cwd=directorio,
                           stdout=fh,stderr=subprocess.STDOUT,check=False).returncode
    if ret:
        raise RuntimeError(f'run_aster fallo (codigo {ret}). Revisar {log} y .mess')
    if not (directorio/'C01_LBA_resultados.csv').exists():
        raise RuntimeError(f'run_aster termino pero no se genero el CSV de LBA en {directorio}')
    print(f'OK: {directorio}',flush=True)


def resumen(indices, p):
    rows=[]
    for i in indices:
        carpeta=RAIZ/'resultados'/f'M{i:02d}'
        csv_path=carpeta/'C01_LBA_resultados.csv'
        if not csv_path.is_file(): continue
        with csv_path.open(newline='',encoding='utf-8') as fh:
            modos=list(csv.DictReader(fh))
        if not modos: continue
        meta=json.loads((carpeta/'malla.json').read_text(encoding='utf-8'))
        q=float(modos[0]['q_critica_MN_m2'])
        rows.append({'malla':f'M{i:02d}', 'h_nominal_m':p['tamano_mallas_m'][i-1],
                     'h_real_max_m':max(meta['h_circunferencia_m'],meta['h_altura_m']),
                     'elementos':meta['n_elementos'],'nodos':meta['n_nodos'],
                     'mu_crit':float(modos[0]['factor_critico_mu']),
                     'q_crit_MN_m2':q,'q_crit_kPa':1000*q,
                     'variacion_con_malla_previa_pct':''})
    # Respeta el orden de la lista del alumno. La diferencia se calcula contra
    # el anterior resultado de la lista, no es un estimador formal del error.
    for i in range(1,len(rows)):
        r0,r1=rows[i-1],rows[i]
        r1['variacion_con_malla_previa_pct']=100*abs(r1['q_crit_kPa']-r0['q_crit_kPa'])/abs(r1['q_crit_kPa'])
    if rows:
        out=RAIZ/'resultados'/'convergencia.csv'
        with out.open('w',newline='',encoding='utf-8') as fh:
            w=csv.DictWriter(fh,fieldnames=list(rows[0]))
            w.writeheader();w.writerows(rows)
        print(f'Resumen: {out}',flush=True)
        if len(rows)>1:
            try:
                import matplotlib
                matplotlib.use('Agg')
                import matplotlib.pyplot as plt
                fig,ax=plt.subplots()
                ax.plot([r['h_real_max_m'] for r in rows],
                        [r['q_crit_kPa'] for r in rows],'o-')
                ax.set_xlabel('Tamano real maximo del elemento (m)')
                ax.set_ylabel('Primera carga critica LBA (kPa)')
                ax.set_title('C01 - Sensibilidad de malla')
                ax.grid(True)
                fig.tight_layout()
                fig.savefig(RAIZ/'resultados'/'convergencia.svg')
                plt.close(fig)
            except ImportError:
                print('Matplotlib no disponible; se conserva el CSV')
    return rows


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    op=ap.add_mutually_exclusive_group()
    op.add_argument('--indice',type=int,default=None,help='Malla de la lista, empezando en 1')
    op.add_argument('--convergencia',action='store_true',help='Ejecutar secuencialmente las N mallas')
    ap.add_argument('--solo-preparar',action='store_true')
    ap.add_argument('--aster',default='run_aster')
    args=ap.parse_args()
    p=configuracion()
    n=len(p['tamano_mallas_m'])
    indices=list(range(1,n+1)) if args.convergencia else [args.indice or 1]
    if any(i<1 or i>n for i in indices):
        ap.error(f'Indice fuera de rango: 1..{n}')
    for i in indices:
        dir=preparar(i,p)
        if not args.solo_preparar: ejecutar(dir,args.aster)
    if not args.solo_preparar:
        resumen(indices,p)
    else:
        print('Solo preparacion: run_aster no ejecutado.',flush=True)

if __name__=='__main__': main()
