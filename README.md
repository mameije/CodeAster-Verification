# Verificacion de modelos Code_Aster

Ejemplos autocontenidos con dos objetivos: **verificar los procedimientos numericos** y **utilizarlos en un curso de posgrado**. No es un proyecto de investigacion ni un administrador de campanas.

- `C01_Presion_Radial_Fija/`: cilindro completo sometido a presion radial uniforme **no seguidora**, LA/LBA y sensibilidad de malla con N discretizaciones editables.

Cada ejemplo conserva los comandos nativos de Code_Aster empleados en Viento cuando corresponda, pero no depende de ese repositorio.

Los resultados se generan localmente y no se guardan en Git. El estado de validacion del calculo se indica en el README del caso.

## Entorno de trabajo: Windows, WSL, VS Code y Code_Aster

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
