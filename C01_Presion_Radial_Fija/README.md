# C01: LBA de cilindro bajo presión radial fija

**Responsable científico y mantenedor:** Mariano P. Ameijeiras  
**Desarrollo de código y documentación:** Mariano P. Ameijeiras, con asistencia de ChatGPT (OpenAI).  
**Institución:** Universidad Nacional de Córdoba, Argentina.  
**Entorno de referencia:** Code_Aster 18.1.8 · Python 3.11.17 · Ubuntu 22.04.5 LTS (WSL 2).  
**Documentación general:** [Instalación](../INSTALACION.md) · [Registro de verificaciones](../VERIFICACIONES.md).  
**Última revisión:** 26 de noviembre de 2026.

**Estado:** contraste favorable con Brush en presión crítica y forma modal;
convergencia de malla observada. Verificación formal pendiente de completar
la tabla cuantitativa de refinamiento y el criterio de aceptación
([registro central](../VERIFICACIONES.md)).

## Dos objetivos

1. **Verificacion**: comprobar que la secuencia LA -> matriz geometrica -> LBA reproduce el comportamiento esperado bajo presion radial uniforme, con sensibilidad de malla. La verificacion cuantitativa **no esta cerrada** hasta cotejar una solucion independiente con las mismas condiciones mecanicas.
2. **Posgrado**: ejercicio reproducible con lectura del `.comm`, variacion de geometria, material y tamano de malla mediante `parametros.json`, y ejecucion local. La lista de N mallas permite estudiar la convergencia; no se realiza un barrido de geometria.

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
- **Ambos bordes (z=0 y H):** `DX=DY=0` en todos los nodos del perimetro, giros libres.
- **Un solo nodo real del borde inferior** (`NODO_REF`, en (R,0,0)): `DZ=0` para eliminar exclusivamente la traslacion rigida axial. El resto de desplazamientos axiales permanece libre.
- No hay nodos maestros ni relaciones RBE3/RBE2. Estas condiciones son fijas en C01 y no se parametrizan.
- JSON en lugar de Excel, ejecucion secuencial local. Sin Slurm, criterios KC ni utilidades de Viento.

> **Nota mecanica:** un patron de fuerzas radiales aplicado en la geometria indeformada no es la misma formulacion que una presion hidrostatica seguidora sobre la superficie deformada. La matriz `RIGI_GEOM` emplea el estado previo de tensiones; este ejercicio no incorpora una matriz adicional de rigidez tangente de carga seguidora. La comparacion directa con formulaciones de cargas seguidoras no resulta mecanicamente equivalente.

## Parametros (archivo `parametros.json`)

| Clave | Significado |
| --- | --- |
| `D`, `H`, `t` | Diametro, altura y espesor [m] |
| `E`, `nu` | Modulo elastico [MN/m2], Poisson [-] |
| `q_ref` | Presion radial de referencia [MN/m2]; `0.001 MN/m2 = 1 kPa` |
| `n_modos` | Cantidad minima de modos LBA positivos solicitados (1 a 12) |
| `tamano_mallas_m` | Lista de **N >= 1** tamanos nominales [m]; se permiten cualquier N de valores distintos |
| `recursos` | Limites de tiempo, memoria, MPI e hilos para cada corrida individual |

### Caso de referencia de Brush y Almroth

La configuracion inicial reproduce los datos del ejemplo numerico de *Buckling of Bars, Plates, and Shells* (1975), cap. 5, apartado 5.5a, pp. 161-164:

| D | H | t | E | nu |
| ---: | ---: | ---: | ---: | ---: |
| 1.016 m | 0.508 m | 0.00508 m | 68947.57293 MN/m2 | 0.30 |

La ecuacion (5.45), bajo las hipotesis de Donnell y con los bordes simplemente apoyados, predice aproximadamente **p_cr = 106 psi = 730.84 kPa**, con **m=1** semionda longitudinal y **n=8** ondas circunferenciales. Es una referencia teorica independiente; el resultado numerico y su correspondencia modal deben analizarse separadamente.

La referencia usa las condiciones `w=w,xx=0` en ambos bordes (ec. 5.42); al considerar tambien las relaciones `u,v`, la sec. 5.5e precisa `u,x=v=0`. En el modelo FEM se imponen `w=v=0` por `DX=DY=0` y se dejan libres los giros y el movimiento axial (salvo la eliminacion del movimiento rigido). La condicion de momento flector nulo y el esfuerzo axial libre son **naturales** en la formulacion de cascaras; su equivalencia con el modelo idealizado debe comprobarse al analizar los resultados.

La presion de referencia `q_ref=0.001 MN/m2` sirve para calcular el factor de carga LBA; la carga critica es `mu_cr*q_ref`. La lista de mallas es `[0.64, 0.32, 0.16, 0.08, 0.06, 0.04, 0.03]` m, de mayor a menor tamano nominal; se admite una cantidad arbitraria N de tamanos distintos. Se conservan los comandos nativos de Aster para el calculo.

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

