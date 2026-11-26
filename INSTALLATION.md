# Installation and execution environment

**Project:** [CodeAster-Verification](README.md)  
**Scientific lead and maintainer:** Mariano P. Ameijeiras  
**Code and documentation development:** Mariano P. Ameijeiras, with assistance from ChatGPT (OpenAI).  
**Institution:** Universidad Nacional de Córdoba, Argentina.  
**Last reviewed:** 26 November 2026.

This document describes the reference environment used to develop the
Code_Aster structural stability verification examples. The exact versions
below describe a **reference setup**, not established minimum requirements
or a guarantee of compatibility with other builds.

## 1. Reference versions

| Component | Reference version | Notes |
| --- | --- | --- |
| Host operating system | Windows 11 | Main development workstation |
| Windows Subsystem for Linux | WSL 2 | Linux virtualized environment |
| Linux distribution | Ubuntu 22.04.5 LTS | Reference shell environment |
| Code_Aster | 18.1.8 | Installed through Micromamba |
| Python | 3.11.17 | Recorded version in the \`aster-mpi\` environment |
| Matplotlib | 3.11.2 (reported; verify) | Optional plotting dependency |
| Micromamba | To be confirmed | Environment manager |
| Visual Studio Code | To be confirmed | Windows editor connected to WSL |
| Shell mesh model | COQUE_3D / QUAD9 | Native Code_Aster model |

A Code_Aster version and an MPI-capable build are separate questions:
the environment name \`aster-mpi\` is not proof that a particular
installation has been built with MPI support.

## 2. Installing WSL and Ubuntu

On **Windows 11**, open an administrator PowerShell terminal and execute:

\`\`\`powershell
wsl --install -d Ubuntu-22.04
\`\`\`

Restart Windows if requested and complete the first-run Ubuntu user
configuration. Inspect the installed distribution and WSL version:

\`\`\`powershell
wsl --list --verbose
wsl --version
\`\`\`

WSL 2 is recommended. The available distributions can be inspected using
\`wsl --list --online\`.

Official reference: [Microsoft Learn — Install WSL](https://learn.microsoft.com/en-us/windows/wsl/install).

## 3. Visual Studio Code connected to WSL

Install [Visual Studio Code](https://code.visualstudio.com/) on Windows and
the official **WSL** extension. Open an Ubuntu terminal, change to the
working directory, and execute:

\`\`\`bash
code .
\`\`\`

A remote VS Code window will open in WSL. In that window, use
**Python: Select Interpreter** to select the Python executable inside
the \`aster-mpi\` environment.

Official reference: [VS Code — Developing in WSL](https://code.visualstudio.com/docs/remote/wsl).

## 4. Micromamba and Code_Aster

Install Micromamba **inside Ubuntu** following the
[official Micromamba installation guide](https://mamba.readthedocs.io/en/latest/installation/micromamba-installation.html).

Code_Aster packages for Linux are available through
[conda-forge](https://anaconda.org/conda-forge/code-aster).
Choose the variant compatible with the required MPI functionality and
record its exact build and version; the installation details can vary
between conda-forge builds. These instructions intentionally do **not**
assume that all available Code_Aster packages are MPI enabled.

With a compatible environment already created:

\`\`\`bash
micromamba activate aster-mpi
which python3
which run_aster
python3 --version
micromamba list -n aster-mpi code-aster
\`\`\`

Both \`python3\` and \`run_aster\` should refer to the intended environment.
The number of MPI processes per calculation is controlled through
\`mpi_nbcpu\` in each case's \`parameters.json\`. One MPI process is the
default for these small verification problems.

## 5. Matplotlib and Latin Modern Roman

Install Matplotlib **inside** the \`aster-mpi\` environment:

\`\`\`bash
micromamba install -n aster-mpi -c conda-forge matplotlib
python3 -c "import matplotlib; print(matplotlib.__version__)"
\`\`\`

Install the Latin Modern fonts in **Ubuntu**, not in the Python environment:

\`\`\`bash
sudo apt update
sudo apt install fonts-lmodern
fc-match "Latin Modern Roman"
\`\`\`

Latin Modern Roman is preferred in the SVG plots. If it is unavailable,
Matplotlib uses a serif fallback and reports it. SVG labels are stored as
editable text (\`svg.fonttype = 'none'\`); the font is not embedded.

## 6. Obtain and execute the repository

After the GitHub repository has been renamed and published:

\`\`\`bash
git clone https://github.com/mameije/CodeAster-Verification.git
cd CodeAster-Verification
code .
\`\`\`

For example, from the \`C01_Radial_Pressure\` directory:

\`\`\`bash
micromamba activate aster-mpi
cd C01_Radial_Pressure
python3 run.py --mesh-index 4
python3 run.py --convergence
python3 run.py --plots-only
\`\`\`

The example may also be launched with a one-time custom solver path:
\`python3 run.py --aster /path/to/run_aster --mesh-index 4\`.

Each case **clears its own \`results/\` directory** when preparing or
executing a calculation. The \`--plots-only\` option is non-destructive.

## 7. Version and environment inspection

On Ubuntu (WSL):

\`\`\`bash
cat /etc/os-release
uname -r
micromamba --version
micromamba activate aster-mpi
which python3
which run_aster
python3 --version
micromamba list -n aster-mpi code-aster
python3 -c "import matplotlib; print(matplotlib.__version__)"
code --version
\`\`\`

On Windows PowerShell:

\`\`\`powershell
wsl --version
wsl --list --verbose
\`\`\`

## 8. Updating a local clone after the repository rename

If an existing clone still uses the old name, inspect its current remote:

\`\`\`bash
git remote -v
\`\`\`

After the GitHub rename, update \`origin\` to the new URL:

\`\`\`bash
git remote set-url origin https://github.com/mameije/CodeAster-Verification.git
git remote -v
git pull
\`\`\`

If desired, rename the local working directory **only after closing VS
Code terminals using that path**; renaming the directory is independent
of the GitHub repository rename. Do not move or delete generated results
without checking whether any local data must be retained.

This installation guide is maintained in Markdown. A formatted PDF
manual may be prepared separately.
