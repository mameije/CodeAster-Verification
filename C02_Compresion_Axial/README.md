# C02: Pandeo de cilindro bajo compresión axial

**Responsable científico y mantenedor:** Mariano P. Ameijeiras  
**Desarrollo de código y documentación:** Mariano P. Ameijeiras, con asistencia de ChatGPT (OpenAI).  
**Institución:** Universidad Nacional de Córdoba, Argentina.  
**Entorno de referencia:** Code_Aster 18.1.8 · Python 3.11.17 · Ubuntu 22.04.5 LTS (WSL 2).  
**Documentación general:** [Instalación](../INSTALACION.md) · [Registro de verificaciones](../VERIFICACIONES.md).  
**Última revisión:** 26 de noviembre de 2026.

**Estado:** implementación preparada. **No ejecutada todavía con Code_Aster**; pendiente de confirmar cargas, tensiones previas, autovalores, formas modales y convergencia.

## Referencia teórica

Brush y Almroth, *Buckling of Bars, Plates, and Shells* (1975),
capítulo 5, sección **5.5b, Axial Compression**, páginas 167–169;
ecuaciones (5.49)–(5.55), figura 5.8 y figura 5.9.
Las condiciones de borde se relacionan también con §5.5a (ec. 5.42)
y §5.5e (p. 174).

El cilindro completo se somete a una carga axial de compresión uniformemente
distribuida en ambas circunferencias extremas. En el estado previo idealizado
de membrana:

```text
Nx0 = -P/(2*pi*R) = -sigma_ref*t
Ntheta0 = Nx_theta0 = 0
```

La solución clásica de compresión axial (Brush, ec. **5.52**) es:

```text
sigma_cr = E*t / (R * sqrt(3*(1-nu^2)))
```

donde `R=D/2`, `E` es el módulo elástico y `nu` el coeficiente de Poisson.
Para `nu=0.3`, Brush expresa esta relación como
`sigma_cr ≈ 0.605*E*t/R` (ec. 5.53).

### Valor teórico para la geometría inicial

| Parámetro | Valor |
| --- | ---: |
| Diámetro `D` | 1,016 m |
| Altura `H` | 0,508 m |
| Espesor `t` | 0,00508 m |
| Módulo elástico `E` | 68 947,57293168 MN/m² |
| Poisson `nu` | 0,30 |
| **Tensión crítica clásica, ec. (5.52)** | **417,290 MPa** |
| Carga axial total crítica correspondiente | 6,7662 MN |

Esta referencia se obtiene directamente de la ecuación (5.52), no mediante
lectura gráfica.

La ec. **(5.50)** permite un contraste más específico para los números enteros
de semiondas longitudinales `m` y ondas circunferenciales `n`:

```text
k = m*pi*R/H
C = E*t/(1-nu^2)
B = E*t^3/[12*(1-nu^2)]

sigma_cr(m,n) =
   { [(k^2+n^2)^2 / k^2] * B/R^2
     + [k^2/(k^2+n^2)^2] * (1-nu^2)*C } / t
```

Para esta geometría, al minimizar la ec. (5.50) respecto de pares enteros
positivos de `m` y no negativos de `n`, se obtiene aproximadamente:

| (m, n) | Tensión crítica de Brush, ec. (5.50) |
| --- | ---: |
| (3, 9) | **417,354 MPa** |
| (5, 6) | 417,371 MPa |
| (4, 8) | 417,990 MPa |
| (1, 7) | 418,059 MPa |

La proximidad de varios autovalores es una propiedad importante del pandeo
axial de cilindros. El primer modo calculado no tiene por qué presentar un único
par de ondas predeterminado; debe comprobarse visualmente y en relación con el
espectro numérico.

El parámetro de Batdorf de la figura 5.9 es
`Z = H^2/(R*t)*sqrt(1-nu^2) ≈ 95.394`, mayor que 2,85;
Brush indica que, para `Z>2.85`, la figura 5.9 reproduce el valor clásico
de la ec. (5.52). Las ecuaciones originales usan `a` para el radio
y `D` para la rigidez a flexión; aquí se escribe `R` para el radio
y `B` para dicha rigidez, reservando `D` para el diámetro.

**Alcance:** las soluciones de Brush derivan de la teoría de Donnell y de
un estado previo de membrana idealizado. Las condiciones de borde y los efectos
de flexión de borde del modelo COQUE_3D pueden introducir diferencias.

## Modelo numérico

- Cilindro completo, pared `QUAD9`, elemento nativo `COQUE_3D`.
- Ambos extremos: `DX=DY=0`; desplazamientos radiales y tangenciales nulos.
- Giros de borde libres; momento flector meridional no impuesto.
- Desplazamientos axiales libres, salvo `DZ=0` en un nodo del borde inferior
  (`NODO_REF`) para eliminar la traslación rígida axial.
