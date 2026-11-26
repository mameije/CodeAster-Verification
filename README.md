# Verificación de modelos Code_Aster

**Responsable científico y mantenedor:** Mariano P. Ameijeiras  
**Desarrollo de código y documentación:** Mariano P. Ameijeiras, con asistencia de ChatGPT (OpenAI).  
**Institución:** Universidad Nacional de Córdoba, Argentina.

Colección de ejemplos autocontenidos para la **verificación de procedimientos numéricos**
y su utilización en estudios de estabilidad estructural y docencia de posgrado.
Los cálculos conservan, cuando corresponde, los comandos nativos de Code_Aster
empleados en el proyecto Viento, sin depender de dicho repositorio.

## Documentación general

- [Instalación y entorno de ejecución](INSTALACION.md): Windows 11, WSL 2,
  Ubuntu 22.04.5 LTS, VS Code y el entorno `aster-mpi` de Code_Aster 18.1.8.
  Incluye versiones de referencia y comandos para comprobarlas.
- [Registro de verificaciones](VERIFICACIONES.md): casos estudiados, referencias
  independientes, resultados contrastados y estado de cada verificación.

## Casos

| Caso | Problema | Análisis | Documentación |
| --- | --- | --- | --- |
| C01 | Cilindro bajo presión radial uniforme no seguidora | LA / LBA y convergencia de malla | [C01](C01_Presion_Radial_Fija/README.md) |
| C02 | Cilindro bajo compresión axial uniforme | LA / LBA y convergencia de malla | [C02](C02_Compresion_Axial/README.md) |

Los parámetros de cada caso se establecen en su archivo `parametros.json`.
Los resultados numéricos se generan localmente y no se incorporan al repositorio.
El alcance y estado de cada verificación se documentan en
[VERIFICACIONES.md](VERIFICACIONES.md) y en el README correspondiente.

**Última revisión de la documentación:** 26 de noviembre de 2026.