# Regenerar exclusivamente los dos SVG desde convergencia.csv
python3 ejecutar.py --solo-figuras
```

Si `run_aster` tiene otra ruta, se puede pasar `--aster /ruta/a/run_aster`.

**Limpieza automatica:** los comandos de preparacion o calculo eliminan por completo la carpeta `resultados/` de C01 y la vuelven a crear vacia. **Excepcion: `--solo-figuras` no limpia ni modifica resultados numericos.** Esto incluye mallas M01, M02, archivos `.med`, `.mess`, CSV y graficos previos. `--solo-preparar` tambien limpia `resultados/`. No se modifica `parametros.json`, el `.comm` original ni otros directorios del proyecto. El programa comprueba primero el rango de indices y, cuando se va a ejecutar Aster, que exista `run_aster`. Por seguridad, se rechaza una carpeta `resultados` que sea un enlace simbolico. **No ejecutar dos instancias a la vez**, ya que una podria borrar los resultados de la otra.

Cada malla seleccionada genera su carpeta `resultados/M01`, `M02`, ... con `cilindro.mail`, `caso.json`, `.comm`, `.export` y salidas. El CSV `resultados/convergencia.csv` contiene el primer factor critico positivo, la primera carga critica y la variacion respecto de la malla anterior. Cuando existen al menos dos resultados y Matplotlib esta disponible, se generan dos figuras:

- `resultados/convergencia.svg`: carga critica en funcion del tamano real maximo del elemento (`h_real_max_m`).
- `resultados/convergencia_por_elementos.svg`: carga critica en funcion del numero total de elementos QUAD9 (`elementos`).

La abscisa de la segunda figura es el numero de elementos, no el numero de nodos. Para `--indice 1` solo se genera `M01`; `--convergencia` prepara y resuelve secuencialmente las N mallas.

### Regeneracion de figuras sin recalcular

```bash
python3 ejecutar.py --solo-figuras
```

Esta opcion lee **exclusivamente** `resultados/convergencia.csv` y sobrescribe
los dos archivos SVG. No lee `parametros.json`, no borra ni reconstruye
`resultados/`, no genera mallas y **no ejecuta Code_Aster**. Requiere un
consolidado existente con al menos dos mallas y Matplotlib instalado.
No se combina con `--indice`, `--convergencia` o `--solo-preparar`.

La tipografía de las figuras es **Latin Modern Roman**, con sustitución por
DejaVu Serif si la fuente no se encuentra. Los textos de los SVG permanecen
editables (`svg.fonttype='none'`), sin incrustación de fuentes. La instalación
de WSL, VS Code, `aster-mpi`, Matplotlib y `fonts-lmodern`, así como sus
versiones de referencia, se documentan en [INSTALACION.md](../INSTALACION.md).

**No se ejecutan multiples geometrias, imperfecciones ni campanas.** Las modificaciones de parametros se realizan directamente en `parametros.json`. Cada ejecucion reinicia `resultados/`; `--convergencia` prepara y resuelve todas las mallas indicadas en la configuracion vigente.

## Comprobaciones fisicas y numericas

1. `run_aster` debe terminar sin errores, con campos LA y modos LBA visibles en `C01_LA.med` y `C01_LBA.med`.
2. Evaluar fuerzas y desplazamientos LA; la resultante global ideal de una presion uniforme en cilindro cerrado es cero, sin que ello signifique esfuerzo nulo. Para un estado de membrana alejado de los bordes, `N_theta ≈ -q_ref R` es una comprobacion preliminar; Brush considera una idealizacion de membrana del estado previo, mientras que el FEM puede presentar efectos de borde.
3. Visualizar en ParaView los modos: revisar ovalizaciones, numeros de ondas y modos proximos. **La convergencia del primer autovalor no garantiza por si sola la correspondencia modal.**
4. Revisar tiempos, nodos y carga critica conforme se refina la malla. `h_nominal` es un objetivo: la columna `h_real_max_m` indica el tamano geometrico realmente obtenido.
5. Comparar la presion critica y el patron modal con Brush (ecuacion 5.45; 106 psi, m=1, n=8). Las diferencias deben interpretarse considerando la teoria de Donnell, las condiciones de borde y la formulacion de carga. **El cierre formal de la verificación está pendiente** hasta documentar las tolerancias y la tabla completa de convergencia.

## Documentacion tecnica consultada

- [Code_Aster U4.44.01 - `FORCE_COQUE`](https://demo-docaster.simvia-app.fr/versions/v17/manuals/man_u/u4/u4.44.01/index.html): componentes globales `FX`, `FY`, `FZ` y distincion del operando normal `PRES`.
- [DocAster U4.51.03 - cargas fijas y seguidoras](https://docaster-en-codeaster-doc-4113bb35b8213385c636b94f1536856d7f617.gitlab.io/manuals/man_u/u4/u4.51.03/Chargements.html): cargas vinculadas a geometria inicial frente a cargas `SUIV`.

## Imperfecciones

**No se incorporan en C01**: LBA se resuelve sobre geometria perfecta. La imperfeccion modal puede abordarse en un ejercicio posterior (GNIA/GMNIA), con parametros explicitos y sin mezclarla con este contraste LBA.