- Carga axial **no seguidora**, uniformemente distribuida sobre las dos aristas.
  La malla incluye segmentos cuadráticos `SEG3` agrupados en
  `ARISTA_INF` y `ARISTA_SUP`.
- Carga en `AFFE_CHAR_MECA/FORCE_ARETE`, con
  `FZ=+sigma_ref*t` abajo y `FZ=-sigma_ref*t` arriba, en MN/m.
  Las dos fuerzas se equilibran. No se impone una deformación axial uniforme
  ni se concentran fuerzas sobre un nodo aislado.
- La parte mecánica LA/LBA usa los mismos operadores nativos de C01:
  `MECA_STATIQUE`, `CREA_CHAMP`, `RIGI_MECA`, `RIGI_GEOM`,
  `INFO_MODE`/Sturm y `CALC_MODES`.

La distribución lineal `FORCE_ARETE` sobre aristas de cáscaras `COQUE_3D`
está descrita en la [documentación de Code_Aster U4.44.01](https://docaster-en-codeaster-doc-4113bb35b8213385c636b94f1536856d7f617.gitlab.io/manuals/man_u/u4/u4.44.01/Chargements_de_type_Neumann_.html).

## Parámetros y unidades

Modificar exclusivamente `parametros.json` para cambiar la geometría,
el material, el valor de referencia `sigma_ref`, el número de modos o los
tamaños de las mallas. Las condiciones de borde de Brush permanecen fijas
en el archivo `.comm`.

| Clave | Definición |
| --- | --- |
| `D`, `H`, `t` | Diámetro, altura y espesor [m] |
| `E`, `nu` | Módulo elástico [MN/m²] y Poisson |
| `sigma_ref` | **Magnitud positiva** de la tensión axial compresiva de referencia [MN/m² = MPa] |
| `n_modos` | Cantidad mínima de autovalores positivos solicitados (1 a 12) |
| `tamano_mallas_m` | Lista de N tamaños nominales de elemento [m] |
| `recursos` | CPU, MPI, memoria y tiempo del cálculo |

Se adopta `sigma_ref=1 MN/m²=1 MPa`. La tensión crítica positiva calculada
por LBA es `sigma_cr=mu*sigma_ref`; no corresponde interpretar el signo
positivo como tracción. La tensión de membrana axial de compresión es
`sigma_x=-sigma_cr`.

La lista de tamaños iniciales es
`[0.64, 0.32, 0.16, 0.08, 0.06, 0.04, 0.03]` m.
Los tamaños reales se ajustan al número entero de divisiones de la geometría,
con mínimo de ocho elementos circunferenciales y dos longitudinales.

## Ejecución

Desde la carpeta `C02_Compresion_Axial/`, con `aster-mpi` activado:

```bash
# Ejecutar una sola malla
python3 ejecutar.py --indice 4

# Ejecutar secuencialmente todas las mallas
python3 ejecutar.py --convergencia

# Regenerar únicamente las dos figuras SVG sin ejecutar Code_Aster
python3 ejecutar.py --solo-figuras

# Preparar mallas y archivos de entrada sin ejecutar el solver
python3 ejecutar.py --convergencia --solo-preparar
```

**Limpieza:** todos los comandos de preparación y cálculo eliminan y recrean
`resultados/` antes de comenzar. `--solo-figuras` es la excepción:
no borra ni modifica resultados numéricos.

Salidas principales:

- `resultados/Mnn/C02_LA_resultados.csv`: comprobación de reacción axial
  en `NODO_REF` y carga total axial nominal `P_ref`.
- `resultados/Mnn/C02_LBA_resultados.csv`: factores `mu` y tensiones
  críticas `sigma_critica_MPa`.
- `resultados/Mnn/C02_LA.med` y `C02_LBA.med`: campos para ParaView.
- `resultados/convergencia.csv`: factores, tensiones críticas y
  discretización.
- `resultados/convergencia.svg`: tensión crítica frente a tamaño real
  máximo del elemento.
- `resultados/convergencia_por_elementos.svg`: tensión crítica frente a
  número total de elementos QUAD9.

Matplotlib es opcional para el cálculo; se requiere para regenerar los SVG.
La tipografía se configura en Latin Modern Roman, si está instalada.

## Comprobaciones pendientes

1. Confirmar que el `.mail` contiene una pared QUAD9 y las dos aristas SEG3.
2. Ejecutar el caso piloto; revisar `.mess`, convergencia y reacciones.
3. Comprobar `SIEF_ELGA` y la distribución axial del estado previo;
   lejos de los bordes se espera `Nx≈-sigma_ref*t`.
4. Comparar `sigma_cr` con 417,290 MPa (ec. 5.52) y 417,354 MPa
   (mínimo discreto de la ec. 5.50, para la geometría inicial).
5. Inspeccionar varios modos en ParaView y estudiar la convergencia con
   refinamiento. La proximidad de autovalores exige evaluar más de un modo.

**Estado de verificación: en preparación, sin ejecución Code_Aster confirmada.**
