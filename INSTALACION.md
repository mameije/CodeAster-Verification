# Instalación y entorno de ejecución

**Proyecto:** [Verificación de modelos Code_Aster](README.md)  
**Responsable científico y mantenedor:** Mariano P. Ameijeiras  
**Desarrollo de código y documentación:** Mariano P. Ameijeiras, con asistencia de ChatGPT (OpenAI).  
**Institución:** Universidad Nacional de Córdoba, Argentina.  
**Última revisión:** 26 de noviembre de 2026.

Esta guía describe la organización de Windows, WSL, VS Code y el entorno
`aster-mpi`. Los procedimientos de instalación se mantienen en este documento,
separados del [índice general](README.md) y de cada caso de verificación.

## Versiones del entorno de referencia

Las siguientes versiones corresponden al entorno de trabajo registrado para
los cálculos, **no a requisitos mínimos ni a una certificación de compatibilidad**.
No se ha realizado un inventario automático actualizado de todas las versiones.

| Componente | Versión de referencia | Observaciones |
| --- | --- | --- |
| Windows | 11 | Sistema operativo anfitrión |
| WSL | 2 | Ubuntu ejecutado mediante WSL |
| Ubuntu | 22.04.5 LTS | Distribución Linux de trabajo |
| Code_Aster | 18.1.8 | Instalación en `aster-mpi` |
| Python | 3.11.17 | Versión registrada para `aster-mpi`; comprobar en cada equipo |
| Matplotlib | 3.11.2 | Versión comunicada; comprobar en el intérprete activo |
| Micromamba | Por confirmar | Gestor de entornos |
| Visual Studio Code | Por confirmar | Editor de Windows con extensión WSL |

Comprobación de versiones en la terminal **Ubuntu (WSL)**:

```bash
cat /etc/os-release
uname -r
micromamba --version
micromamba activate aster-mpi
python3 --version
which python3
which run_aster
micromamba list -n aster-mpi code-aster
python3 -c "import matplotlib; print(matplotlib.__version__)"
code --version
```

En **PowerShell de Windows**, la versión de WSL y el tipo de distribución
se comprueban mediante:

```powershell
wsl --version
wsl --list --verbose
```

---

## Procedimiento de instalación y configuración

Los ejemplos se ejecutan en Ubuntu (WSL) con Code_Aster instalado en un entorno
`micromamba` denominado `aster-mpi`. VS Code se utiliza como editor y terminal
remota de WSL. Las fuentes tipograficas de Ubuntu se administran por separado
de los paquetes de Python.

### 1. Instalacion de WSL y Ubuntu

En **PowerShell de Windows con permisos de administrador**:

```powershell
wsl --install -d Ubuntu-22.04
```

Reiniciar Windows cuando sea solicitado. Completar la configuracion inicial del
usuario de Ubuntu. Comprobar la distribucion y la version de WSL:

```powershell
wsl --list --verbose
```

La instalacion, los requisitos y los procedimientos alternativos se describen
en [Microsoft Learn: instalar WSL](https://learn.microsoft.com/es-es/windows/wsl/install).
El listado de distribuciones disponibles se obtiene con `wsl --list --online`.
Se recomienda WSL 2.

### 2. VS Code integrado con WSL

Instalar **Visual Studio Code** en Windows y la extension oficial **WSL**.
Abrir una terminal de Ubuntu, desplazarse a la carpeta del repositorio y ejecutar:

```bash
code .
```

Esto abre una ventana de VS Code conectada a WSL. Las terminales integradas y
las extensiones remotas utilizan las herramientas Linux de la distribucion.
Seleccionar el interprete Python del entorno `aster-mpi` mediante
**Python: Select Interpreter**.

Referencia: [VS Code — Developing in WSL](https://code.visualstudio.com/docs/remote/wsl).

### 3. Code_Aster y el entorno `aster-mpi`

Instalar **Micromamba** dentro de Ubuntu siguiendo su
[documentacion oficial](https://mamba.readthedocs.io/en/latest/installation/micromamba-installation.html).
Code_Aster se distribuye como paquete para Linux en
[conda-forge: code-aster](https://anaconda.org/conda-forge/code-aster),
con distintas compilaciones; para este proyecto corresponde utilizar una
**compilacion compatible con MPI**. La seleccion exacta de version y variante
debe comprobarse al crear el entorno. El nombre `aster-mpi` identifica el
entorno local; no implica por si solo que una instalacion sea paralela.

Con el entorno ya creado, la activacion y las comprobaciones basicas son:

```bash
micromamba activate aster-mpi
which python3
which run_aster
micromamba list -n aster-mpi code-aster
```

`python3` y `run_aster` deben resolverse dentro del mismo entorno.
La cantidad de procesos MPI se configura mediante `mpi_nbcpu` en
`parametros.json`; se utiliza inicialmente un proceso.

La biblioteca grafica se instala **dentro** del entorno:

```bash
micromamba install -n aster-mpi -c conda-forge matplotlib
python3 -c "import matplotlib; print(matplotlib.__version__)"
```

### 4. Tipografia Latin Modern Roman

La fuente es un recurso de Ubuntu, no de Code_Aster ni del entorno Python:

```bash
sudo apt update
sudo apt install fonts-lmodern
fc-match "Latin Modern Roman"
```

Las figuras SVG de C01 utilizan Latin Modern Roman cuando esta disponible;
de lo contrario se utiliza DejaVu Serif y se emite un aviso. El texto se
conserva editable en los SVG (la fuente no se incrusta en el archivo).

La presente seccion constituye una **referencia de instalacion**. Una guia
reproducible desde cero con versiones fijadas y verificacion del entorno MPI
podra desarrollarse por separado. La documentacion se mantiene inicialmente
en Markdown para su posterior edicion en PDF.
