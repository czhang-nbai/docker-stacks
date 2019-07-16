# jupyterlab-runall

Add a 'Run All Cells' toolbar button and context menu item.


## Prerequisites

* JupyterLab

## Installation

```bash
jupyter labextension install jupyterlab-runall
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

