# Registro de verificaciones

**Responsable científico y mantenedor:** Mariano P. Ameijeiras  
**Desarrollo de código y documentación:** Mariano P. Ameijeiras, con asistencia de ChatGPT (OpenAI).  
**Última revisión:** 26 de noviembre de 2026.

Este registro centraliza los problemas estudiados con Code_Aster, sus referencias
independientes y la evidencia disponible. Los resultados se generan localmente;
no se conservan en Git. El detalle de cada modelo figura en su README.

## Estados de verificación

- **En preparación:** definición del problema y del modelo numérico.
- **Contrastado:** existen resultados numéricos y comparaciones con una
  referencia independiente, aunque falta completar su documentación.
- **Verificado:** condiciones, resultados, criterio de aceptación y estudio de
  convergencia documentados, con correspondencia modal cuando resulte aplicable.

El estado «Verificado» se utiliza solamente después de establecer y documentar
el alcance de la comparación; no constituye una validación general de Code_Aster.

## Casos

| Caso | Problema y análisis | Referencia independiente | Evidencia disponible | Estado |
| --- | --- | --- | --- | --- |
| [C01](C01_Presion_Radial_Fija/README.md) | Cilindro completo, presión radial no seguidora, LA/LBA, COQUE_3D/QUAD9 | Brush y Almroth (1975), cap. 5, §5.5a | Presión crítica, patrón modal y curvas de refinamiento de malla | **Contrastado** |

## C01 — Pandeo de cilindro bajo presión radial fija

**Referencia:** Brush y Almroth, *Buckling of Bars, Plates, and Shells*
(1975), capítulo 5, sección 5.5a, ecuación (5.45).

**Modelo:** cilindro perfecto, presión uniforme radial no seguidora; ambos
bordes con desplazamientos transversal y circunferencial restringidos;
desplazamiento axial bloqueado en un único nodo del borde inferior para
eliminar la traslación rígida. Elemento COQUE_3D, malla QUAD9.

| Magnitud | Valor |
| --- | ---: |
| Diámetro `D` | 1,016 m |
| Altura `H` | 0,508 m |
| Espesor `t` | 0,00508 m |
| Presión crítica de referencia (aprox.) | 730,84 kPa |
| Presión crítica Code_Aster, malla M01 (240 QUAD9) | 734,883 kPa |
| Diferencia relativa de M01 respecto de la referencia | +0,553 % |
| Modo teórico de referencia | `m=1`, `n=8` |
| Modo observado en ParaView | `m=1`, `n=8` |

**Evidencia adicional:** se obtuvieron curvas de carga crítica frente a tamaño
real de elemento y número de elementos, compatibles cualitativamente con
convergencia por refinamiento. Los valores completos de cada discretización
no se incluyen aquí porque aún no se ha incorporado una tabla de resultados
revisada a la documentación.

**Pendiente de cierre formal:** documentar el conjunto completo de mallas
ejecutadas, definir explícitamente tolerancias o criterios de aceptación y
registrar las diferencias atribuibles a la teoría de Donnell, a las condiciones
de borde y a la representación de la carga. Hasta entonces, la coincidencia de
carga crítica y modo se califica como **contraste favorable**, sin declarar una
verificación general de toda la formulación.

**Entorno de referencia:** Code_Aster 18.1.8, Ubuntu 22.04.5 LTS (WSL 2);
véase [INSTALACION.md](INSTALACION.md).

---

Los casos nuevos se incorporan a la tabla cuando exista una comparación con
una solución teórica, numérica o experimental independiente. Cada registro
debe identificar el alcance de la verificación y la evidencia que lo respalda.
