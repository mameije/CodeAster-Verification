# C01: LBA de cilindro bajo presion radial fija

**Estado:** prototipo preparado y verificaciones estaticas de sus archivos. **NO** ejecutado en Code_Aster; pendiente contrastar con teoria y reproducir correctamente los apoyos del benchmark.

## Dos objetivos

1. **Verificacion**: comprobar que la secuencia LA -> matriz geometrica -> LBA reproduce el comportamiento esperado bajo presion radial uniforme, con sensibilidad de malla. La verificacion cuantitativa **no esta cerrada** hasta cotejar una solucion independiente con las mismas condiciones mecanicas.
2. **Posgrado**: permitir que el alumno lea el `.comm`, cambie dimensiones, material y un tamano de malla, y ejecute el mismo caso. La lista de N mallas es optativa para estudiar la convergencia; no se realiza un barrido de geometria.

## Procedencia y fidelidad al proyecto Viento

Consultados en `mameije/Viento` (rama `main`):

- `TanqueViento_LA_LBA.comm`, blob Git `6e516aadef8d7f16bcb7eb69cc6e20d8c35d539d`.
- `generar_mallas.py`, blob Git `46cbf8b557b1c44a1dd53848126cf0dfc186ad78`.
- `escritura_resultados.py`: se conservaron unicamente las funciones de escritura usadas.

Comandos de Code_Aster conservados: `LIRE_MAILLAGE`, `AFFE_MODELE` (`COQUE_3D`), `AFFE_CARA_ELEM`, `DEFI_MATERIAU`, `AFFE_MATERIAU`, `AFFE_CHAR_MECA`, `AFFE_CHAR_MECA_F`, `MECA_STATIQUE`, `CALC_CHAMP`, `CREA_CHAMP`, `CALC_MATR_ELEM` (`RIGI_MECA`, `RIGI_GEOM`), `NUME_DDL`, `ASSE_MATRICE`, `INFO_MODE`, `CALC_MODES`, `IMPR_RESU`, `POST_RELEVE_T`.

Cambios respecto de Viento **solo por el nuevo problema mecanico**:

- Cilindro completo (0 a 2π) con elementos QUAD9, en vez de semicilindro y restricciones de simetria.
- Sin ley circunferencial de viento: presion constante `q_ref` radial hacia adentro de la *geometria original*.
- `FORCE_COQUE` en componentes **FX/FY globales** mediante `FORMULE`: `FX=-q_ref*X/R`, `FY=-q_ref*Y/R`, sin calculo de fuerza seguidora.
- Base con traslaciones `DX=DY=DZ=0`, rotaciones libres; **extremo superior libre**. Estas son condiciones de borde explicitas, no necesariamente iguales a las de un caso teorico publicado.
- JSON en lugar de Excel, ejecucion secuencial local. Sin Slurm, criterios KC ni utilidades de Viento.

> **Nota mecanica:** un patron de fuerzas radiales aplicado en la geometria indeformada no es la misma formulacion que una presion hidrostatica seguidora sobre la superficie deformada. La matriz `RIGI_GEOM` emplea el estado previo de tensiones; este ejercicio no incorpora una matriz adicional de rigidez tangente de carga seguidora. No comparar sin mas los autovalores con formulas que incluyan ese efecto.

## Parametros (archivo `parametros.json`)

| Clave | Significado |
| --- | --- |
| `D`, `H`, `t` | Diametro, altura y espesor [m] |
| `E`, `nu` | Modulo elastico [MN/m2], Poisson [-] |
| `q_ref` | Presion radial de referencia [MN/m2]; `0.001 MN/m2 = 1 kPa` |
| `n_modos` | Cantidad minima de modos LBA positivos solicitados (1 a 12) |
| `apoyo` | En esta primera version, `BASE_ARTICULADA_SUP_LIBRE` |
| `tamano_mallas_m` | Lista de **N >= 1** tamanos nominales [m]; se permiten cualquier N de valores distintos |
| `recursos` | Limites de tiempo, memoria, MPI e hilos para cada corrida individual |

Los valores proporcionados son **de ejemplo**, no calibrados contra un benchmark teorico.

## Ejecucion con WSL y el entorno de Code_Aster

Abrir una terminal en `CodeAster/Cascaras/Verificacion/C01_Presion_Radial_Fija/` y activar el entorno que contiene `run_aster`.

```bash
# Solo preparar la primera malla, SIN llamar a Aster
python3 ejecutar.py --solo-preparar

# Resolver una malla (por defecto, la primera de la lista)
python3 ejecutar.py

# Resolver la tercera malla
python3 ejecutar.py --indice 3

# Preparar todas las mallas, sin solver
python3 ejecutar.py --convergencia --solo-preparar

# Resolver secuencialmente las N mallas y comparar
python3 ejecutar.py --convergencia
```

Si `run_aster` tiene otra ruta, se puede pasar `--aster /ruta/a/run_aster`.

Cada malla genera `resultados/M01`, `M02`, ... con `cilindro.mail`, `caso.json`, `.comm`, `.export` y salidas. Las salidas de otras mallas no se sobrescriben. El CSV `resultados/convergencia.csv` contiene el primer factor critico positivo, la primera carga critica y la variacion respecto de la malla anterior; con Matplotlib, se escribe `convergencia.svg`.

**No se ejecutan multiples geometrias, imperfecciones ni campanas**. El alumno cambia un parametro del JSON y repite manualmente si quiere. Al modificar la geometria, volver a generar los casos anteriores de la carpeta `resultados` si se desean comparaciones consistentes: `--convergencia` vuelve a preparar y ejecutar todas las mallas seleccionadas.

## Comprobaciones fisicas a realizar tras la primera ejecucion

1. `run_aster` debe terminar sin errores, con campos LA y modos LBA visibles en `C01_LA.med` y `C01_LBA.med`.
2. Evaluar fuerzas y desplazamientos LA; la resultante global ideal de una presion uniforme en cilindro cerrado es cero, sin que ello signifique esfuerzo nulo. Para un estado de membrana alejado del apoyo, `N_theta ≈ -q_ref R` es una comprobacion preliminar, no una solucion exacta del cilindro con borde inferior restringido.
3. Visualizar en ParaView los modos: revisar ovalizaciones, numeros de ondas y modos proximos. **La convergencia del primer autovalor no garantiza por si sola la correspondencia modal.**
4. Revisar tiempos, nodos y carga critica conforme se refina la malla. `h_nominal` es un objetivo: la columna `h_real_max_m` indica el tamano geometrico realmente obtenido.
5. Identificar en Brush y Almroth u otra referencia verificada una solucion analitica/numerica **para la misma formulacion de carga y apoyos**. Hasta entonces: **verificacion pendiente**, no declarar el caso validado.

## Documentacion tecnica consultada

- [Code_Aster U4.44.01 - `FORCE_COQUE`](https://demo-docaster.simvia-app.fr/versions/v17/manuals/man_u/u4/u4.44.01/index.html): componentes globales `FX`, `FY`, `FZ` y distincion del operando normal `PRES`.
- [DocAster U4.51.03 - cargas fijas y seguidoras](https://docaster-en-codeaster-doc-4113bb35b8213385c636b94f1536856d7f617.gitlab.io/manuals/man_u/u4/u4.51.03/Chargements.html): cargas vinculadas a geometria inicial frente a cargas `SUIV`.

## Imperfecciones

**No se incorporan en C01**: LBA se resuelve sobre geometria perfecta. La imperfeccion modal puede abordarse en un ejercicio posterior (GNIA/GMNIA), con parametros explicitos y sin mezclarla con este contraste LBA.
