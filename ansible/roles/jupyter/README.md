# Jupyter Role

Prepares the GPU/development server (`abzan`) to serve Jupyter notebooks: verifies the
NVIDIA drivers are live, installs the LaTeX/pandoc toolchain notebook exports need, and
opens the notebook port.

## Requirements
- `common` role (firewalld)
- NVIDIA drivers installed and `nvidia-smi` on `PATH`
- Jupyter itself is installed and run outside this role

## Variables
- `jupyter_packages` - Export dependencies (`texlive-xetex`, `texlive-fonts-recommended`, `texlive-plain-generic`, `pandoc`)
- `jupyter_permitted_ports` - firewalld ports on the `internal` zone (`8888/tcp`)
