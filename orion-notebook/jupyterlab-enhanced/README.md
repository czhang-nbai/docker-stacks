# JupyterLab-enhanced

This extension is intended for creating and running a script('.sh','.py' or'.sbatch') file in JupyterLab. Additionally, it supports creation of SLURM job script and python3 files that are able to run inside Jupyter Notebook.


## Prerequisites

* JupyterLab

## Installation

```bash
jupyter labextension install jupyterlab-enhanced
```

## Development

For a development install (requires npm version 4 or later), do the following in the repository directory:

```bash
npm install
npm run build
jupyter labextension install .
```

To rebuild the package and the JupyterLab app:

```bash
npm run build
jupyter lab build
```
